"""
PDF 檢視器模組
提供 PDF 頁面顯示和互動功能
"""

from PyQt6.QtWidgets import (QWidget, QScrollArea, QLabel, QVBoxLayout,
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QPointF, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QMouseEvent, QPen, QColor, QPainterPath, QBrush, QKeyEvent


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
        self.current_page_num = 0
        
        # 互動模式
        self.interaction_mode = "select"  # select, highlight, rectangle, etc.
        self.text_selection_mode = "rect"  # rect, point, range, smart
        self.is_drawing = False
        self.start_point = None
        self.end_point = None
        self.drawing_path = QPainterPath()
        
        # 文字選取
        self.is_selecting_text = False
        self.selection_rect = None
        self.selection_points = []  # 用於範圍選取模式
        
        # 智能文字選取
        self.page_words = []  # 頁面上的所有文字及位置
        self.selected_words = []  # 選取的文字列表
        self.hover_word_index = None  # 懸停的文字索引
        
        # 設定滑鼠追蹤（用於懸停效果）
        self.setMouseTracking(True)
        self.hover_point = None
        
        # PDF handler 參考（用於智能選取）
        self.pdf_handler = None
    
    def set_pixmap(self, pixmap: QPixmap):
        """設定顯示的圖片"""
        self.current_pixmap = pixmap
        self.update_display()
    
    def set_page_words(self, words, page_num):
        """設定頁面文字資訊（用於智能選取）"""
        self.page_words = words
        self.current_page_num = page_num
        self.selected_words = []
    
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
        self._update_cursor()
    
    def set_text_selection_mode(self, mode: str):
        """設定文字選取模式：rect, point, range, smart"""
        self.text_selection_mode = mode
        self.selection_points = []
        self.selected_words = []
        self.hover_word_index = None
        self._update_cursor()
        self.update()
    
    def _update_cursor(self):
        """更新滑鼠游標"""
        if self.interaction_mode == "select":
            if self.text_selection_mode == "rect":
                self.setCursor(Qt.CursorShape.CrossCursor)
            elif self.text_selection_mode == "point":
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            elif self.text_selection_mode == "range":
                self.setCursor(Qt.CursorShape.IBeamCursor)
            elif self.text_selection_mode == "smart":
                self.setCursor(Qt.CursorShape.IBeamCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.interaction_mode in ["highlight", "underline", "strikeout", "rectangle", "circle"]:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.interaction_mode == "freehand":
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.interaction_mode == "text":
            self.setCursor(Qt.CursorShape.IBeamCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """滑鼠按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            
            # 檢查是否為文字選取模式
            if self.interaction_mode == "select":
                if self.text_selection_mode == "point":
                    # 點擊選取模式：立即發射選取信號
                    self._handle_point_selection(event.pos())
                elif self.text_selection_mode == "range":
                    # 範圍選取模式：記錄點擊點
                    self._handle_range_selection(event.pos())
                elif self.text_selection_mode == "smart":
                    # 智能文字選取模式
                    self._handle_smart_selection_start(event.pos())
                elif self.text_selection_mode == "rect":
                    # 矩形選取模式：傳統拖曳方式
                    self.is_drawing = True
                    self.is_selecting_text = True
                    self.selection_rect = None
            else:
                self.is_drawing = True
            
            if self.interaction_mode == "freehand":
                self.drawing_path = QPainterPath()
                self.drawing_path.moveTo(self.start_point)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """滑鼠移動事件"""
        if self.is_drawing and self.start_point:
            self.end_point = event.pos()
            
            if self.interaction_mode == "freehand":
                self.drawing_path.lineTo(self.end_point)
            
            # 智能選取：拖曳擴展選取
            if self.interaction_mode == "select" and self.text_selection_mode == "smart":
                self._handle_smart_selection_move(event.pos())
            
            self.update()
        
        # 範圍選取模式：顯示預覽
        if self.interaction_mode == "select" and self.text_selection_mode == "range":
            if len(self.selection_points) == 1:
                self.hover_point = event.pos()
                self.update()
        
        # 智能選取模式：顯示懸停文字高亮
        if self.interaction_mode == "select" and self.text_selection_mode == "smart" and not self.is_drawing:
            self._update_hover_word(event.pos())
    
    def keyPressEvent(self, event):
        """鍵盤事件"""
        # ESC 鍵取消範圍選取
        if event.key() == Qt.Key.Key_Escape:
            if self.selection_points:
                self.selection_points = []
                self.hover_point = None
                self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """滑鼠釋放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False
            
            if self.interaction_mode == "text":
                self.point_clicked.emit(self.map_to_pdf_coordinates(self.start_point))
            elif self.interaction_mode == "select" and self.text_selection_mode == "smart":
                # 智能文字選取完成
                if self.selected_words and self.pdf_handler:
                    # 從選取的文字提取內容
                    from PyQt6.QtCore import pyqtSignal
                    # 發射帶有文字列表的信號
                    # 由於 text_selected 期望 QRectF，我們創建一個包含所有文字的矩形
                    if self.selected_words:
                        # 計算所有選取文字的邊界矩形
                        all_x0 = min(w[0] for w in self.selected_words)
                        all_y0 = min(w[1] for w in self.selected_words)
                        all_x1 = max(w[2] for w in self.selected_words)
                        all_y1 = max(w[3] for w in self.selected_words)
                        
                        bounding_rect = QRectF(all_x0, all_y0, all_x1 - all_x0, all_y1 - all_y0)
                        self.text_selected.emit(bounding_rect)
                self.is_selecting_text = False
            elif self.interaction_mode == "select" and self.is_selecting_text:
                # 文字選取模式（矩形）
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
    
    def _word_rect_to_screen(self, word_info):
        """將文字矩形從 PDF 座標轉換為螢幕座標"""
        x0, y0, x1, y1 = word_info[0], word_info[1], word_info[2], word_info[3]
        
        # 獲取圖片偏移
        offset_x, offset_y = self.get_pixmap_offset()
        
        # 轉換為螢幕座標
        screen_x0 = x0 * self.zoom_level + offset_x
        screen_y0 = y0 * self.zoom_level + offset_y
        screen_x1 = x1 * self.zoom_level + offset_x
        screen_y1 = y1 * self.zoom_level + offset_y
        
        return QRectF(screen_x0, screen_y0, screen_x1 - screen_x0, screen_y1 - screen_y0)
    
    def paintEvent(self, event):
        """繪製事件"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 繪製智能選取的文字高亮
        if self.interaction_mode == "select" and self.text_selection_mode == "smart":
            # 繪製選取的文字
            if self.selected_words:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 120, 215, 80))  # 淺藍色半透明
                
                for word_info in self.selected_words:
                    rect = self._word_rect_to_screen(word_info)
                    painter.drawRect(rect)
            
            # 繪製懸停的文字（如果沒有正在選取）
            if not self.is_drawing and self.hover_word_index is not None and self.hover_word_index < len(self.page_words):
                painter.setBrush(QColor(0, 120, 215, 40))  # 更淺的藍色
                word_info = self.page_words[self.hover_word_index]
                rect = self._word_rect_to_screen(word_info)
                painter.drawRect(rect)
        
        # 繪製範圍選取的第一個點和預覽線
        if self.interaction_mode == "select" and self.text_selection_mode == "range":
            if len(self.selection_points) >= 1:
                # 繪製第一個點
                first_point = self.selection_points[0]
                pen = QPen(QColor(0, 120, 215), 3)
                painter.setPen(pen)
                painter.setBrush(QColor(0, 120, 215))
                painter.drawEllipse(first_point, 5, 5)
                
                # 如果有懸停點，繪製預覽矩形
                if self.hover_point:
                    pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine)
                    painter.setPen(pen)
                    brush_color = QColor(0, 120, 215, 30)
                    painter.setBrush(brush_color)
                    start_pointf = QPointF(first_point)
                    end_pointf = QPointF(self.hover_point)
                    rect = QRectF(start_pointf, end_pointf).normalized()
                    painter.drawRect(rect)
                    
                    # 顯示提示文字
                    painter.setPen(QColor(0, 120, 215))
                    painter.drawText(self.hover_point.x() + 10, self.hover_point.y() - 10, "點擊確定範圍")
        
        # 繪製選取框或繪圖
        if self.is_drawing and self.start_point and self.end_point:
            # 轉換 QPoint 為 QPointF
            start_pointf = QPointF(self.start_point)
            end_pointf = QPointF(self.end_point)
            
            if self.interaction_mode == "select" and self.is_selecting_text:
                # 文字選取框（矩形模式）
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
    
    def _handle_point_selection(self, point: QPoint):
        """處理點擊選取模式"""
        # 將點擊點轉換為 PDF 座標
        pdf_point = self.map_to_pdf_coordinates(point)
        
        # 創建一個小矩形區域（例如 50x20 像素）
        width = 200  # PDF 座標
        height = 30
        
        rect = QRectF(
            pdf_point.x() - width/2,
            pdf_point.y() - height/2,
            width,
            height
        )
        
        # 發射文字選取信號
        self.text_selected.emit(rect)
        self.update()
    
    def _handle_range_selection(self, point: QPoint):
        """處理範圍選取模式（點擊兩次定義範圍）"""
        self.selection_points.append(point)
        
        if len(self.selection_points) == 2:
            # 兩個點都已選擇，創建矩形
            start_pointf = QPointF(self.selection_points[0])
            end_pointf = QPointF(self.selection_points[1])
            rect = QRectF(start_pointf, end_pointf).normalized()
            pdf_rect = self.map_rect_to_pdf(rect)
            
            # 發射選取信號
            self.text_selected.emit(pdf_rect)
            
            # 重置選取點
            self.selection_points = []
        
        self.update()
    
    def _find_word_at_position(self, point: QPoint):
        """找到滑鼠位置對應的文字"""
        if not self.page_words:
            return None
        
        # 轉換為 PDF 座標
        pdf_point = self.map_to_pdf_coordinates(point)
        
        # 遍歷所有文字，找到包含此點的文字
        for i, word_info in enumerate(self.page_words):
            x0, y0, x1, y1 = word_info[0], word_info[1], word_info[2], word_info[3]
            if x0 <= pdf_point.x() <= x1 and y0 <= pdf_point.y() <= y1:
                return i
        
        return None
    
    def _handle_smart_selection_start(self, point: QPoint):
        """處理智能選取開始"""
        # 找到點擊的文字
        word_index = self._find_word_at_position(point)
        if word_index is not None:
            self.selected_words = [self.page_words[word_index]]
            self.is_drawing = True
            self.is_selecting_text = True
            self.update()
    
    def _handle_smart_selection_move(self, point: QPoint):
        """處理智能選取拖曳"""
        if not self.selected_words or not self.page_words:
            return
        
        # 找到當前懸停的文字
        current_word_index = self._find_word_at_position(point)
        if current_word_index is None:
            return
        
        # 找到第一個選取的文字索引
        first_word = self.selected_words[0]
        first_index = self.page_words.index(first_word) if first_word in self.page_words else 0
        
        # 選取從第一個文字到當前文字之間的所有文字
        if current_word_index >= first_index:
            self.selected_words = self.page_words[first_index:current_word_index + 1]
        else:
            self.selected_words = self.page_words[current_word_index:first_index + 1]
        
        self.update()
    
    def _update_hover_word(self, point: QPoint):
        """更新懸停文字高亮"""
        word_index = self._find_word_at_position(point)
        if word_index != self.hover_word_index:
            self.hover_word_index = word_index
            self.update()


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

