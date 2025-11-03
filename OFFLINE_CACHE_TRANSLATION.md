# 快取式離線翻譯使用指南

## 📝 概述

由於 Windows 環境下 PyTorch 存在 DLL 相容性問題，我們改用**快取式離線翻譯**方案。這個方案簡單、穩定，不需要額外的大型依賴套件。

## 🔧 工作原理

### 1. 線上模式（預設）
- 使用 Google Translate 進行翻譯
- 自動將翻譯結果儲存到本地快取
- 需要網路連線

### 2. 離線模式
- 僅使用已快取的翻譯結果
- 如果文字未在快取中，會顯示錯誤訊息
- 完全不需要網路連線

## 💡 使用流程

### 步驟 1：在有網路時建立快取

```
1. 確保網路連線正常
2. 開啟 PDF 文件
3. 選取要翻譯的文字
4. 點擊「翻譯選取」
5. 翻譯結果會自動儲存到快取
```

### 步驟 2：切換到離線模式

在 `src/main_window.py` 中修改：

```python
# 第 98 行
self.translation_manager = TranslationManager(use_offline=True)  # 啟用離線模式
```

### 步驟 3：在無網路環境使用

```
1. 啟動應用程式（已切換到離線模式）
2. 選取之前翻譯過的文字
3. 點擊「翻譯選取」
4. 系統會從快取中讀取翻譯結果
```

## 📂 快取檔案位置

快取檔案儲存在：
- **Windows**: `C:\Users\{用戶名}\.pdfreader_translation_cache.pkl`
- **Linux/Mac**: `~/.pdfreader_translation_cache.pkl`

## ⚙️ 進階設定

### 方法 1：在程式中切換模式

```python
# 切換到離線模式
translation_manager.set_offline_mode(True)

# 切換到線上模式
translation_manager.set_offline_mode(False)
```

### 方法 2：查看快取大小

```python
cache_size = translation_manager.get_cache_size()
print(f"快取中有 {cache_size} 筆翻譯")
```

### 方法 3：清除快取

```python
translation_manager.clear_cache()
```

## 🎯 使用場景

### ✅ 適合的場景

1. **重複翻譯相同文件**
   - 第一次在線上翻譯
   - 後續可在離線環境查看

2. **預先建立翻譯庫**
   - 在有網路時翻譯所有常用文字
   - 在無網路環境直接使用

3. **提升翻譯速度**
   - 快取的翻譯結果即時載入
   - 無需等待網路請求

### ⚠️ 限制

1. **無法翻譯新文字**
   - 離線模式下，未快取的文字無法翻譯
   - 必須先在線上模式建立快取

2. **快取大小**
   - 快取會隨著使用增長
   - 建議定期清理不需要的快取

3. **不同語言對**
   - 每個語言對都是獨立快取
   - 需要分別建立快取

## 📊 使用範例

### 範例 1：建立常用文件的翻譯快取

```python
# 1. 線上模式（預設）
translation_manager = TranslationManager(use_offline=False)

# 2. 翻譯常用段落
paragraphs = [
    "Abstract. Human detection has several...",
    "Introduction. Artificial Intelligence (AI)...",
    "Conclusion. In this study we...",
]

for para in paragraphs:
    result = translation_manager.translate(para, "en", "zh-TW")
    print(f"已快取: {para[:30]}...")

# 3. 切換到離線模式
translation_manager.set_offline_mode(True)

# 4. 現在可以在無網路環境使用
result = translation_manager.translate(paragraphs[0], "en", "zh-TW")
print("離線翻譯:", result)
```

### 範例 2：檢查是否在快取中

```python
# 快取的文字可以立即翻譯
text1 = "Hello, world!"
translation_manager.translate(text1, "en", "zh-TW")  # 第一次：線上翻譯並快取

# 第二次：從快取讀取（即使在離線模式）
result = translation_manager.translate(text1, "en", "zh-TW")  # 即時返回
```

## 🔄 匯出和匯入快取

### 匯出快取（在有網路的電腦）

```python
import shutil
from pathlib import Path

# 找到快取檔案
cache_file = Path.home() / ".pdfreader_translation_cache.pkl"

# 複製到可攜式儲存裝置
shutil.copy(cache_file, "/path/to/usb/translation_cache.pkl")
```

### 匯入快取（在無網路的電腦）

```python
import shutil
from pathlib import Path

# 從 USB 複製快取檔案
source = Path("/path/to/usb/translation_cache.pkl")
target = Path.home() / ".pdfreader_translation_cache.pkl"

shutil.copy(source, target)
```

## 🛠️ 除錯

### 問題 1：離線模式無法翻譯

**錯誤訊息**：`離線模式：無法翻譯新文字（未在快取中）`

**解決方法**：
1. 切換到線上模式
2. 翻譯該文字以建立快取
3. 再切換回離線模式

### 問題 2：快取檔案損壞

**錯誤訊息**：`載入快取失敗`

**解決方法**：
1. 刪除快取檔案
2. 重新建立快取

### 問題 3：快取太大

**解決方法**：
```python
# 清除所有快取
translation_manager.clear_cache()

# 只保留最近使用的翻譯
# （需要自己實作基於時間的清理邏輯）
```

## 📈 效能對比

| 模式 | 首次翻譯 | 重複翻譯 | 網路需求 | 儲存需求 |
|------|---------|---------|---------|---------|
| 線上模式 | 2-5秒 | 2-5秒 | 需要 | 最小 |
| 線上+快取 | 2-5秒 | <0.1秒 | 需要 | 中等 |
| 離線模式 | N/A | <0.1秒 | 不需要 | 中等 |

## 💻 系統需求

- **Python**: 3.8+
- **依賴套件**: 
  - `deep-translator>=1.11.0`（線上翻譯）
  - 標準函式庫（快取功能）
- **儲存空間**: 視快取大小而定（通常 <10MB）
- **網路**: 僅線上模式需要

## 🎓 最佳實踐

1. **定期備份快取**
   - 將快取檔案複製到安全位置
   - 避免意外刪除

2. **分類建立快取**
   - 為不同專案建立不同的快取檔案
   - 使用環境變數指定快取路徑

3. **監控快取大小**
   - 定期檢查快取大小
   - 清除不需要的翻譯

4. **團隊共享快取**
   - 在一台電腦建立快取
   - 分享給團隊其他成員使用

## ⚡ 與 PyTorch 方案的對比

| 特性 | 快取式離線 | PyTorch 離線 |
|------|-----------|-------------|
| **安裝難度** | ⭐ 簡單 | ⭐⭐⭐⭐⭐ 困難 |
| **DLL 問題** | ✅ 無 | ❌ 有 |
| **儲存需求** | ~10MB | ~5GB |
| **翻譯新文字** | ❌ 不可（需先快取） | ✅ 可以 |
| **翻譯速度** | ⭐⭐⭐⭐⭐ 即時 | ⭐⭐⭐ 中等 |
| **翻譯品質** | ⭐⭐⭐⭐⭐ Google | ⭐⭐⭐⭐ MarianMT |
| **適用場景** | 重複文件 | 新文件 |

## 📝 結論

快取式離線翻譯雖然無法翻譯全新的文字，但對於需要重複查看相同文件的場景非常適合。它簡單、穩定、無依賴問題，是在 Windows 環境下實現離線翻譯的實用方案。

### 使用建議

- **有網路環境**：使用線上模式，自動建立快取
- **無網路環境**：切換到離線模式，使用快取翻譯
- **混合環境**：在有網路時預先翻譯，在無網路時查看

---

**版本**: 1.0
**更新日期**: 2025-11-03
**狀態**: ✅ 生產就緒

