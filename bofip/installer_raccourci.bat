@echo off
rem Cree le raccourci "Recherche BOFiP" sur le Bureau de l'utilisateur.
powershell -NoProfile -Command "$s = (New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Recherche BOFiP.lnk'); $s.TargetPath = '%~dp0rechercher_bofip.bat'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = '%SystemRoot%\System32\shell32.dll,22'; $s.Save()"
if errorlevel 1 (
    echo Le raccourci n'a pas pu etre cree.
) else (
    echo Raccourci "Recherche BOFiP" cree sur le Bureau.
)
pause
