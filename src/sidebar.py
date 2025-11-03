"""
側邊欄模組
提供縮圖、書籤和註解列表
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QListWidget,
                             QListWidgetItem, QLabel, QPushButton, QHBoxLayout,
                             QDialog, QLineEdit, QTextEdit, QDialogButtonBox,
                             QComboBox, QProgressBar, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon


class ThumbnailWidget(QWidget):
    """縮圖檢視"""
    
    page_selected = pyqtSignal(int)  # 頁面被選擇
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 縮圖列表
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumbnail_list.setIconSize(QSize(120, 150))
        self.thumbnail_list.setSpacing(10)
        self.thumbnail_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumbnail_list.itemClicked.connect(self.on_thumbnail_clicked)
        
        layout.addWidget(self.thumbnail_list)
    
    def add_thumbnail(self, page_num: int, pixmap):
        """新增縮圖"""
        item = QListWidgetItem(f"頁 {page_num + 1}")
        item.setIcon(QIcon(pixmap))
        item.setData(Qt.ItemDataRole.UserRole, page_num)
        self.thumbnail_list.addItem(item)
    
    def clear_thumbnails(self):
        """清除所有縮圖"""
        self.thumbnail_list.clear()
    
    def on_thumbnail_clicked(self, item: QListWidgetItem):
        """縮圖點擊事件"""
        page_num = item.data(Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.page_selected.emit(page_num)
    
    def set_current_page(self, page_num: int):
        """設定當前頁面"""
        for i in range(self.thumbnail_list.count()):
            item = self.thumbnail_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == page_num:
                self.thumbnail_list.setCurrentItem(item)
                break


class BookmarkWidget(QWidget):
    """書籤檢視"""
    
    bookmark_selected = pyqtSignal(int)  # 書籤被選擇，參數為頁碼
    add_bookmark_requested = pyqtSignal()  # 請求新增書籤
    delete_bookmark_requested = pyqtSignal(int)  # 請求刪除書籤
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 工具列
        toolbar_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("新增")
        self.add_btn.clicked.connect(self.add_bookmark_requested.emit)
        
        self.delete_btn = QPushButton("刪除")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addStretch()
        
        # 書籤列表
        self.bookmark_list = QListWidget()
        self.bookmark_list.itemDoubleClicked.connect(self.on_bookmark_double_clicked)
        
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.bookmark_list)
    
    def add_bookmark_item(self, title: str, page_num: int):
        """新增書籤項目"""
        item = QListWidgetItem(f"📑 {title} (頁 {page_num + 1})")
        item.setData(Qt.ItemDataRole.UserRole, page_num)
        self.bookmark_list.addItem(item)
    
    def clear_bookmarks(self):
        """清除所有書籤"""
        self.bookmark_list.clear()
    
    def on_bookmark_double_clicked(self, item: QListWidgetItem):
        """書籤雙擊事件"""
        page_num = item.data(Qt.ItemDataRole.UserRole)
        if page_num is not None:
            self.bookmark_selected.emit(page_num)
    
    def on_delete_clicked(self):
        """刪除按鈕點擊"""
        current_row = self.bookmark_list.currentRow()
        if current_row >= 0:
            self.delete_bookmark_requested.emit(current_row)
            self.bookmark_list.takeItem(current_row)


class AnnotationWidget(QWidget):
    """註解檢視"""
    
    annotation_selected = pyqtSignal(int, object)  # 註解被選擇
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 註解列表
        self.annotation_list = QListWidget()
        self.annotation_list.itemDoubleClicked.connect(self.on_annotation_double_clicked)
        
        layout.addWidget(QLabel("註解列表"))
        layout.addWidget(self.annotation_list)
    
    def add_annotation_item(self, page_num: int, annot_type: str, content: str = ""):
        """新增註解項目"""
        display_text = f"頁 {page_num + 1} - {annot_type}"
        if content:
            display_text += f": {content[:30]}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, (page_num, annot_type))
        self.annotation_list.addItem(item)
    
    def clear_annotations(self):
        """清除所有註解"""
        self.annotation_list.clear()
    
    def on_annotation_double_clicked(self, item: QListWidgetItem):
        """註解雙擊事件"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            page_num, annot_type = data
            self.annotation_selected.emit(page_num, annot_type)


