@echo off
setlocal EnableDelayedExpansion
TITLE "Pull Request from Local (Voice2Text)"

cd /d "%~dp0"

echo.
echo ================================
echo PR Helper - Local to GitHub
echo ================================
echo Repo folder: %CD%
echo.

REM ---- Check git exists ----
git --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] git not found. Install Git for Windows and try again.
  pause
  exit /b 1
)

REM ---- Check repo ----
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo [ERROR] This folder is not a git repository.
  pause
  exit /b 1
)

REM ---- Abort if merge conflicts ----
for /f %%C in ('git diff --name-only --diff-filter=U') do (
  echo [ERROR] Merge conflicts detected: %%C
  echo Resolve conflicts first, then rerun this script.
  pause
  exit /b 1
)

REM ---- Ensure .gitignore has common ignores ----
if not exist ".gitignore" (
  echo [INFO] Creating .gitignore
  type nul > .gitignore
)
call :ensure_ignore "__pycache__/"
call :ensure_ignore "*.pyc"
call :ensure_ignore "venv_ucm_voice2text_python311/"
call :ensure_ignore ".venv/"

REM ---- Remove tracked pycache/pyc if any ----
echo [INFO] Cleaning tracked __pycache__ / *.pyc (if tracked)...
for /f "delims=" %%F in ('git ls-files ^| findstr /i "\\__pycache__\\ \.pyc$"') do (
  echo   - untracking: %%F
  git rm --cached "%%F" >nul 2>&1
)

echo.
git status
echo.

REM ---- Determine current branch ----
for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD') do set "CUR_BRANCH=%%B"

REM ---- Ask for branch name if on main ----
set "BRANCH=%CUR_BRANCH%"
if /i "%CUR_BRANCH%"=="main" (
  set /p BRANCH=You are on main. Enter new branch name (e.g. fix/spanish-asr): 
  if "%BRANCH%"=="" (
    echo [ERROR] Branch name cannot be empty.
    pause
    exit /b 1
  )
  echo [INFO] Creating branch: %BRANCH%
  git checkout -b "%BRANCH%"
  if errorlevel 1 (
    echo [ERROR] Failed to create branch.
    pause
    exit /b 1
  )
) else (
  echo [INFO] Using current branch: %BRANCH%
)

REM ---- Stage changes ----
echo.
echo [INFO] Staging changes...
git add -A
if errorlevel 1 (
  echo [ERROR] git add failed.
  pause
  exit /b 1
)

REM ---- Commit only if there are staged changes ----
git diff --cached --quiet
set "DIFF_STAGED=%ERRORLEVEL%"

if "%DIFF_STAGED%"=="1" (
  echo.
  set /p MSG=Commit message (no quotes needed, blank = default): 
  call :strip_quotes MSG
  if "!MSG!"=="" set "MSG=Update app"

  echo [INFO] Committing with message: !MSG!
  git commit -m "!MSG!"
  if errorlevel 1 (
    echo [ERROR] git commit failed.
    pause
    exit /b 1
  )
) else (
  echo [INFO] No staged changes to commit.
)

REM ---- Push ----
echo.
echo [INFO] Pushing branch to origin...
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if errorlevel 1 (
  git push -u origin "%BRANCH%"
) else (
  git push
)
if errorlevel 1 (
  echo [ERROR] git push failed.
  pause
  exit /b 1
)

REM ---- Create PR (gh if available) ----
where gh >nul 2>&1
if errorlevel 1 (
  echo.
  echo [INFO] GitHub CLI (gh) not found. Printing PR URL instead...
  call :print_compare_url "%BRANCH%"
  echo.
  echo Open the URL above to create the Pull Request.
  pause
  exit /b 0
)

echo.
set /p PR_TITLE=PR title (blank = default): 
call :strip_quotes PR_TITLE
if "!PR_TITLE!"=="" set "PR_TITLE=Update Voice2Text Agent"

set /p PR_BODY=PR body (optional, single line): 
call :strip_quotes PR_BODY
if "!PR_BODY!"=="" set "PR_BODY=- Changes pushed from local branch %BRANCH%"

echo [INFO] Creating PR with gh...
gh pr create --base main --head "%BRANCH%" --title "!PR_TITLE!" --body "!PR_BODY!"
if errorlevel 1 (
  echo [WARN] gh PR creation failed (maybe not authenticated).
  echo You can still create the PR manually using the URL below:
  call :print_compare_url "%BRANCH%"
  pause
  exit /b 0
)

echo.
echo ✅ Done. PR created (or already exists).
pause
exit /b 0


REM =========================
REM Helpers
REM =========================
:ensure_ignore
set "LINE=%~1"
findstr /x /c:"%LINE%" .gitignore >nul 2>&1
if errorlevel 1 (
  echo %LINE%>> .gitignore
)
exit /b 0

:strip_quotes
REM Removes surrounding quotes if user typed them
set "val=!%~1!"
if defined val (
  if "!val:~0,1!"=="^"" (
    if "!val:~-1!"=="^"" (
      set "val=!val:~1,-1!"
    )
  )
)
set "%~1=!val!"
exit /b 0

:print_compare_url
set "BR=%~1"
for /f "delims=" %%R in ('powershell -NoProfile -Command ^
  "$u=(git remote get-url origin); if($u -match 'github\.com[:/](.+?)(\.git)?$'){ $Matches[1] }"') do set "REPOSLUG=%%R"
if "%REPOSLUG%"=="" (
  echo [ERROR] Could not parse GitHub repo from origin remote.
  echo Run: git remote -v
  exit /b 0
)
echo https://github.com/%REPOSLUG%/compare/%BR%?expand=1
exit /b 0