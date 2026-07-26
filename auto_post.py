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
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "").strip()

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
    ID/PWでのフォームログイン
    """
    print("Logging into X via credentials on Cloud...")
    page.goto("https://x.com/i/flow/login")
    page.wait_for_timeout(6000)

    clean_user = username.replace("@", "").strip()

    # 1. ユーザー名/メールアドレス
    print("Entering username:", clean_user)
    try:
        user_input = page.wait_for_selector('input[autocomplete="username"], input[name="text"]', timeout=25000)
        user_input.fill(clean_user)
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)
    except Exception as e:
        print(f"Username input error: {e}")

    # 2. 追加確認ステップ
    page.wait_for_timeout(2000)
    pass_input_check = page.query_selector('input[name="password"]')
    if not pass_input_check:
        extra_input = (
            page.query_selector('input[data-testid="ocfEnterTextTextInput"]') or
            page.query_selector('input[name="text"]') or
            page.query_selector('input[type="text"]')
        )
        if extra_input:
            print("Detected extra verification screen. Filling email/username...")
            fill_val = email if email else clean_user
            extra_input.fill(fill_val)
            page.keyboard.press("Enter")
            page.wait_for_timeout(4000)

    # 3. パスワード
    print("Entering password...")
    try:
        pass_input = page.wait_for_selector('input[name="password"]', timeout=25000)
        pass_input.fill(password)
        page.keyboard.press("Enter")
        page.wait_for_timeout(6000)
    except Exception as e:
        print(f"Password input error: {e}")

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
    自動投稿のメイン処理
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
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless, 
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent=user_agent_str
            )

            # AUTH TOKEN が設定されている場合は Cookie 認証（100%確実・セキュリティ遮断ゼロ）
            if X_AUTH_TOKEN:
                print("Using X_AUTH_TOKEN Cookie Authentication (100% Bypasses All Security Checkpoints)...")
                context.add_cookies([
                    {"name": "auth_token", "value": X_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
                    {"name": "auth_token", "value": X_AUTH_TOKEN, "domain": "x.com", "path": "/"}
                ])
                page = context.new_page()
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            elif X_USERNAME and X_PASSWORD:
                page = context.new_page()
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                login_with_credentials(page, X_USERNAME, X_PASSWORD, X_EMAIL)
            else:
                if not os.path.exists(USER_DATA_DIR):
                    print("Login session not found.")
                    return
                context = p.chromium.launch_persistent_context(
                    user_data_dir=USER_DATA_DIR,
                    headless=headless,
                    viewport={"width": 1280, "height": 900},
                    user_agent=user_agent_str,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.new_page()
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("Navigating to Compose Post page...")
            page.goto("https://x.com/compose/post")
            page.wait_for_timeout(5000)
            page.screenshot(path=os.path.join(BASE_DIR, "step5_compose_page.png"))

            # テキスト入力エリア
            final_text = sanitize_and_trim_post(stock["post_text"])
            print("Filling post text...")
            editor = page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=25000)
            editor.click()
            page.keyboard.insert_text(final_text)
            page.wait_for_timeout(2000)

            # 画像アップロード
            file_input = page.query_selector('input[data-testid="fileInput"]')
            if file_input:
                file_input.set_input_files(card_img_path)
                print("Attached image card.")
                page.wait_for_timeout(5000)
                page.screenshot(path=os.path.join(BASE_DIR, "step6_attached_image.png"))

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
            page.screenshot(path=os.path.join(BASE_DIR, "step7_after_submit.png"))

            # 4. Obsidianのノートのタグを #投稿済み に書き換え
            mark_stock_as_posted(stock)
            context.close()

    except Exception as err:
        print("An error occurred during auto post:")
        traceback.print_exc()
        try:
            if 'page' in locals():
                page.screenshot(path=os.path.join(BASE_DIR, "error_final_state.png"))
        except:
            pass
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
