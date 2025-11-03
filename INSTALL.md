# 安裝指南

## 系統需求

- Windows 10 或更新版本
- Python 3.8 或更新版本

## 安裝步驟

### 1. 確認 Python 版本

開啟命令提示字元或 PowerShell，執行：

```bash
python --version
```

確認版本為 3.8 或以上。

### 2. 建立虛擬環境

已經建立好了 `venv` 虛擬環境。啟動它：

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

這將安裝以下套件：
- PyQt6: GUI 框架
- PyMuPDF (fitz): PDF 處理
- Pillow: 圖片處理
- cryptography: 加密和數位簽章
- python-dateutil: 日期時間工具

### 4. 驗證安裝

安裝完成後，可以執行：

```bash
python -c "import PyQt6; import fitz; print('安裝成功！')"
```

如果看到「安裝成功！」表示所有依賴都已正確安裝。

## 啟動應用程式

```bash
python main.py
```

## 常見問題

### Q: 啟動虛擬環境時出現「無法載入檔案，因為這個系統上已停用指令碼執行」錯誤

**A:** 這是 PowerShell 的執行原則限制。解決方法：

1. 以系統管理員身分開啟 PowerShell
2. 執行：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. 輸入 `Y` 確認
4. 重新啟動虛擬環境

或者，您可以使用 CMD 而不是 PowerShell。

### Q: pip install 速度很慢

**A:** 可以使用國內映像源加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 缺少 Microsoft Visual C++ 相關錯誤

**A:** 某些套件需要 Visual C++ 運行庫。請下載並安裝：
- [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Q: PyQt6 安裝失敗

**A:** 確保 pip 是最新版本：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 解除安裝

1. 退出虛擬環境：
   ```bash
   deactivate
   ```

2. 刪除整個專案資料夾即可

## 更新

要更新所有依賴到最新版本：

```bash
pip install --upgrade -r requirements.txt
```

