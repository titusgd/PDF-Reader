@echo off
REM PDF 閱讀器啟動腳本
REM 此腳本會自動啟動虛擬環境並執行應用程式

echo ========================================
echo PDF 閱讀器
echo ========================================
echo.

REM 檢查虛擬環境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo [錯誤] 找不到虛擬環境
    echo 請先執行: python -m venv venv
    echo 然後執行: venv\Scripts\activate.bat
    echo 最後執行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [啟動] 啟動虛擬環境...
call venv\Scripts\activate.bat

echo [啟動] 執行 PDF 閱讀器...
echo.
python main.py

REM 如果程式異常結束，暫停以便查看錯誤訊息
if errorlevel 1 (
    echo.
    echo [錯誤] 程式執行時發生錯誤
    pause
)

deactivate

