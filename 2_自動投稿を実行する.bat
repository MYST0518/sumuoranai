@echo off
chcp 65001 > NUL
title 澄 𝕏自動投稿 - 実行
echo ===================================================
echo   🔮 占い師 澄（すむ） SNS自動投稿システム
echo   【2. Obsidianストックから𝕏へ自動投稿】
echo ===================================================
echo.
"C:\Users\myst\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0auto_post.py"

echo.
echo 処理が完了しました。
timeout /t 5
