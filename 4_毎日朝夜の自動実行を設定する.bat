@echo off
chcp 65001 > NUL
title 澄 𝕏自動投稿 - 朝夜スケジュール設定
echo ===================================================
echo   🔮 占い師 澄（すむ） SNS自動投稿システム
echo   【4. 毎日 朝08:00 と 夜21:00 の自動投稿スケジュール設定】
echo ===================================================
echo.
echo Windowsのタスクスケジューラに「毎日 朝08:00」と「毎日 夜21:00」の
echo 自動投稿タスクを登録します。
echo.
pause

schtasks /create /tn "Sumu_AutoPost_Morning" /tr "\"%~dp02_自動投稿を実行する.bat\"" /sc daily /st 08:00 /f
schtasks /create /tn "Sumu_AutoPost_Night" /tr "\"%~dp02_自動投稿を実行する.bat\"" /sc daily /st 21:00 /f

echo.
echo ===================================================
echo ✅ 設定が完了しました！
echo 毎日 08:00 と 21:00 に自動投稿が実行されます。
echo ===================================================
pause
