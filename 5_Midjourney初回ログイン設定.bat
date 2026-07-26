@echo off
chcp 65001 > NUL
title 澄 𝕏自動投稿 - Midjourney初回ログイン設定
echo ===================================================
echo   🔮 占い師 澄（すむ） Midjourney自動連携
echo   【5. Midjourney初回ログイン設定】
echo ===================================================
echo.
echo 今からブラウザが開きます。
echo Midjourney (www.midjourney.com または Discord) にログインしてください。
echo ログインが完了したら、この画面で Enter キーを押してください。
echo.
pause

"C:\Users\myst\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0midjourney_automation.py" --login

echo.
echo Midjourneyログイン設定が完了しました。
pause > NUL
