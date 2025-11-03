# 快速入門指南

## 5 分鐘快速開始

### 方法一：使用自動安裝腳本（推薦）

1. **雙擊執行 `install.bat`**
   - 自動建立虛擬環境
   - 自動安裝所有依賴
   - 顯示安裝進度

2. **雙擊執行 `run.bat`**
   - 自動啟動應用程式

就這麼簡單！

### 方法二：手動安裝

#### 步驟 1：啟動虛擬環境

開啟命令提示字元或 PowerShell，切換到專案目錄：

```cmd
cd C:\python\PDFReader
```

啟動虛擬環境：

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

#### 步驟 2：安裝依賴

```bash
pip install -r requirements.txt
```

#### 步驟 3：啟動應用程式

```bash
python main.py
```

## 第一次使用

### 1. 開啟 PDF

啟動應用程式後：
- 點擊工具列的「開啟」按鈕
- 或按 `Ctrl+O`
- 選擇一個 PDF 檔案

### 2. 探索功能

#### 基本操作
- **翻頁**: 使用工具列的上一頁/下一頁按鈕
- **縮放**: 使用 + / - 按鈕或下拉選單
- **側邊欄**: 查看縮圖、書籤和註解

#### 註解工具
1. 點擊選單 → 工具 → 註解工具
2. 選擇工具（高亮、底線、文字註解等）
3. 在 PDF 上操作
4. Ctrl+S 儲存

#### 書籤
1. 瀏覽到想加書籤的頁面
2. 按 `Ctrl+B`
3. 輸入書籤名稱
4. 在側邊欄的「書籤」標籤中查看

### 3. 深色模式

點擊工具列的「深色模式」按鈕，立即切換外觀！

## 常用快捷鍵

| 功能 | 快捷鍵 |
|------|--------|
| 開啟 | Ctrl+O |
| 儲存 | Ctrl+S |
| 搜尋 | Ctrl+F |
| 放大 | Ctrl++ |
| 縮小 | Ctrl+- |
| 書籤 | Ctrl+B |
| 全螢幕 | F11 |

## 問題排除

### ❌ 執行 install.bat 時出現「找不到 Python」

**解決方法：**
1. 確認已安裝 Python 3.8 或更新版本
2. 從 [python.org](https://www.python.org/downloads/) 下載並安裝
3. **重要**：安裝時勾選「Add Python to PATH」

### ❌ PowerShell 無法執行腳本

**解決方法：**
以系統管理員身分開啟 PowerShell，執行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

或者改用 CMD 而不是 PowerShell。

### ❌ 安裝依賴太慢

**解決方法：**
使用國內映像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### ❌ 應用程式啟動後看不到視窗

**解決方法：**
1. 檢查工作列是否有應用程式圖示
2. 確認沒有錯誤訊息
3. 嘗試按 Alt+Tab 切換視窗

## 進階使用

詳細的功能說明請參閱：
- **USAGE.md** - 完整使用手冊
- **PROJECT_STATUS.md** - 功能清單和狀態

## 需要幫助？

1. 檢查 **INSTALL.md** - 詳細安裝指南
2. 檢查 **USAGE.md** - 功能使用說明
3. 查看程式碼註解 - 所有模組都有詳細的中文註解

## 下一步

探索更多功能：
- ✏️ 嘗試各種註解工具
- 📑 建立書籤組織你的文件
- 🔍 使用搜尋功能快速找到內容
- ✍️ 試試數位簽章功能
- 📋 填寫 PDF 表單

享受使用 PDF 閱讀器！

