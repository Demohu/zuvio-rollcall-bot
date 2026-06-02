@echo off
echo ==========================================
echo  Compiling Zuvio Rollcall Bot to EXE...
echo  (This may take 1 to 2 minutes)
echo ==========================================
echo.

python -m PyInstaller --clean --onefile --noconsole Zuvio.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Compilation failed!
    goto :end
)

echo.
echo Cleaning temporary files...
del /s /q /f Zuvio.spec >nul 2>&1
rmdir /s /q __pycache__ >nul 2>&1
rmdir /s /q build >nul 2>&1

echo.
echo ==========================================
echo  SUCCESS!
echo  Executable created at: dist\Zuvio.exe
echo ==========================================
echo.

:end
pause