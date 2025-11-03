# 文字選取功能測試指南

## 修正內容總結

### 問題根源
1. **雙重縮放問題**：PDF 渲染時已縮放，但顯示時又再次縮放
2. **座標偏移未處理**：圖片在 QLabel 中居中顯示，但座標映射未考慮偏移
3. **縮放值未同步**：渲染縮放值與顯示縮放值不一致

### 修正措施

#### 1. 移除雙重縮放（`src/pdf_viewer.py`）
```python
# 修正前：會二次縮放
def update_display(self):
    scaled_pixmap = self.current_pixmap.scaled(...)
    
# 修正後：直接顯示（已在渲染時縮放）
def update_display(self):
    super().setPixmap(self.current_pixmap)
```

#### 2. 同步縮放值（`src/pdf_viewer.py`）
```python
def display_page(self, pixmap: QPixmap, page_num: int, zoom: float = 1.0):
    self.page_widget.zoom_level = zoom  # 同步縮放級別
```

#### 3. 處理座標偏移（`src/pdf_viewer.py`）
```python
def get_pixmap_offset(self):
    """獲取圖片在 QLabel 中的偏移量"""
    offset_x = (label_width - pixmap_width) / 2
    offset_y = (label_height - pixmap_height) / 2
    return (max(0, offset_x), max(0, offset_y))

def map_rect_to_pdf(self, rect: QRectF) -> QRectF:
    offset_x, offset_y = self.get_pixmap_offset()
    pdf_rect = QRectF(
        (rect.x() - offset_x) / self.zoom_level,
        (rect.y() - offset_y) / self.zoom_level,
        rect.width() / self.zoom_level,
        rect.height() / self.zoom_level
    )
    return pdf_rect
```

#### 4. 改進文字提取（`src/pdf_handler.py`）
```python
def get_text_from_rect(self, page_num: int, rect) -> str:
    # 使用 get_text() 配合 clip 參數，更準確
    text = page.get_text("text", clip=fitz_rect)
    return text.strip() if text else ""
```

## 測試步驟

### 基本功能測試

1. **開啟 PDF 文件**
   ```
   檔案 → 開啟... → 選擇 PDF
   ```

2. **測試文字選取**
   - 在 PDF 中拖曳滑鼠選取一段文字
   - 觀察藍色選取框是否準確覆蓋文字
   - 查看側邊欄「翻譯」分頁中的「原文」
   - 確認提取的文字與選取區域完全一致

3. **測試不同縮放級別**
   - 100% 縮放：選取文字並確認
   - 放大到 150%：選取文字並確認
   - 縮小到 75%：選取文字並確認
   - 適應寬度：選取文字並確認
   - 適應頁面：選取文字並確認

4. **測試不同位置**
   - 頁面頂部的文字
   - 頁面中間的文字
   - 頁面底部的文字
   - 頁面左側的文字
   - 頁面右側的文字

5. **測試不同選取大小**
   - 選取單一單詞
   - 選取一行文字
   - 選取一段文字
   - 選取多段文字
   - 選取整頁文字

### 翻譯功能測試

1. **選取文字翻譯**
   - 選取英文文字
   - 點擊「翻譯選取」
   - 確認翻譯結果正確

2. **使用快捷鍵**
   - 選取文字
   - 按 `Ctrl+T`
   - 確認自動翻譯

3. **翻譯目前頁面**
   - 工具 → 翻譯目前頁面
   - 確認提取整頁文字
   - 確認翻譯結果

4. **翻譯整份文件**
   - 工具 → 翻譯整份文件
   - 確認逐頁翻譯
   - 觀察進度條
   - 確認最終結果

## 預期結果

✅ **選取框準確**
- 藍色虛線框精確覆蓋選取的文字
- 框的位置、大小與實際選取一致

✅ **文字提取正確**
- 「原文」區域顯示的文字與選取的文字完全相同
- 沒有截斷、錯位或遺漏
- 保留原始的換行和格式

✅ **翻譯功能正常**
- 翻譯結果準確
- 進度顯示正常
- 沒有錯誤訊息

## 已知限制

1. **頁面旋轉**：如果 PDF 頁面旋轉了 90/180/270 度，座標映射可能不準確
2. **多欄佈局**：對於多欄佈局，文字提取順序可能不理想
3. **圖表區域**：選取圖表或圖片區域不會提取到文字
4. **掃描版 PDF**：純圖片的 PDF（無文字層）無法提取文字

## 除錯資訊

如果仍然有座標問題，可以添加調試輸出：

```python
def on_text_selected(self, rect):
    """文字被選取事件"""
    print(f"選取區域（螢幕座標）: {rect}")
    
    # 獲取偏移
    offset_x, offset_y = self.pdf_viewer.page_widget.get_pixmap_offset()
    print(f"偏移量: ({offset_x}, {offset_y})")
    
    # 縮放值
    zoom = self.current_zoom
    print(f"縮放值: {zoom}")
    
    # PDF 座標
    text = self.pdf_handler.get_text_from_rect(self.current_page, rect)
    print(f"提取文字: {text[:50]}...")
```

## 回報問題

如果測試時發現問題，請提供：
1. PDF 文件（或截圖）
2. 選取的位置和範圍
3. 當前縮放級別
4. 預期提取的文字
5. 實際提取的文字
6. 應用程式的錯誤訊息（如有）

