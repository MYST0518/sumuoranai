import os
import math
from PIL import Image, ImageDraw

def generate_tarot_card_image(theme_text, message_text="", output_path="card_output.png"):
    """
    本物のタロットカードサイズ(縦長 2:3 比率 : 800x1200)の可愛いパステルカードを自動生成する
    """
    width, height = 800, 1200
    image = Image.new("RGB", (width, height), "#140c1d")
    draw = ImageDraw.Draw(image)

    # 1. かわいいパステルピンク〜ラベンダーの縦長夢かわグラデーション
    for r in range(800, 0, -5):
        ratio = r / 800
        r_c = int(60 + 195 * (1 - ratio))
        g_c = int(30 + 130 * (1 - ratio))
        b_c = int(90 + 160 * (1 - ratio))
        draw.ellipse([width//2 - r, height//2 - r * 1.3, width//2 + r, height//2 + r * 1.3], fill=(r_c, g_c, b_c))

    # 2. 金色の縦長エレガントフレーム (タロットカード枠)
    draw.rectangle([25, 25, width - 25, height - 25], outline="#f3d078", width=5)
    draw.rectangle([35, 35, width - 35, height - 35], outline="#99782f", width=2)

    # 四隅のかわいいコーナーハート・星装飾
    corners = [(40, 40), (width - 40, 40), (40, height - 40), (width - 40, height - 40)]
    for cx, cy in corners:
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline="#f3d078", width=2)

    # 3. 中央の輝くパステル魔法陣と星
    cx, cy = width // 2, height // 2 - 40
    
    # 輝くオーラ
    for rad in range(220, 40, -10):
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(255, 215, 230), width=1)

    # キラキラ輝く8角星
    points = []
    for i in range(16):
        r = 160 if i % 2 == 0 else 70
        angle = i * (math.pi / 8)
        px = cx + int(r * math.cos(angle))
        py = cy + int(r * math.sin(angle))
        points.append((px, py))
    draw.polygon(points, outline="#f3d078", fill=(120, 60, 140))

    # 中央のパステルムーン・ハートアクセント
    draw.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], outline="#ffffff", width=3)
    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill="#f3d078")

    # 保存
    image.save(output_path)
    return output_path

if __name__ == "__main__":
    generate_tarot_card_image("テスト", "", "pure_vertical_cute_card.png")
    print("Vertical cute card generated successfully!")