class TranslationWidget(QWidget):
    """翻譯檢視"""
    
    # 信號定義
    translate_selected_requested = pyqtSignal(str, str)  # 翻譯選取文字 (from_lang, to_lang)
    translate_document_requested = pyqtSignal(str, str)  # 翻譯整份文件 (from_lang, to_lang)
    language_changed = pyqtSignal(str, str)  # 語言設定變更 (from_lang, to_lang)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_text = ""
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # 語言選擇區域
        lang_group = QGroupBox("語言設定")
        lang_layout = QVBoxLayout(lang_group)
        
        # 來源語言
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("來源語言:"))
        self.from_lang_combo = QComboBox()
        self.from_lang_combo.addItems([
            "自動偵測", "英文", "繁體中文", "簡體中文", 
            "日文", "韓文", "法文", "德文", "西班牙文"
        ])
        self.from_lang_combo.setCurrentText("英文")
        self.from_lang_combo.currentTextChanged.connect(self.on_language_changed)
        from_layout.addWidget(self.from_lang_combo)
        
        # 目標語言
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("目標語言:"))
        self.to_lang_combo = QComboBox()
        self.to_lang_combo.addItems([
            "繁體中文", "簡體中文", "英文", "日文", 
            "韓文", "法文", "德文", "西班牙文"
        ])
        self.to_lang_combo.setCurrentText("繁體中文")
        self.to_lang_combo.currentTextChanged.connect(self.on_language_changed)
        to_layout.addWidget(self.to_lang_combo)
        
        lang_layout.addLayout(from_layout)
        lang_layout.addLayout(to_layout)
        main_layout.addWidget(lang_group)
        
        # 操作按鈕
        button_layout = QHBoxLayout()
        
        self.translate_selected_btn = QPushButton("翻譯選取")
        self.translate_selected_btn.clicked.connect(self.on_translate_selected)
        self.translate_selected_btn.setEnabled(False)
        
        self.translate_doc_btn = QPushButton("翻譯文件")
        self.translate_doc_btn.clicked.connect(self.on_translate_document)
        
        button_layout.addWidget(self.translate_selected_btn)
        button_layout.addWidget(self.translate_doc_btn)
        main_layout.addLayout(button_layout)
        
        # 原文區域
        original_group = QGroupBox("原文")
        original_layout = QVBoxLayout(original_group)
        
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(False)  # 允許編輯
        self.original_text.setMaximumHeight(150)
        self.original_text.setPlaceholderText("選取 PDF 中的文字，或直接輸入要翻譯的文字...")
        
        # 當文字改變時，同步更新 selected_text 並啟用翻譯按鈕
        self.original_text.textChanged.connect(self.on_original_text_changed)
        
        original_layout.addWidget(self.original_text)
        main_layout.addWidget(original_group)
        
        # 譯文區域
        translation_group = QGroupBox("譯文")
        translation_layout = QVBoxLayout(translation_group)
        
        # 建立可捲動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)
        
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)
        self.translation_text.setPlaceholderText("翻譯結果將顯示在這裡...")
        
        scroll_area.setWidget(self.translation_text)
        translation_layout.addWidget(scroll_area)
        main_layout.addWidget(translation_group)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # 狀態標籤
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #666;")
        main_layout.addWidget(self.status_label)
        
        # 添加彈性空間
        main_layout.addStretch()
    
    def set_selected_text(self, text: str):
        """設定選取的文字"""
        self.selected_text = text
        # 使用 blockSignals 避免觸發 textChanged 信號
        self.original_text.blockSignals(True)
        self.original_text.setPlainText(text)
        self.original_text.blockSignals(False)
        self.translate_selected_btn.setEnabled(bool(text.strip()))
    
    def set_translation_result(self, text: str):
        """設定翻譯結果"""
        self.translation_text.setPlainText(text)
    
    def clear_translation(self):
        """清除翻譯結果"""
        self.translation_text.clear()
        self.status_label.clear()
    
    def show_progress(self, current: int, total: int):
        """顯示進度"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"翻譯中... ({current}/{total})")
    
    def hide_progress(self):
        """隱藏進度"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("翻譯完成")
    
    def show_error(self, message: str):
        """顯示錯誤訊息"""
        self.status_label.setText(f"錯誤: {message}")
        self.status_label.setStyleSheet("color: red;")
        self.progress_bar.setVisible(False)
    
    def on_translate_selected(self):
        """翻譯選取文字"""
        from_lang = self.from_lang_combo.currentText()
        to_lang = self.to_lang_combo.currentText()
        self.translate_selected_requested.emit(from_lang, to_lang)
    
    def on_translate_document(self):
        """翻譯整份文件"""
        from_lang = self.from_lang_combo.currentText()
        to_lang = self.to_lang_combo.currentText()
        self.translate_document_requested.emit(from_lang, to_lang)
    
    def on_language_changed(self):
        """語言設定變更"""
        from_lang = self.from_lang_combo.currentText()
        to_lang = self.to_lang_combo.currentText()
        self.language_changed.emit(from_lang, to_lang)
    
    def on_original_text_changed(self):
        """原文文字改變事件"""
        # 同步更新 selected_text
        self.selected_text = self.original_text.toPlainText()
        # 根據文字內容啟用/停用翻譯按鈕
        has_text = bool(self.selected_text.strip())
        self.translate_selected_btn.setEnabled(has_text)
    
    def enable_buttons(self, enabled: bool):
        """啟用/停用按鈕"""
        self.translate_doc_btn.setEnabled(enabled)
        if enabled and self.selected_text:
            self.translate_selected_btn.setEnabled(True)
        else:
            self.translate_selected_btn.setEnabled(False)


