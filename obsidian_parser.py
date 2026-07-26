import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROBA3_URL = "https://roba3.com/expert/id842"

def get_stock_directory():
    """
    相対パス(クラウド/リポジトリ内)および絶対パス(ローカル)からObsidianストックフォルダを探索
    """
    candidates = [
        os.path.join(BASE_DIR, "02_SNS投稿ストック"),
        os.path.join(BASE_DIR, "05_タロット78枚デッキ保管庫"),
        os.path.join(BASE_DIR, "🔮澄（すむ）占いSNS運用", "02_SNS投稿ストック"),
        r"C:\Users\myst\.gemini\antigravity\scratch\miya\🔮澄（すむ）占いSNS運用\02_SNS投稿ストック"
    ]
    for d in candidates:
        if os.path.exists(d):
            return d
    return None

def get_next_unposted_stock():
    """
    Obsidianの投稿ストックフォルダから未投稿(#ストック)の投稿を1件取得する
    """
    stock_dir = get_stock_directory()
    if not stock_dir:
        print("Error: Stock directory not found in candidates.")
        return None

    print(f"Reading Obsidian stock from: {stock_dir}")

    for root, _, files in os.walk(stock_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "#ストック" not in content:
                continue

            # 「## 投稿ストック」セクションごとに分割
            sections = re.split(r"(?=\n##\s+投稿ストック)", content)
            for section in sections:
                if "#ストック" in section:
                    # テーマ/カード名の抽出
                    theme_match = re.search(r"-\s*\*\*カード\*\*:\s*(.+)", section) or re.search(r"-\s*\*\*テーマ\*\*:\s*(.+)", section)
                    theme = theme_match.group(1).strip() if theme_match else "占い師 澄（すむ）からのメッセージ"

                    # 投稿文の抽出 (コードブロック ```text ... ``` の中身)
                    post_text_match = re.search(r"```text\s*\n(.*?)\n```", section, re.DOTALL)
                    if post_text_match:
                        post_text = post_text_match.group(1).strip()
                    else:
                        continue

                    # URLの確認・自動挿入
                    if ROBA3_URL not in post_text:
                        post_text += f"\n\n▼ご予約・ご相談はこちら（ロバミミ公式）\n{ROBA3_URL}"

                    return {
                        "file_path": file_path,
                        "section_raw": section,
                        "theme": theme,
                        "post_text": post_text
                    }
    return None

def mark_stock_as_posted(stock_info):
    """
    投稿完了後、Obsidianノート内の #ストック を #投稿済み (日時) に書き換える
    """
    file_path = stock_info["file_path"]
    section_raw = stock_info["section_raw"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_section = section_raw.replace("#ストック", f"#投稿済み ({now_str})")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content.replace(section_raw, new_section)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Obsidian note updated -> Posted at {now_str}")

if __name__ == "__main__":
    stock = get_next_unposted_stock()
    if stock:
        print("Found Stock:")
        print("Theme:", stock["theme"])
        print("Post Text:\n", stock["post_text"])
    else:
        print("No unposted stock found.")
