import os
import sys
import time
import traceback
import argparse
from playwright.sync_api import sync_playwright
from generate_card import generate_tarot_card_image
from obsidian_parser import get_next_unposted_stock, mark_stock_as_posted

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")

X_USERNAME = os.environ.get("X_USERNAME")
X_PASSWORD = os.environ.get("X_PASSWORD")
X_EMAIL = os.environ.get("X_EMAIL", "")

def run_login_setup():
    """
    ローカル用: ブラウザを開き、ユーザーがX(Twitter)にログインしてセッションを保存する
    """
    print("=" * 60)
    print("Initial Login Setup for Sumu Auto Poster")
    print("Browser opened. Please log in to your X (Twitter) account.")
    print("When login is completed, press Enter in this console.")
    print("=" * 60)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        page.goto("https://x.com/i/flow/login")

        input("\n>>> ログインが完了したら、ここに Enter キーを押してください: ")
        context.close()
        print("Login session saved successfully.")

def login_with_credentials(page, username, password, email=""):
    """
    クラウド(GitHub Actions)用: 𝕏ログインの全パターン対応ロジック
    """
    print("Logging into X via credentials on Cloud...")
    page.goto("https://x.com/i/flow/login")
    page.wait_for_timeout(5000)

    clean_user = username.replace("@", "").strip()

    # 1. ユーザー名/メールアドレスの入力
    print("Entering username/email...")
    user_input = page.wait_for_selector('input[autocomplete="username"]', timeout=25000)
    user_input.fill(clean_user)
    page.keyboard.press("Enter")
    page.wait_for_timeout(4000)

    # 2. 追加確認ステップ (電話番号やメールアドレス・ユーザー名の再入力要求)
    extra_input = page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
    if extra_input:
        print("Detected extra verification step (email/phone/username request)...")
        fill_val = email if email else clean_user
        extra_input.fill(fill_val)
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)

    # 3. パスワードの入力
    print("Entering password...")
    pass_input = page.wait_for_selector('input[name="password"]', timeout=25000)
    pass_input.fill(password)
    page.keyboard.press("Enter")
    page.wait_for_timeout(6000)

    print("Login sequence finished. Current URL:", page.url)

def sanitize_and_trim_post(text):
    """
    𝕏の140文字制限に絶対収まるように本文を厳格にトリミング調整する
    """
    lines = text.strip().split("\n")
    body_parts = []
    footer_parts = []

    for line in lines:
        if "roba3.com" in line or "#" in line or "▼" in line:
            footer_parts.append(line)
        else:
            body_parts.append(line)

    body_text = "\n".join(body_parts).strip()

    if len(body_text) > 75:
        body_text = body_text[:72] + "..."

    footer_text = (
        "▼ロバミミでの個別の鑑定ご予約はこちら🔮\n"
        "https://roba3.com/expert/id842\n"
        "#今日の占い #タロット #占い師澄 #ロバミミ"
    )

    return f"{body_text}\n\n{footer_text}"

def run_auto_post(headless=True):
    """
    自動投稿のメイン処理 (ローカル / クラウド共通)
    """
    print("=" * 60)
    print("Starting Sumu Auto Post Process...")
    print("=" * 60)

    try:
        # 1. Obsidianから未投稿ストックを取得
        stock = get_next_unposted_stock()
        if not stock:
            print("No unposted stock found in Obsidian.")
            return

        print(f"Stock Found: [{stock['theme']}]")

        # 2. 画像の準備
        mj_custom_dir = os.path.join(BASE_DIR, "my_midjourney_images")
        card_img_path = None
        theme_lower = stock["theme"].lower()

        if os.path.exists(mj_custom_dir):
            custom_files = [os.path.join(mj_custom_dir, f) for f in os.listdir(mj_custom_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            keywords = {
                "愚者": "fool", "fool": "fool",
                "太陽": "sun", "sun": "sun",
                "星": "star", "star": "star",
                "女帝": "empress", "empress": "empress",
                "恋人": "lovers", "lovers": "lovers",
                "運命": "wheel", "wheel": "wheel"
            }
            target_kw = None
            for k, v in keywords.items():
                if k in theme_lower:
                    target_kw = v
                    break

            if target_kw:
                for fpath in custom_files:
                    if target_kw in os.path.basename(fpath).lower():
                        card_img_path = fpath
                        print(f"Matched Card Image: {card_img_path}")
                        break

            if not card_img_path and custom_files:
                card_img_path = custom_files[0]

        if not card_img_path or not os.path.exists(card_img_path):
            card_img_path = os.path.join(BASE_DIR, "temp_card_post.png")
            generate_tarot_card_image(stock["theme"], stock["post_text"], card_img_path)

        print("Card Image Ready:", card_img_path)

        # 3. Playwrightで𝕏へ自動投稿
        with sync_playwright() as p:
            if X_USERNAME and X_PASSWORD:
                browser = p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                login_with_credentials(page, X_USERNAME, X_PASSWORD, X_EMAIL)
            else:
                if not os.path.exists(USER_DATA_DIR):
                    print("Login session not found. Please run 1_初回ログイン設定.bat first.")
                    return
                context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=headless,
                    viewport={"width": 1280, "height": 900},
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.new_page()
                page.goto("https://x.com/home")
                page.wait_for_timeout(4000)

            print("Navigating to Compose Post page...")
            page.goto("https://x.com/compose/post")
            page.wait_for_timeout(4000)

            # テキスト入力エリア
            final_text = sanitize_and_trim_post(stock["post_text"])
            print("Filling post text...")
            editor = page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=20000)
            editor.click()
            page.keyboard.insert_text(final_text)
            page.wait_for_timeout(2000)

            # 画像アップロード
            file_input = page.query_selector('input[data-testid="fileInput"]')
            if file_input:
                file_input.set_input_files(card_img_path)
                print("Attached image card.")
                page.wait_for_timeout(5000)

            # 「ポストする」ボタンクリック
            print("Submitting post...")
            page.evaluate("""() => {
                const btn = document.querySelector('button[data-testid="tweetButtonInline"]') || 
                            document.querySelector('button[data-testid="tweetButton"]');
                if (btn) {
                    btn.disabled = false;
                    btn.click();
                }
            }""")
            page.wait_for_timeout(1000)
            page.keyboard.press("Control+Enter")

            print("Post execution completed!")
            page.wait_for_timeout(6000)

            # 4. Obsidianのノートのタグを #投稿済み に書き換え
            mark_stock_as_posted(stock)
            context.close()

    except Exception as err:
        print("An error occurred during auto post:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="占い師 澄 𝕏 自動投稿ツール")
    parser.add_argument("--login", action="store_true", help="𝕏初回ログイン設定")
    parser.add_argument("--visible", action="store_true", help="ブラウザ画面を表示して動作させる")
    args = parser.parse_args()

    if args.login:
        run_login_setup()
    else:
        run_auto_post(headless=not args.visible)
