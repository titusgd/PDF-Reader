# 文字選取座標修正說明

## 問題描述

用戶選取 PDF 中的文字區域時，應用程式提取的文字與實際選取的區域不符。

### 原因分析

1. **座標偏移問題**
   - PDF 頁面在 QLabel 中居中顯示
   - 選取座標相對於 QLabel，而非相對於圖片
   - 需要減去圖片的偏移量

2. **縮放比例**
   - PDF 渲染時應用了縮放（zoom）
   - 反向映射時需要除以縮放比例

3. **座標系統**
   - 螢幕座標：相對於 QLabel 的像素座標
   - PDF 座標：PyMuPDF 的點座標系統

## 修正方案

### 1. 新增 `get_pixmap_offset()` 方法

```python
def get_pixmap_offset(self):
    """獲取圖片在 QLabel 中的偏移量"""
    # 計算圖片居中顯示的偏移
    offset_x = (label_width - pixmap_width) / 2
    offset_y = (label_height - pixmap_height) / 2
    return (max(0, offset_x), max(0, offset_y))
```

### 2. 改進 `map_rect_to_pdf()` 方法

```python
def map_rect_to_pdf(self, rect: QRectF) -> QRectF:
    """將螢幕矩形映射到 PDF 矩形"""
    # 1. 獲取圖片偏移
    offset_x, offset_y = self.get_pixmap_offset()
    
    # 2. 減去偏移並考慮縮放比例
    pdf_rect = QRectF(
        (rect.x() - offset_x) / self.zoom_level,
        (rect.y() - offset_y) / self.zoom_level,
        rect.width() / self.zoom_level,
        rect.height() / self.zoom_level
    )
    return pdf_rect
```

### 3. 改進 `get_text_from_rect()` 方法

使用 `page.get_text("text", clip=fitz_rect)` 替代 `page.get_textbox()`，提供更準確的文字提取。

## 座標轉換流程

```
用戶選取 (螢幕座標)
    ↓
減去 QLabel 偏移 (offset_x, offset_y)
    ↓
除以縮放比例 (zoom_level)
    ↓
PDF 座標 (用於文字提取)
```

## 測試步驟

1. 開啟包含文字的 PDF 文件
2. 拖曳滑鼠選取一段文字
3. 查看側邊欄「翻譯」分頁中的「原文」
4. 確認提取的文字與選取區域一致

## 已知限制

1. **頁面旋轉**：目前未處理頁面旋轉的情況
2. **多欄佈局**：對於多欄佈局，可能需要額外處理文字順序
3. **圖片區域**：選取圖片區域不會提取文字

## 後續改進

- [ ] 支援頁面旋轉的座標轉換
- [ ] 改善多欄佈局的文字提取順序
- [ ] 添加視覺化調試模式，顯示實際的 PDF 座標範圍
- [ ] 支援 OCR 文字提取（針對掃描版 PDF）

