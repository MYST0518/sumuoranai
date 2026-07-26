import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright
from generate_card import generate_tarot_card_image
from obsidian_parser import get_next_unposted_stock, mark_stock_as_posted

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")

X_USERNAME = os.environ.get("X_USERNAME")
X_PASSWORD = os.environ.get("X_PASSWORD")

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

def login_with_credentials(page, username, password):
    """
    クラウド(GitHub Actions)用: 追加認証画面・安全確認を完全自動突破する強固なログイン
    """
    print("Logging into X via credentials on Cloud...")
    page.goto("https://x.com/i/flow/login")
    page.wait_for_timeout(4000)

    clean_user = username.replace("@", "").strip()

    # 1. ユーザー名/メールアドレスの入力
    try:
        user_input = page.wait_for_selector('input[autocomplete="username"]', timeout=20000)
        user_input.fill(clean_user)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Error on username input: {e}")

    # 2. 追加確認ステップ (電話番号やユーザー名の再確認画面) の自動突破
    try:
        unusual_input = page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
        if unusual_input:
            print("Detected extra verification step. Resolving automatically...")
            unusual_input.fill(clean_user)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Extra check handling: {e}")

    # 3. パスワードの入力
    try:
        pass_input = page.wait_for_selector('input[name="password"]', timeout=20000)
        pass_input.fill(password)
        page.keyboard.press("Enter")
        page.wait_for_timeout(6000)
    except Exception as e:
        print(f"Error on password input: {e}")

    print("Login sequence finished.")


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

    # 本文を最大75文字に安全カット
    if len(body_text) > 75:
        body_text = body_text[:72] + "..."

    # ロバミミURLとハッシュタグの固定フッター
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

    # 1. Obsidianから未投稿ストックを取得
    stock = get_next_unposted_stock()
    if not stock:
        print("No unposted stock found in Obsidian.")
        return

    print(f"[{stock['theme']}]")

    # 2. 画像の準備 (投稿テーマのカード名と画像を完全一致させる)
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

    print("Card Image Ready.")

    # 3. Playwrightで𝕏へ自動投稿
    with sync_playwright() as p:
        if X_USERNAME and X_PASSWORD:
            # クラウド環境: 新規ブラウザ起動＋ID/PWログイン
            browser = p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            login_with_credentials(page, X_USERNAME, X_PASSWORD)
        else:
            # ローカル環境: 保存されたセッションコンテキスト
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

        # 投稿ウィンドウまたは入力エリアを探す
        print("Setting text and card image...")
        page.goto("https://x.com/compose/post")
        page.wait_for_timeout(3000)

        # テキスト入力エリア (140文字以内に安全カット済みの文章)
        final_text = sanitize_and_trim_post(stock["post_text"])
        editor = page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=15000)
        editor.click()
        page.keyboard.insert_text(final_text)
        page.wait_for_timeout(1500)


        # 画像アップロード
        file_input = page.query_selector('input[data-testid="fileInput"]')
        if file_input:
            file_input.set_input_files(card_img_path)
            print("Attached image card.")
            page.wait_for_timeout(4000)

        # 「ポストする」実行 (JSダイレクトクリック + Control+Enter)
        print("Submitting post via JS & shortcut...")
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
        page.wait_for_timeout(5000)

        # 4. Obsidianのノートのタグを #投稿済み に書き換え
        mark_stock_as_posted(stock)
        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="占い師 澄 𝕏 自動投稿ツール (クラウド/ローカル対応)")
    parser.add_argument("--login", action="store_true", help="𝕏初回ログイン設定")
    parser.add_argument("--visible", action="store_true", help="ブラウザ画面を表示して動作させる")
    args = parser.parse_args()

    if args.login:
        run_login_setup()
    else:
        run_auto_post(headless=not args.visible)
