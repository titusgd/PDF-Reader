"""
PDF 檢視器模組
提供 PDF 頁面顯示和互動功能
"""

from PyQt6.QtWidgets import (QWidget, QScrollArea, QLabel, QVBoxLayout,
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QPointF, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QMouseEvent, QPen, QColor, QPainterPath, QBrush


class PDFPageWidget(QLabel):
    """PDF 頁面顯示元件"""
    
    # 信號定義
    area_selected = pyqtSignal(QRectF)  # 區域被選擇
    point_clicked = pyqtSignal(QPoint)  # 點擊位置
    text_selected = pyqtSignal(QRectF)  # 文字被選取（用於翻譯）
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        
        self.current_pixmap: QPixmap = None
        self.zoom_level = 1.0
        self.rotation = 0
        
        # 互動模式
        self.interaction_mode = "select"  # select, highlight, rectangle, etc.
        self.is_drawing = False
        self.start_point = None
        self.end_point = None
        self.drawing_path = QPainterPath()
        
        # 文字選取
        self.is_selecting_text = False
        self.selection_rect = None
    
    def set_pixmap(self, pixmap: QPixmap):
        """設定顯示的圖片"""
        self.current_pixmap = pixmap
        self.update_display()
    
    def update_display(self):
        """更新顯示"""
        if self.current_pixmap:
            # 直接顯示，不再次縮放（縮放已在渲染時完成）
            super().setPixmap(self.current_pixmap)
    
    def set_zoom(self, zoom: float):
        """設定縮放級別"""
        self.zoom_level = zoom
        # 不在這裡重新顯示，因為需要重新渲染PDF
        # self.update_display()
    
    def get_zoom(self) -> float:
        """獲取當前縮放級別"""
        return self.zoom_level
    
    def set_rotation(self, rotation: int):
        """設定旋轉角度"""
        self.rotation = rotation % 360
        # TODO: 實作旋轉功能
    
    def set_interaction_mode(self, mode: str):
        """設定互動模式"""
        self.interaction_mode = mode
        
        if mode == "select":
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif mode in ["highlight", "underline", "strikeout", "rectangle", "circle"]:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == "freehand":
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == "text":
            self.setCursor(Qt.CursorShape.IBeamCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """滑鼠按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.is_drawing = True
            
            # 檢查是否為文字選取模式
            if self.interaction_mode == "select":
                self.is_selecting_text = True
                self.selection_rect = None
            
            if self.interaction_mode == "freehand":
                self.drawing_path = QPainterPath()
                self.drawing_path.moveTo(self.start_point)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """滑鼠移動事件"""
        if self.is_drawing and self.start_point:
            self.end_point = event.pos()
            
            if self.interaction_mode == "freehand":
                self.drawing_path.lineTo(self.end_point)
            
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """滑鼠釋放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False
            
            if self.interaction_mode == "text":
                self.point_clicked.emit(self.map_to_pdf_coordinates(self.start_point))
            elif self.interaction_mode == "select" and self.is_selecting_text:
                # 文字選取模式
                if self.start_point and self.end_point:
                    # 轉換 QPoint 為 QPointF
                    start_pointf = QPointF(self.start_point)
                    end_pointf = QPointF(self.end_point)
                    rect = QRectF(start_pointf, end_pointf).normalized()
                    pdf_rect = self.map_rect_to_pdf(rect)
                    self.selection_rect = rect
                    self.text_selected.emit(pdf_rect)
                self.is_selecting_text = False
            elif self.start_point and self.end_point:
                # 轉換 QPoint 為 QPointF
                start_pointf = QPointF(self.start_point)
                end_pointf = QPointF(self.end_point)
                rect = QRectF(start_pointf, end_pointf).normalized()
                pdf_rect = self.map_rect_to_pdf(rect)
                self.area_selected.emit(pdf_rect)
            
            self.start_point = None
            self.end_point = None
            self.drawing_path = QPainterPath()
            self.update()
    
    def paintEvent(self, event):
        """繪製事件"""
        super().paintEvent(event)
        
        # 繪製選取框或繪圖
        if self.is_drawing and self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 轉換 QPoint 為 QPointF
            start_pointf = QPointF(self.start_point)
            end_pointf = QPointF(self.end_point)
            
            if self.interaction_mode == "select" and self.is_selecting_text:
                # 文字選取框
                pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                brush_color = QColor(0, 120, 215, 50)
                painter.setBrush(brush_color)
                rect = QRectF(start_pointf, end_pointf).normalized()
                painter.drawRect(rect)
            
            elif self.interaction_mode in ["highlight", "rectangle"]:
                pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                rect = QRectF(start_pointf, end_pointf).normalized()
                painter.drawRect(rect)
            
            elif self.interaction_mode == "circle":
                pen = QPen(QColor(0, 255, 0), 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                rect = QRectF(start_pointf, end_pointf).normalized()
                painter.drawEllipse(rect)
            
            elif self.interaction_mode == "freehand":
                pen = QPen(QColor(0, 0, 255), 2)
                painter.setPen(pen)
                painter.drawPath(self.drawing_path)
    
    def get_pixmap_offset(self):
        """獲取圖片在 QLabel 中的偏移量"""
        if not self.current_pixmap:
            return (0, 0)
        
        # 獲取顯示的 pixmap（已縮放）
        displayed_pixmap = self.pixmap()
        if not displayed_pixmap:
            return (0, 0)
        
        # QLabel 的大小
        label_width = self.width()
        label_height = self.height()
        
        # 顯示圖片的大小
        pixmap_width = displayed_pixmap.width()
        pixmap_height = displayed_pixmap.height()
        
        # 計算偏移（圖片居中顯示）
        offset_x = (label_width - pixmap_width) / 2
        offset_y = (label_height - pixmap_height) / 2
        
        return (max(0, offset_x), max(0, offset_y))
    
    def map_to_pdf_coordinates(self, point: QPoint) -> QPoint:
        """將螢幕座標映射到 PDF 座標"""
        if not self.current_pixmap:
            return point
        
        # 獲取圖片偏移
        offset_x, offset_y = self.get_pixmap_offset()
        
        # 減去偏移並考慮縮放比例
        pdf_x = int((point.x() - offset_x) / self.zoom_level)
        pdf_y = int((point.y() - offset_y) / self.zoom_level)
        return QPoint(max(0, pdf_x), max(0, pdf_y))
    
    def map_rect_to_pdf(self, rect: QRectF) -> QRectF:
        """將螢幕矩形映射到 PDF 矩形"""
        if not self.current_pixmap:
            return rect
        
        # 獲取圖片偏移
        offset_x, offset_y = self.get_pixmap_offset()
        
        # 減去偏移並考慮縮放比例
        pdf_rect = QRectF(
            (rect.x() - offset_x) / self.zoom_level,
            (rect.y() - offset_y) / self.zoom_level,
            rect.width() / self.zoom_level,
            rect.height() / self.zoom_level
        )
        return pdf_rect


class PDFViewer(QWidget):
    """PDF 檢視器主元件"""
    
    # 信號定義
    page_changed = pyqtSignal(int)
    zoom_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.page_count = 0
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 捲動區域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # PDF 頁面元件
        self.page_widget = PDFPageWidget()
        self.scroll_area.setWidget(self.page_widget)
        
        layout.addWidget(self.scroll_area)
    
    def display_page(self, pixmap: QPixmap, page_num: int, zoom: float = 1.0):
        """顯示頁面"""
        self.page_widget.set_pixmap(pixmap)
        self.page_widget.zoom_level = zoom  # 同步縮放級別
        self.current_page = page_num
        self.page_changed.emit(page_num)
    
    def clear(self):
        """清除顯示"""
        self.page_widget.clear()
        self.current_page = 0
        self.page_count = 0
    
    def zoom_in(self):
        """放大"""
        current_zoom = self.page_widget.get_zoom()
        new_zoom = min(current_zoom * 1.2, 5.0)  # 最大 500%
        self.set_zoom(new_zoom)
    
    def zoom_out(self):
        """縮小"""
        current_zoom = self.page_widget.get_zoom()
        new_zoom = max(current_zoom / 1.2, 0.1)  # 最小 10%
        self.set_zoom(new_zoom)
    
    def set_zoom(self, zoom: float):
        """設定縮放級別"""
        self.page_widget.set_zoom(zoom)
        self.zoom_changed.emit(zoom)
    
    def get_zoom(self) -> float:
        """獲取縮放級別"""
        return self.page_widget.get_zoom()
    
    def fit_to_width(self):
        """適應寬度"""
        if not self.page_widget.current_pixmap:
            return
        
        scroll_width = self.scroll_area.viewport().width()
        pixmap_width = self.page_widget.current_pixmap.width()
        
        if pixmap_width > 0:
            zoom = (scroll_width - 20) / pixmap_width  # 減去邊距
            self.set_zoom(zoom)
    
    def fit_to_page(self):
        """適應頁面"""
        if not self.page_widget.current_pixmap:
            return
        
        scroll_width = self.scroll_area.viewport().width()
        scroll_height = self.scroll_area.viewport().height()
        pixmap_width = self.page_widget.current_pixmap.width()
        pixmap_height = self.page_widget.current_pixmap.height()
        
        if pixmap_width > 0 and pixmap_height > 0:
            zoom_w = (scroll_width - 20) / pixmap_width
            zoom_h = (scroll_height - 20) / pixmap_height
            zoom = min(zoom_w, zoom_h)
            self.set_zoom(zoom)
    
    def set_interaction_mode(self, mode: str):
        """設定互動模式"""
        self.page_widget.set_interaction_mode(mode)
    
    def get_page_widget(self) -> PDFPageWidget:
        """獲取頁面元件"""
        return self.page_widget
    
    def rotate_left(self):
        """逆時針旋轉 90 度"""
        current_rotation = self.page_widget.rotation
        self.page_widget.set_rotation(current_rotation - 90)
    
    def rotate_right(self):
        """順時針旋轉 90 度"""
        current_rotation = self.page_widget.rotation
        self.page_widget.set_rotation(current_rotation + 90)

