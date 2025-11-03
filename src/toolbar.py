"""
工具列模組
提供主要操作按鈕和工具
"""

from PyQt6.QtWidgets import (QToolBar, QWidget, QLabel, QSpinBox, QComboBox,
                             QHBoxLayout, QPushButton, QSlider, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon


class Toolbar(QToolBar):
    """主工具列"""
    
    # 信號定義
    open_file_requested = pyqtSignal()
    save_file_requested = pyqtSignal()
    print_requested = pyqtSignal()
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    zoom_fit_width = pyqtSignal()
    zoom_fit_page = pyqtSignal()
    zoom_changed = pyqtSignal(float)
    page_changed = pyqtSignal(int)
    rotate_left_requested = pyqtSignal()
    rotate_right_requested = pyqtSignal()
    search_requested = pyqtSignal(str)
    annotation_tool_selected = pyqtSignal(str)
    toggle_sidebar_requested = pyqtSignal()
    toggle_dark_mode = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        # 檔案操作
        self.open_action = QAction("開啟", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file_requested.emit)
        self.addAction(self.open_action)
        
        self.save_action = QAction("儲存", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file_requested.emit)
        self.addAction(self.save_action)
        
        self.print_action = QAction("列印", self)
        self.print_action.setShortcut("Ctrl+P")
        self.print_action.triggered.connect(self.print_requested.emit)
        self.addAction(self.print_action)
        
        self.addSeparator()
        
        # 頁面導航
        self.prev_page_action = QAction("上一頁", self)
        self.prev_page_action.triggered.connect(lambda: self.navigate_page(-1))
        self.addAction(self.prev_page_action)
        
        # 頁碼輸入
        page_widget = QWidget()
        page_layout = QHBoxLayout(page_widget)
        page_layout.setContentsMargins(5, 0, 5, 0)
        
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(1)
        self.page_spinbox.valueChanged.connect(lambda v: self.page_changed.emit(v - 1))
        
        self.page_label = QLabel("/ 1")
        
        page_layout.addWidget(QLabel("頁碼:"))
        page_layout.addWidget(self.page_spinbox)
        page_layout.addWidget(self.page_label)
        
        self.addWidget(page_widget)
        
        self.next_page_action = QAction("下一頁", self)
        self.next_page_action.triggered.connect(lambda: self.navigate_page(1))
        self.addAction(self.next_page_action)
        
        self.addSeparator()
        
        # 縮放控制
        self.zoom_out_action = QAction("縮小", self)
        self.zoom_out_action.triggered.connect(self.zoom_out_requested.emit)
        self.addAction(self.zoom_out_action)
        
        # 縮放比例選擇
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(5, 0, 5, 0)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems([
            "50%", "75%", "100%", "125%", "150%", "200%", "300%",
            "適應寬度", "適應頁面"
        ])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_combo_changed)
        
        zoom_layout.addWidget(self.zoom_combo)
        self.addWidget(zoom_widget)
        
        self.zoom_in_action = QAction("放大", self)
        self.zoom_in_action.triggered.connect(self.zoom_in_requested.emit)
        self.addAction(self.zoom_in_action)
        
        self.addSeparator()
        
        # 旋轉
        self.rotate_left_action = QAction("逆時針旋轉", self)
        self.rotate_left_action.triggered.connect(self.rotate_left_requested.emit)
        self.addAction(self.rotate_left_action)
        
        self.rotate_right_action = QAction("順時針旋轉", self)
        self.rotate_right_action.triggered.connect(self.rotate_right_requested.emit)
        self.addAction(self.rotate_right_action)
        
        self.addSeparator()
        
        # 側邊欄切換
        self.toggle_sidebar_action = QAction("側邊欄", self)
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(True)
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar_requested.emit)
        self.addAction(self.toggle_sidebar_action)
        
        # 深色模式
        self.dark_mode_action = QAction("深色模式", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode.emit)
        self.addAction(self.dark_mode_action)
    
    def navigate_page(self, delta: int):
        """頁面導航"""
        current = self.page_spinbox.value()
        new_value = current + delta
        if self.page_spinbox.minimum() <= new_value <= self.page_spinbox.maximum():
            self.page_spinbox.setValue(new_value)
    
    def set_page_count(self, count: int):
        """設定總頁數"""
        self.page_spinbox.setMaximum(max(1, count))
        self.page_label.setText(f"/ {count}")
    
    def set_current_page(self, page_num: int):
        """設定當前頁碼（從 0 開始）"""
        self.page_spinbox.blockSignals(True)
        self.page_spinbox.setValue(page_num + 1)
        self.page_spinbox.blockSignals(False)
    
    def on_zoom_combo_changed(self, text: str):
        """縮放比例變更"""
        if text == "適應寬度":
            self.zoom_fit_width.emit()
        elif text == "適應頁面":
            self.zoom_fit_page.emit()
        else:
            # 移除 % 符號並轉換為浮點數
            try:
                zoom = float(text.replace("%", "")) / 100.0
                self.zoom_changed.emit(zoom)
            except ValueError:
                pass
    
    def set_zoom_level(self, zoom: float):
        """設定縮放級別"""
        text = f"{int(zoom * 100)}%"
        index = self.zoom_combo.findText(text)
        if index >= 0:
            self.zoom_combo.blockSignals(True)
            self.zoom_combo.setCurrentIndex(index)
            self.zoom_combo.blockSignals(False)


