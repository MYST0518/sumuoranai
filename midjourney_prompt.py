import re

def convert_to_midjourney_prompt(theme_text):
    """
    Obsidianのテーマ/カード名からMidjourney用の英語呪文(Prompt)を自動生成する
    """
    # カード名・テーマのキーワード対応辞書
    card_map = {
        "星": "The Star, ethereal celestial goddess kneeling by a crystalline glowing pool under starlight, glowing eight-pointed golden star",
        "Star": "The Star, ethereal celestial goddess kneeling by a crystalline pool under starlight",
        "太陽": "The Sun, radiant golden celestial sun face beaming glowing rays over sunflowers",
        "Sun": "The Sun, radiant golden sun face beaming glowing rays",
        "愚者": "The Fool, mystical traveler standing on a cliff edge looking at the cosmos, white wolf companion",
        "Fool": "The Fool, mystical traveler on a cliff edge looking at the cosmos",
        "女帝": "The Empress, divine feminine queen seated on an ornate throne in a lush magical forest, star crown",
        "Empress": "The Empress, divine feminine queen on an ornate throne in a magical forest",
        "運命の輪": "Wheel of Fortune, mystical cosmic wheel of fate, glowing sacred geometry, nebula galaxy background",
        "Wheel": "Wheel of Fortune, mystical cosmic wheel of fate, glowing sacred geometry",
        "復縁": "Twin flames reunion, glowing mystical souls embracing in cosmic starlight, romantic fantasy art",
        "恋愛": "Ethereal romantic tarot artwork, two glowing souls under starry sky, magic roses, gold accents",
        "気持ち": "Mystical crystal ball reflecting glowing emotions, ethereal tarot card artwork, cosmic indigo",
        "相手": "Ethereal mystical mirror reflecting starlight, divine connection, magical tarot illustration"
    }

    prompt_core = None
    for kw, val in card_map.items():
        if kw in theme_text:
            prompt_core = val
            break

    if not prompt_core:
        prompt_core = f"A breathtaking fantasy tarot card art representing {theme_text}, cosmic celestial atmosphere, glowing aura"

    # Midjourney用パラメータを付与
    mj_prompt = (
        f"A breathtaking fantasy tarot card illustration of {prompt_core}, "
        f"ornate gold filigree frame, deep cosmic indigo and purple background, "
        f"vibrant glowing details, masterpiece digital painting --ar 1:1 --v 6.0"
    )
    return mj_prompt

if __name__ == "__main__":
    test_theme = "星（Star）希望と前進"
    print("Generated MJ Prompt:")
    print(convert_to_midjourney_prompt(test_theme))
