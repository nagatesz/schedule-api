@echo off
echo We are about to log into GitHub!
echo.
gh_cli\bin\gh.exe auth login --web
echo.
echo Now we will create the repository and push!
gh_cli\bin\gh.exe repo create schedule-api --private --source=. --remote=origin --push
echo.
echo Done! Your code is now on GitHub!
pause
