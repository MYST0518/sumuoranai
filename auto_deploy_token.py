import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")

def extract_and_deploy_auth_token():
    print("=" * 60)
    print("X(Twitter) Auth Token Auto Extraction & Deployment Tool")
    print("=" * 60)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        page.goto("https://x.com/home")
        page.wait_for_timeout(3000)

        if "login" in page.url:
            print("Please log in to your X account in the opened browser window...")
            page.goto("https://x.com/i/flow/login")

        print("Waiting for login session to be active...")
        auth_token = None
        for _ in range(60): # 最大2分待機
            cookies = context.cookies("https://x.com")
            for c in cookies:
                if c["name"] == "auth_token" and len(c["value"]) > 10:
                    auth_token = c["value"]
                    break
            if auth_token:
                break
            time.sleep(2)

        context.close()

    if not auth_token:
        print("Error: Could not extract auth_token.")
        return False

    print(f"Successfully extracted Auth Token: {auth_token[:10]}...")

    # auto_post.py 内のデフォルト Token として自動埋め込み
    auto_post_path = os.path.join(BASE_DIR, "auto_post.py")
    with open(auto_post_path, "r", encoding="utf-8") as f:
        code = f.read()

    old_target = 'X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "").strip()'
    new_target = f'X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "{auth_token}").strip()'

    if old_target in code:
        code = code.replace(old_target, new_target)
        with open(auto_post_path, "w", encoding="utf-8") as f:
            f.write(code)
        print("Updated auto_post.py with hardcoded fallback Auth Token!")

    # GitHub へ全自動プッシュ
    git_exe = r"C:\Users\myst\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
    subprocess.run([git_exe, "add", "."], cwd=BASE_DIR)
    subprocess.run([git_exe, "commit", "-m", "Auto deploy extracted Auth Token for fail-proof cloud post"], cwd=BASE_DIR)
    subprocess.run([git_exe, "push", "-f", "origin", "main"], cwd=BASE_DIR)

    print("=" * 60)
    print("Auth Token deployment to GitHub completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    extract_and_deploy_auth_token()
