@echo off
chcp 65001 >nul
echo ========================================
echo   赛博算命 - 一键更新到网站
echo ========================================
echo.

cd /d E:\claudeceshi\aisuanming

:: 如果还没配置 git，先初始化
if not exist .git (
    git init
    git remote add origin https://github.com/Ljqljq-sys/saibosuanming.git
    git config user.email "ljqlucky@qq.com"
    git config user.name "Ljqljq-sys"
)

:: 提交并推送
git add index.html fortune.html
git commit -m "Update fortune page - %date% %time%"
git push -u origin main

echo.
echo ========================================
echo   更新完成！
echo   网站: https://ljqljq-sys.github.io/saibosuanming/
echo   (等1-2分钟刷新即可看到更新)
echo ========================================
pause
