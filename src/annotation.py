"""
註解功能模組
提供各種 PDF 註解工具
"""

import fitz
from typing import Optional, List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor


class AnnotationType:
    """註解類型常數"""
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    TEXT = "text"
    FREEHAND = "freehand"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    ARROW = "arrow"


class AnnotationManager(QObject):
    """註解管理器"""
    
    # 信號定義
    annotation_added = pyqtSignal(int, object)  # 新增註解
    annotation_removed = pyqtSignal(int, object)  # 刪除註解
    annotation_modified = pyqtSignal(int, object)  # 修改註解
    
    def __init__(self, pdf_handler):
        super().__init__()
        self.pdf_handler = pdf_handler
        self.current_tool = None
        self.current_color = QColor(255, 255, 0, 100)  # 預設黃色半透明
    
    def set_tool(self, tool_type: str):
        """設定當前工具"""
        self.current_tool = tool_type
    
    def set_color(self, color: QColor):
        """設定當前顏色"""
        self.current_color = color
    
    def add_highlight(self, page_num: int, rect: fitz.Rect, color: Optional[Tuple] = None) -> bool:
        """
        新增高亮註解
        
        Args:
            page_num: 頁碼
            rect: 矩形區域
            color: RGB 顏色元組 (r, g, b)，範圍 0-1
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (1, 1, 0)  # 預設黃色
            
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=color)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增高亮失敗: {e}")
            return False
    
    def add_underline(self, page_num: int, rect: fitz.Rect, color: Optional[Tuple] = None) -> bool:
        """新增底線註解"""
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (0, 0, 1)  # 預設藍色
            
            annot = page.add_underline_annot(rect)
            annot.set_colors(stroke=color)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增底線失敗: {e}")
            return False
    
    def add_strikeout(self, page_num: int, rect: fitz.Rect, color: Optional[Tuple] = None) -> bool:
        """新增刪除線註解"""
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (1, 0, 0)  # 預設紅色
            
            annot = page.add_strikeout_annot(rect)
            annot.set_colors(stroke=color)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增刪除線失敗: {e}")
            return False
    
    def add_text_annotation(self, page_num: int, point: fitz.Point, text: str) -> bool:
        """
        新增文字註解
        
        Args:
            page_num: 頁碼
            point: 位置點
            text: 註解文字
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            annot = page.add_text_annot(point, text)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增文字註解失敗: {e}")
            return False
    
    def add_freehand(self, page_num: int, points: List[fitz.Point], color: Optional[Tuple] = None, width: float = 1.0) -> bool:
        """
        新增手繪註解
        
        Args:
            page_num: 頁碼
            points: 點列表
            color: RGB 顏色
            width: 線寬
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (0, 0, 0)  # 預設黑色
            
            annot = page.add_ink_annot([points])
            annot.set_colors(stroke=color)
            annot.set_border(width=width)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增手繪註解失敗: {e}")
            return False
    
    def add_rectangle(self, page_num: int, rect: fitz.Rect, color: Optional[Tuple] = None, fill_color: Optional[Tuple] = None) -> bool:
        """新增矩形註解"""
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (1, 0, 0)  # 預設紅色邊框
            
            annot = page.add_rect_annot(rect)
            annot.set_colors(stroke=color, fill=fill_color)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增矩形失敗: {e}")
            return False
    
    def add_circle(self, page_num: int, rect: fitz.Rect, color: Optional[Tuple] = None, fill_color: Optional[Tuple] = None) -> bool:
        """新增圓形註解"""
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            if color is None:
                color = (0, 1, 0)  # 預設綠色邊框
            
            annot = page.add_circle_annot(rect)
            annot.set_colors(stroke=color, fill=fill_color)
            annot.update()
            
            self.annotation_added.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"新增圓形失敗: {e}")
            return False
    
    def get_annotations(self, page_num: int) -> List:
        """獲取頁面所有註解"""
        page = self.pdf_handler.get_page(page_num)
        if not page:
            return []
        
        annotations = []
        for annot in page.annots():
            annotations.append(annot)
        return annotations
    
    def delete_annotation(self, page_num: int, annot) -> bool:
        """刪除註解"""
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            page.delete_annot(annot)
            self.annotation_removed.emit(page_num, annot)
            return True
            
        except Exception as e:
            print(f"刪除註解失敗: {e}")
            return False
    
    def clear_all_annotations(self, page_num: int) -> bool:
        """清除頁面所有註解"""
        annotations = self.get_annotations(page_num)
        for annot in annotations:
            self.delete_annotation(page_num, annot)
        return True

