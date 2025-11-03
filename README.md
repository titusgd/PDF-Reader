# PyQt6 PDF 閱讀器

**一個功能完整、介面現代化的 PDF 閱讀器**

使用 Python 和 PyQt6 開發

[快速開始](#快速開始)
[功能特色](#功能特色)
[安裝指南](#安裝指南)
[使用文件](#文件)

---

## 📸 專案特點

- ✨ **現代化介面**：Material Design 風格，支援深色模式
- 🚀 **功能完整**：註解、書籤、表單、數位簽章等豐富功能
- 💻 **跨平台**：支援 Windows、macOS、Linux
- 🎯 **易於使用**：直覺的操作介面，完整的中文化
- 🔧 **模組化設計**：清晰的程式碼架構，便於擴展

## 🚀 快速開始

### Windows 使用者（推薦）

1. **雙擊執行 `install.bat`** - 自動安裝所有依賴
2. **雙擊執行 `run.bat`** - 啟動應用程式

就這麼簡單！ 🎉

### 手動安裝

```bash
# 1. 啟動虛擬環境（已建立）
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # macOS/Linux

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 啟動應用程式
python main.py
```

詳細安裝說明請參閱 [QUICKSTART.md](QUICKSTART.md) 或 [INSTALL.md](INSTALL.md)

## ✨ 功能特色

### 核心功能

| 功能類別 | 功能說明 |
|---------|---------|
| 📖 **基本操作** | PDF 開啟、頁面導航、縮放（50%-300%）、旋轉 |
| 🖼️ **檢視模式** | 縮圖預覽、全螢幕、深色模式、文字選取複製 |
| 🔍 **搜尋** | 全文搜尋、結果計數、快速跳轉 |
| 📝 **註解工具** | 高亮、底線、刪除線、文字註解、手繪、圖形標註 |
| 🔖 **書籤管理** | 新增書籤、書籤列表、一鍵跳轉、書籤編輯 |
| 📋 **表單處理** | 表單辨識、填寫、資料匯入/匯出 |
| ✍️ **數位簽章** | 視覺化簽章、文字簽章、簽章管理 |
| 💾 **檔案操作** | 儲存、另存新檔、設定記憶 |

### 介面特色

- 🎨 **精美的 UI**：採用 Material Design 配色
- 🌓 **深色模式**：保護眼睛，夜間使用更舒適
- 🔧 **自訂工具列**：常用功能一鍵觸達
- 📐 **側邊欄**：縮圖、書籤、註解三合一
- ⌨️ **快捷鍵支援**：提升操作效率

## 📚 文件

| 文件 | 說明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5 分鐘快速入門指南 |
| [INSTALL.md](INSTALL.md) | 詳細安裝說明和問題排除 |
| [USAGE.md](USAGE.md) | 完整功能使用手冊 |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | 專案狀態和開發進度 |

## 🎯 使用範例

### 基本操作

```python
# 應用程式會自動處理 PDF 開啟和渲染
# 使用 GUI 介面進行操作：

1. 開啟 PDF：Ctrl+O
2. 瀏覽頁面：使用工具列按鈕或頁碼輸入框
3. 縮放控制：選擇縮放比例或使用 Ctrl+/Ctrl-
4. 新增註解：工具 → 註解工具 → 選擇工具類型
5. 新增書籤：Ctrl+B
6. 儲存檔案：Ctrl+S
```

### 快捷鍵

| 功能 | Windows/Linux | macOS |
|------|---------------|-------|
| 開啟檔案 | Ctrl+O | Cmd+O |
| 儲存 | Ctrl+S | Cmd+S |
| 搜尋 | Ctrl+F | Cmd+F |
| 放大/縮小 | Ctrl+/- | Cmd+/- |
| 新增書籤 | Ctrl+B | Cmd+B |
| 全螢幕 | F11 | F11 |

## 🛠️ 技術架構

### 核心技術

- **GUI 框架**：PyQt6 6.6.1
- **PDF 處理**：PyMuPDF (fitz) 1.23.26
- **圖片處理**：Pillow 10.1.0
- **加密支援**：cryptography 41.0.7

### 專案結構

```
PDFReader/
├── src/              # 原始碼
│   ├── main_window.py      # 主視窗
│   ├── pdf_viewer.py       # PDF 檢視器
│   ├── pdf_handler.py      # PDF 處理核心
│   ├── annotation.py       # 註解管理
│   ├── bookmark.py         # 書籤管理
│   ├── form_editor.py      # 表單編輯
│   ├── signature.py        # 數位簽章
│   ├── toolbar.py          # 工具列
│   ├── sidebar.py          # 側邊欄
│   └── utils.py            # 工具函數
├── resources/        # 資源檔案
│   └── styles/             # QSS 樣式表
├── tests/            # 測試檔案
├── main.py           # 應用程式入口
└── requirements.txt  # 依賴清單
```

## 📋 系統需求

- **Python**：3.8 或更新版本
- **作業系統**：Windows 10+、macOS 10.14+、Linux（任何現代發行版）
- **記憶體**：建議 2GB 以上
- **硬碟空間**：約 200MB（含虛擬環境）

## 🔄 開發狀態

**目前版本：1.0.0**

- ✅ 核心功能：100% 完成
- ✅ 基礎 UI：100% 完成
- ✅ 註解系統：100% 完成
- ✅ 書籤系統：100% 完成
- ✅ 表單處理：80% 完成
- ✅ 數位簽章：70% 完成
- ⏳ 列印功能：開發中

詳細狀態請參閱 [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 🤝 貢獻

歡迎貢獻！專案採用模組化設計，易於擴展。

## 📄 授權

本專案採用 MIT 授權條款。

## 💡 提示

- 首次使用請參閱 [QUICKSTART.md](QUICKSTART.md)
- 遇到問題請查看 [INSTALL.md](INSTALL.md) 的問題排除章節
- 詳細功能說明請參考 [USAGE.md](USAGE.md)