class AnnotationToolbar(QToolBar):
    """註解工具列"""
    
    tool_selected = pyqtSignal(str)  # 工具被選擇
    color_changed = pyqtSignal(object)  # 顏色變更
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("註解工具")
        self.setMovable(False)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        # 建立按鈕群組（單選）
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # 選擇工具
        select_action = QAction("選擇", self)
        select_action.setCheckable(True)
        select_action.setChecked(True)
        select_action.triggered.connect(lambda: self.tool_selected.emit("select"))
        self.addAction(select_action)
        
        self.addSeparator()
        
        # 高亮工具
        highlight_action = QAction("高亮", self)
        highlight_action.setCheckable(True)
        highlight_action.triggered.connect(lambda: self.tool_selected.emit("highlight"))
        self.addAction(highlight_action)
        
        # 底線工具
        underline_action = QAction("底線", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(lambda: self.tool_selected.emit("underline"))
        self.addAction(underline_action)
        
        # 刪除線工具
        strikeout_action = QAction("刪除線", self)
        strikeout_action.setCheckable(True)
        strikeout_action.triggered.connect(lambda: self.tool_selected.emit("strikeout"))
        self.addAction(strikeout_action)
        
        self.addSeparator()
        
        # 文字註解
        text_action = QAction("文字註解", self)
        text_action.setCheckable(True)
        text_action.triggered.connect(lambda: self.tool_selected.emit("text"))
        self.addAction(text_action)
        
        # 手繪工具
        draw_action = QAction("手繪", self)
        draw_action.setCheckable(True)
        draw_action.triggered.connect(lambda: self.tool_selected.emit("freehand"))
        self.addAction(draw_action)
        
        self.addSeparator()
        
        # 圖形工具
        rectangle_action = QAction("矩形", self)
        rectangle_action.setCheckable(True)
        rectangle_action.triggered.connect(lambda: self.tool_selected.emit("rectangle"))
        self.addAction(rectangle_action)
        
        circle_action = QAction("圓形", self)
        circle_action.setCheckable(True)
        circle_action.triggered.connect(lambda: self.tool_selected.emit("circle"))
        self.addAction(circle_action)
        
        arrow_action = QAction("箭頭", self)
        arrow_action.setCheckable(True)
        arrow_action.triggered.connect(lambda: self.tool_selected.emit("arrow"))
        self.addAction(arrow_action)

