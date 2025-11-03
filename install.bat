@echo off
REM PDF 閱讀器安裝腳本

echo ========================================
echo PDF 閱讀器 - 自動安裝
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python
    echo 請先安裝 Python 3.8 或更新版本
    echo 下載位置: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [資訊] 已找到 Python
python --version
echo.

REM 檢查虛擬環境是否已存在
if exist "venv\" (
    echo [資訊] 虛擬環境已存在
) else (
    echo [步驟 1/3] 建立虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo [錯誤] 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo [完成] 虛擬環境建立完成
)
echo.

echo [步驟 2/3] 啟動虛擬環境...
call venv\Scripts\activate.bat
echo.

echo [步驟 3/3] 安裝依賴套件...
echo 這可能需要幾分鐘時間...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [錯誤] 安裝依賴套件失敗
    echo 請檢查網路連線或嘗試使用映像源:
    echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)
echo.

echo ========================================
echo [完成] 安裝成功！
echo ========================================
echo.
echo 使用方法:
echo 1. 執行 run.bat 啟動應用程式
echo 2. 或手動執行:
echo    - venv\Scripts\activate.bat
echo    - python main.py
echo.
pause