class Sidebar(QWidget):
    """側邊欄主元件"""
    
    page_selected = pyqtSignal(int)
    add_bookmark_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 建立分頁
        self.tab_widget = QTabWidget()
        
        # 縮圖分頁
        self.thumbnail_widget = ThumbnailWidget()
        self.thumbnail_widget.page_selected.connect(self.page_selected.emit)
        self.tab_widget.addTab(self.thumbnail_widget, "縮圖")
        
        # 書籤分頁
        self.bookmark_widget = BookmarkWidget()
        self.bookmark_widget.bookmark_selected.connect(self.page_selected.emit)
        self.bookmark_widget.add_bookmark_requested.connect(self.add_bookmark_requested.emit)
        self.tab_widget.addTab(self.bookmark_widget, "書籤")
        
        # 註解分頁
        self.annotation_widget = AnnotationWidget()
        self.annotation_widget.annotation_selected.connect(
            lambda page_num, _: self.page_selected.emit(page_num)
        )
        self.tab_widget.addTab(self.annotation_widget, "註解")
        
        # 翻譯分頁
        self.translation_widget = TranslationWidget()
        self.tab_widget.addTab(self.translation_widget, "翻譯")
        
        layout.addWidget(self.tab_widget)
    
    def get_thumbnail_widget(self) -> ThumbnailWidget:
        """獲取縮圖元件"""
        return self.thumbnail_widget
    
    def get_bookmark_widget(self) -> BookmarkWidget:
        """獲取書籤元件"""
        return self.bookmark_widget
    
    def get_annotation_widget(self) -> AnnotationWidget:
        """獲取註解元件"""
        return self.annotation_widget
    
    def get_translation_widget(self) -> TranslationWidget:
        """獲取翻譯元件"""
        return self.translation_widget


class AddBookmarkDialog(QDialog):
    """新增書籤對話框"""
    
    def __init__(self, current_page: int, parent=None):
        super().__init__(parent)
        self.current_page = current_page
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        self.setWindowTitle("新增書籤")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 標題輸入
        layout.addWidget(QLabel("書籤標題:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(f"頁面 {self.current_page + 1}")
        layout.addWidget(self.title_edit)
        
        # 描述輸入
        layout.addWidget(QLabel("描述 (可選):"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addWidget(self.description_edit)
        
        # 按鈕
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_bookmark_data(self):
        """獲取書籤資料"""
        title = self.title_edit.text() or f"頁面 {self.current_page + 1}"
        description = self.description_edit.toPlainText()
        return title, description

