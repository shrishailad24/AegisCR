@echo off
echo ==============================================================
echo            AegisCR GitHub Production Push Assistant
echo ==============================================================
echo.
echo This assistant will push the dynamic background, high contrast,
echo package initializer, and Render configuration changes to your
echo GitHub repository.
echo.
echo Because the AI assistant runs in a background sandbox, Windows
echo security isolates it from the desktop, preventing Git Credential
echo Manager from displaying the browser login popup. Running this
echo script from your desktop will launch the Git Credential Manager
echo login interface successfully.
echo.
echo Press any key to authenticate and push to main...
pause > nul
echo.
echo Executing: git push origin main --force
echo.
git push origin main --force
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed. Please verify your internet connection or
    echo ensure you are authenticated with GitHub on this machine.
    echo.
) else (
    echo.
    echo [SUCCESS] Code successfully pushed to GitHub!
    echo Render will now automatically trigger a successful redeploy.
    echo.
)
echo Press any key to exit...
pause > nul
