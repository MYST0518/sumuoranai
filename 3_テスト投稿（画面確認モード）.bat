@echo off
chcp 65001 > NUL
title 澄 𝕏自動投稿 - テスト実行（画面表示）
echo ===================================================
echo   🔮 占い師 澄（すむ） SNS自動投稿システム
echo   【3. テスト投稿（ブラウザを表示して実行）】
echo ===================================================
echo.
"C:\Users\myst\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0auto_post.py" --visible

echo.
echo 処理が完了しました。
pause
