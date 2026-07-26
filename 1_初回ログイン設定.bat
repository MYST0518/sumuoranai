@echo off
chcp 65001 > NUL
title 澄 𝕏自動投稿 - 初回ログイン設定
echo ===================================================
echo   🔮 占い師 澄（すむ） SNS自動投稿システム
echo   【1. 初回ログイン設定】
echo ===================================================
echo.
echo 今からブラウザが開きます。
echo 𝕏 (Twitter) のアカウントでログインを行ってください。
echo ログインが完了したら、この画面で Enter キーを押してください。
echo.
pause

"C:\Users\myst\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0auto_post.py" --login


echo.
echo 設定が完了しました。何かキーを押すと閉じます。
pause > NUL
