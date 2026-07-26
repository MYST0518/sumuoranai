import os
import sys
import time
import requests
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MJ_USER_DATA_DIR = os.path.join(BASE_DIR, "user_data_midjourney")

def run_midjourney_login():
    """
    初回設定: ブラウザを開き、ユーザーがMidjourney(www.midjourney.com または Discord)にログインする
    """
    print("=" * 60)
    print("Initial Login Setup for Midjourney Integration")
    print("Browser opened. Please log in to Midjourney (www.midjourney.com / Discord).")
    print("When login is completed, press Enter in this console.")
    print("=" * 60)


    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=MJ_USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        page.goto("https://www.midjourney.com/explore")

        input("\n>>> Midjourneyへのログインが完了したら、ここに Enter キーを押してください: ")
        context.close()
        print("✅ Midjourneyのログイン情報が保存されました！次回から自動生成が可能になります。")

def generate_via_midjourney(prompt_text, output_image_path="midjourney_card.png"):
    """
    Midjourneyを使って画像を自動生成・ダウンロードする関数
    """
    print(f"Starting Midjourney Auto Generation: {prompt_text[:50]}...")

    if not os.path.exists(MJ_USER_DATA_DIR):
        print("Midjourney login session not found. Please run initial Midjourney login first.")
        return None

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=MJ_USER_DATA_DIR,
                headless=False,  # Midjourney生成の様子を表示
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.new_page()
            page.goto("https://www.midjourney.com/create")
            page.wait_for_timeout(4000)

            # 入力プロンプトフォームを探す
            input_box = page.query_selector('textarea') or page.query_selector('input[type="text"]')
            if input_box:
                input_box.click()
                page.keyboard.insert_text(prompt_text)
                page.keyboard.press("Enter")
                print("Submitted prompt to Midjourney. Waiting ~40s for image generation...")
                page.wait_for_timeout(45000)

                # 生成された画像エレメントを取得
                img_elem = page.query_selector('img[src*="cdn.midjourney.com"]') or page.query_selector('img[src*="midjourney"]')
                if img_elem:
                    img_url = img_elem.get_attribute("src")
                    if img_url:
                        response = requests.get(img_url, timeout=15)
                        if response.status_code == 200:
                            with open(output_image_path, "wb") as f:
                                f.write(response.content)
                            print(f"Successfully saved Midjourney generated image: {output_image_path}")
                            context.close()
                            return output_image_path

            context.close()
    except Exception as e:
        print(f"Exception during Midjourney generation: {e}")

    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        run_midjourney_login()
    else:
        test_prompt = "A breathtaking fantasy tarot card art of The Star, cosmic purple background --ar 1:1"
        generate_via_midjourney(test_prompt, "test_mj_out.png")
