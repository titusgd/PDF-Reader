# 原文框可編輯功能說明

## 更新內容

### 修改項目

將翻譯面板中的「原文」框從只讀模式改為可編輯模式，使用戶可以：
1. 直接輸入要翻譯的文字
2. 編輯從 PDF 選取的文字
3. 複製貼上外部文字進行翻譯

### 修改檔案

`src/sidebar.py` - `TranslationWidget` 類別

## 功能特性

### 1. 可編輯的原文框

```python
self.original_text.setReadOnly(False)  # 允許編輯
```

**特性：**
- ✅ 可以直接輸入文字
- ✅ 可以編輯已選取的文字
- ✅ 可以複製貼上
- ✅ 支援多行文字
- ✅ 支援 Ctrl+A、Ctrl+C、Ctrl+V 等快捷鍵

### 2. 自動同步與按鈕控制

```python
def on_original_text_changed(self):
    """原文文字改變事件"""
    # 同步更新 selected_text
    self.selected_text = self.original_text.toPlainText()
    # 根據文字內容啟用/停用翻譯按鈕
    has_text = bool(self.selected_text.strip())
    self.translate_selected_btn.setEnabled(has_text)
```

**功能：**
- 當用戶輸入或修改文字時
- 自動更新內部的 `selected_text` 變數
- 自動啟用「翻譯選取」按鈕（如果有文字）
- 自動停用「翻譯選取」按鈕（如果沒有文字）

### 3. 避免無限循環

```python
def set_selected_text(self, text: str):
    """設定選取的文字"""
    # 使用 blockSignals 避免觸發 textChanged 信號
    self.original_text.blockSignals(True)
    self.original_text.setPlainText(text)
    self.original_text.blockSignals(False)
```

**說明：**
- 當從 PDF 選取文字時，使用 `blockSignals` 避免觸發 `textChanged`
- 防止不必要的信號發射和處理

## 使用方式

### 方式 1：從 PDF 選取文字

1. 在 PDF 中拖曳滑鼠選取文字
2. 文字自動填入「原文」框
3. 可以直接翻譯，或先編輯再翻譯

### 方式 2：直接輸入文字

1. 點擊「原文」框
2. 直接輸入要翻譯的文字
3. 點擊「翻譯選取」按鈕

### 方式 3：複製貼上

1. 從其他地方複製文字（Ctrl+C）
2. 點擊「原文」框
3. 貼上文字（Ctrl+V）
4. 點擊「翻譯選取」按鈕

### 方式 4：編輯已選取的文字

1. 從 PDF 選取文字（自動填入原文框）
2. 在原文框中修改或調整文字
3. 點擊「翻譯選取」按鈕

## UI 改進

### 提示文字更新

```python
self.original_text.setPlaceholderText("選取 PDF 中的文字，或直接輸入要翻譯的文字...")
```

**說明：**
- 提示用戶可以選取或輸入
- 當框內沒有文字時顯示
- 輸入文字後自動消失

## 行為說明

### 按鈕狀態控制

| 原文框狀態 | 「翻譯選取」按鈕 | 「翻譯文件」按鈕 |
|-----------|----------------|----------------|
| 空白 | 停用 | 啟用（如有文件） |
| 有文字 | 啟用 | 啟用（如有文件） |
| 翻譯中 | 停用 | 停用 |

### 快捷鍵支援

- `Ctrl+A`：全選文字
- `Ctrl+C`：複製文字
- `Ctrl+V`：貼上文字
- `Ctrl+X`：剪下文字
- `Ctrl+Z`：復原
- `Ctrl+Y`：重做
- `Ctrl+T`：翻譯（當有文字時）

## 範例使用情境

### 情境 1：翻譯 PDF 中的部分文字

1. 選取 Abstract 段落
2. 文字自動填入原文框
3. 發現選取範圍多了一些不需要的內容
4. 在原文框中刪除多餘的文字
5. 點擊「翻譯選取」

### 情境 2：翻譯網頁上的文字

1. 從瀏覽器複製一段英文
2. 切換到 PDF 閱讀器
3. 點擊翻譯分頁
4. 在原文框中貼上文字
5. 點擊「翻譯選取」

### 情境 3：翻譯並修正

1. 從 PDF 選取文字
2. 發現某些單詞拼寫錯誤
3. 在原文框中修正拼寫
4. 翻譯修正後的文字

### 情境 4：組合多處文字

1. 從 PDF 選取第一段文字
2. 在原文框中保留
3. 手動添加換行
4. 複製第二段文字並貼上
5. 翻譯組合後的文字

## 技術細節

### 信號處理

```python
# 連接 textChanged 信號
self.original_text.textChanged.connect(self.on_original_text_changed)

# 處理函數
def on_original_text_changed(self):
    self.selected_text = self.original_text.toPlainText()
    has_text = bool(self.selected_text.strip())
    self.translate_selected_btn.setEnabled(has_text)
```

### 避免循環

```python
# 設定文字時阻止信號
self.original_text.blockSignals(True)
self.original_text.setPlainText(text)
self.original_text.blockSignals(False)
```

## 相容性

- ✅ 與 PDF 文字選取功能完全相容
- ✅ 與快捷鍵 Ctrl+T 相容
- ✅ 與翻譯工作流程相容
- ✅ 不影響「翻譯文件」功能

## 優點

1. **更靈活**：不僅限於 PDF 內容
2. **可修正**：可以編輯選取的文字
3. **更方便**：支援複製貼上
4. **更直觀**：即時啟用/停用按鈕

## 注意事項

1. 原文框最大高度為 150 像素，超過會顯示捲軸
2. 翻譯時會停用按鈕，防止重複提交
3. 空白或純空格不會啟用翻譯按鈕
4. 修改原文後需要重新點擊翻譯按鈕

