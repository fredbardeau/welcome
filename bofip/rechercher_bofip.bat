@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py bofip_recherche.py %*
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python n'est pas installe sur ce poste : voir LISEZMOI.md.
    ) else (
        python bofip_recherche.py %*
    )
)
pause
