import os
import math
from PIL import Image, ImageDraw

OUTPUT_DIR = r"C:\Users\myst\.gemini\antigravity\scratch\sumu-auto-poster\images\tarot_78"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 全78枚のタロットカード定義
MAJOR_ARCANA = [
    ("00_Fool", "愚者", (80, 50, 150), (212, 175, 55)),
    ("01_Magician", "魔術師", (120, 30, 90), (255, 215, 0)),
    ("02_HighPriestess", "女教皇", (20, 60, 120), (200, 220, 255)),
    ("03_Empress", "女帝", (140, 40, 100), (255, 182, 193)),
    ("04_Emperor", "皇帝", (150, 20, 30), (218, 165, 32)),
    ("05_Hierophant", "法王", (70, 30, 110), (238, 232, 170)),
    ("06_Lovers", "恋人", (160, 50, 120), (255, 192, 203)),
    ("07_Chariot", "戦車", (30, 80, 120), (192, 192, 192)),
    ("08_Strength", "力", (170, 90, 30), (255, 215, 0)),
    ("09_Hermit", "隠者", (40, 40, 60), (220, 220, 220)),
    ("10_WheelOfFortune", "運命の輪", (90, 40, 130), (212, 175, 55)),
    ("11_Justice", "正義", (30, 90, 90), (218, 165, 32)),
    ("12_HangedMan", "吊るされた男", (50, 70, 110), (175, 238, 238)),
    ("13_Death", "死神", (20, 20, 30), (180, 180, 180)),
    ("14_Temperance", "節制", (40, 100, 110), (255, 228, 196)),
    ("15_Devil", "悪魔", (80, 20, 40), (205, 92, 92)),
    ("16_Tower", "塔", (130, 30, 30), (255, 140, 0)),
    ("17_Star", "星", (30, 40, 110), (255, 255, 220)),
    ("18_Moon", "月", (30, 50, 90), (230, 230, 250)),
    ("19_Sun", "太陽", (180, 110, 20), (255, 215, 0)),
    ("20_Judgement", "審判", (80, 60, 130), (240, 240, 255)),
    ("21_World", "世界", (40, 120, 100), (212, 175, 55))
]

SUITS = [
    ("Wands", "ワンド", (150, 70, 20)),
    ("Cups", "カップ", (30, 80, 140)),
    ("Swords", "ソード", (60, 70, 90)),
    ("Pentacles", "ペンタクル", (130, 110, 30))
]

NUMBERS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]

def generate_card_art(file_name, name_ja, bg_rgb, border_rgb):
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), "#0a0814")
    draw = ImageDraw.Draw(img)

    # 1. 幻想的な放射グラデーション背景
    for r in range(750, 0, -6):
        ratio = r / 750
        r_c = int(bg_rgb[0] * (1 - ratio * 0.7))
        g_c = int(bg_rgb[1] * (1 - ratio * 0.7))
        b_c = int(bg_rgb[2] * (1 - ratio * 0.7))
        draw.ellipse([width//2 - r, height//2 - r, width//2 + r, height//2 + r], fill=(r_c, g_c, b_c))

    # 2. 金色のグラフィックカードフレーム
    draw.rectangle([35, 35, width - 35, height - 35], outline=border_rgb, width=6)
    draw.rectangle([50, 50, width - 50, height - 50], outline=(border_rgb[0]//2, border_rgb[1]//2, border_rgb[2]//2), width=2)

    # 3. 神聖幾何学・魔法陣の中央シンボル
    cx, cy = width // 2, height // 2
    for rad in range(260, 60, -20):
        c_val = (int(border_rgb[0] * rad / 260), int(border_rgb[1] * rad / 260), int(border_rgb[2] * rad / 260))
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=c_val, width=2)

    # 12角星 / 神聖ジオメトリの放射線
    for i in range(24):
        angle = i * (math.pi / 12)
        r_outer = 240 if i % 2 == 0 else 140
        x_end = cx + int(r_outer * math.cos(angle))
        y_end = cy + int(r_outer * math.sin(angle))
        draw.line([(cx, cy), (x_end, y_end)], fill=border_rgb, width=2)

    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=border_rgb, width=4)
    draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=border_rgb)

    save_path = os.path.join(OUTPUT_DIR, f"{file_name}.png")
    img.save(save_path)
    return save_path

# 全78枚の画像を生成
generated_count = 0

# 大アルカナ 22枚
for code, name, bg, border in MAJOR_ARCANA:
    generate_card_art(f"Major_{code}", name, bg, border)
    generated_count += 1

# 小アルカナ 56枚
for s_code, s_name, s_bg in SUITS:
    for idx, num in enumerate(NUMBERS):
        file_id = f"Minor_{s_code}_{idx+1:02d}_{num}"
        name_full = f"{s_name}の{num}"
        border_c = (212, 175, 55) if idx >= 10 else (180, 160, 100)
        generate_card_art(file_id, name_full, s_bg, border_c)
        generated_count += 1

print(f"Successfully generated {generated_count} Tarot Cards in {OUTPUT_DIR}!")
