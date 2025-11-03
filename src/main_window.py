"""
主視窗模組
整合所有功能的主應用程式視窗
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QInputDialog, QDockWidget,
                             QPushButton, QDialog, QTextEdit, QDialogButtonBox,
                             QLabel, QLineEdit, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence
import fitz

from .pdf_handler import PDFHandler
from .pdf_viewer import PDFViewer
from .toolbar import Toolbar, AnnotationToolbar
from .sidebar import Sidebar, AddBookmarkDialog
from .annotation import AnnotationManager
from .bookmark import BookmarkManager
from .form_editor import FormEditor
from .signature import SignatureManager
from .translator import TranslationManager
from .utils import Config


class SearchDialog(QDialog):
    """搜尋對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("搜尋文字")
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("搜尋:"))
        self.search_edit = QLineEdit()
        layout.addWidget(self.search_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_search_text(self) -> str:
        """獲取搜尋文字"""
        return self.search_edit.text()


class TextAnnotationDialog(QDialog):
    """文字註解對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增文字註解")
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("註解內容:"))
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(150)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_text(self) -> str:
        """獲取文字"""
        return self.text_edit.toPlainText()


class MainWindow(QMainWindow):
    """主視窗"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 閱讀器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化核心元件
        self.config = Config()
        self.pdf_handler = PDFHandler()
        self.annotation_manager = AnnotationManager(self.pdf_handler)
        self.bookmark_manager = BookmarkManager()
        self.form_editor = FormEditor(self.pdf_handler)
        self.signature_manager = SignatureManager(self.pdf_handler)
        self.translation_manager = TranslationManager(use_offline=False)  # 預設線上模式（可自動快取）
        
        # 當前狀態
        self.current_file = None
        self.current_page = 0
        self.current_zoom = 1.0
        
        # 建立 UI
        self.setup_ui()
        self.setup_menu()
        self.connect_signals()
        
        # 載入設定
        self.load_settings()
    
    def setup_ui(self):
        """設定 UI"""
        # 中央元件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 側邊欄
        self.sidebar = Sidebar()
        self.sidebar.setMaximumWidth(250)
        main_layout.addWidget(self.sidebar)
        
        # PDF 檢視器
        self.pdf_viewer = PDFViewer()
        main_layout.addWidget(self.pdf_viewer, 1)
        
        # 工具列
        self.toolbar = Toolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # 註解工具列
        self.annotation_toolbar = AnnotationToolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.annotation_toolbar)
        self.annotation_toolbar.hide()  # 預設隱藏
        
        # 狀態列
        self.statusBar().showMessage("就緒")
    
    def setup_menu(self):
        """設定選單"""
        menubar = self.menuBar()
        
        # 檔案選單
        file_menu = menubar.addMenu("檔案")
        
        open_action = QAction("開啟...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("儲存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存新檔...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("列印...", self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.triggered.connect(self.print_document)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("結束", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 編輯選單
        edit_menu = menubar.addMenu("編輯")
        
        search_action = QAction("搜尋...", self)
        search_action.setShortcut(QKeySequence.StandardKey.Find)
        search_action.triggered.connect(self.search_text)
        edit_menu.addAction(search_action)
        
        # 檢視選單
        view_menu = menubar.addMenu("檢視")
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("縮小", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("全螢幕", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 工具選單
        tools_menu = menubar.addMenu("工具")
        
        annotation_action = QAction("註解工具", self)
        annotation_action.triggered.connect(self.toggle_annotation_toolbar)
        tools_menu.addAction(annotation_action)
        
        bookmark_action = QAction("新增書籤", self)
        bookmark_action.setShortcut("Ctrl+B")
        bookmark_action.triggered.connect(self.add_bookmark)
        tools_menu.addAction(bookmark_action)
        
        form_action = QAction("表單編輯", self)
        form_action.triggered.connect(self.edit_form)
        tools_menu.addAction(form_action)
        
        signature_action = QAction("新增簽章", self)
        signature_action.triggered.connect(self.add_signature)
        tools_menu.addAction(signature_action)
        
        tools_menu.addSeparator()
        
        # 翻譯選單
        translate_selected_action = QAction("翻譯選取文字", self)
        translate_selected_action.setShortcut("Ctrl+T")
        translate_selected_action.triggered.connect(self.translate_selected_text)
        tools_menu.addAction(translate_selected_action)
        
        translate_page_action = QAction("翻譯目前頁面", self)
        translate_page_action.triggered.connect(self.translate_current_page)
        tools_menu.addAction(translate_page_action)
        
        translate_doc_action = QAction("翻譯整份文件", self)
        translate_doc_action.triggered.connect(self.translate_document)
        tools_menu.addAction(translate_doc_action)
        
        # 說明選單
        help_menu = menubar.addMenu("說明")
        
        about_action = QAction("關於", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """連接信號"""
        # PDF 處理器信號
        self.pdf_handler.document_loaded.connect(self.on_document_loaded)
        self.pdf_handler.error_occurred.connect(self.show_error)
        
        # 工具列信號
        self.toolbar.open_file_requested.connect(self.open_file)
        self.toolbar.save_file_requested.connect(self.save_file)
        self.toolbar.print_requested.connect(self.print_document)
        self.toolbar.zoom_in_requested.connect(self.zoom_in)
        self.toolbar.zoom_out_requested.connect(self.zoom_out)
        self.toolbar.zoom_fit_width.connect(self.pdf_viewer.fit_to_width)
        self.toolbar.zoom_fit_page.connect(self.pdf_viewer.fit_to_page)
        self.toolbar.zoom_changed.connect(self.pdf_viewer.set_zoom)
        self.toolbar.page_changed.connect(self.goto_page)
        self.toolbar.rotate_left_requested.connect(self.rotate_left)
        self.toolbar.rotate_right_requested.connect(self.rotate_right)
        self.toolbar.toggle_sidebar_requested.connect(self.toggle_sidebar)
        self.toolbar.toggle_dark_mode.connect(self.toggle_dark_mode)
        
        # 註解工具列信號
        self.annotation_toolbar.tool_selected.connect(self.on_annotation_tool_selected)
        
        # 側邊欄信號
        self.sidebar.page_selected.connect(self.goto_page)
        self.sidebar.add_bookmark_requested.connect(self.add_bookmark)
        
        # PDF 檢視器信號
        self.pdf_viewer.page_changed.connect(self.on_page_changed)
        self.pdf_viewer.zoom_changed.connect(self.on_zoom_changed)
        
        # 頁面元件信號
        page_widget = self.pdf_viewer.get_page_widget()
        page_widget.area_selected.connect(self.on_area_selected)
        page_widget.point_clicked.connect(self.on_point_clicked)
        page_widget.text_selected.connect(self.on_text_selected)
        
        # 書籤管理器信號
        self.bookmark_manager.bookmark_added.connect(self.on_bookmark_added)
        
        # 翻譯元件信號
        translation_widget = self.sidebar.get_translation_widget()
        translation_widget.translate_selected_requested.connect(self.on_translate_selected_requested)
        translation_widget.translate_document_requested.connect(self.on_translate_document_requested)
        
        # 翻譯管理器信號
        self.translation_manager.translation_ready.connect(self.on_translation_ready)
        self.translation_manager.error_occurred.connect(self.on_translation_error)
    
    def open_file(self):
        """開啟檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "開啟 PDF 檔案", "", "PDF 檔案 (*.pdf)"
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path: str):
        """載入 PDF"""
        if self.pdf_handler.open_document(file_path):
            self.current_file = file_path
            self.config.add_recent_file(file_path)
            self.setWindowTitle(f"PDF 閱讀器 - {file_path}")
            self.statusBar().showMessage(f"已開啟: {file_path}")
    
    def on_document_loaded(self, page_count: int):
        """文件載入完成"""
        self.toolbar.set_page_count(page_count)
        self.current_page = 0
        
        # 載入第一頁
        self.goto_page(0)
        
        # 生成縮圖
        self.generate_thumbnails()
        
        # 載入表單欄位
        self.form_editor.load_form_fields()
    
    def generate_thumbnails(self):
        """生成縮圖"""
        thumbnail_widget = self.sidebar.get_thumbnail_widget()
        thumbnail_widget.clear_thumbnails()
        
        for page_num in range(self.pdf_handler.page_count):
            pixmap = self.pdf_handler.render_thumbnail(page_num)
            if pixmap:
                thumbnail_widget.add_thumbnail(page_num, pixmap)
    
    def goto_page(self, page_num: int):
        """跳轉到指定頁面"""
        if 0 <= page_num < self.pdf_handler.page_count:
            pixmap = self.pdf_handler.render_page(page_num, self.current_zoom)
            if pixmap:
                self.pdf_viewer.display_page(pixmap, page_num, self.current_zoom)
                self.current_page = page_num
                self.toolbar.set_current_page(page_num)
                self.sidebar.get_thumbnail_widget().set_current_page(page_num)
    
    def on_page_changed(self, page_num: int):
        """頁面變更事件"""
        self.current_page = page_num
        self.statusBar().showMessage(
            f"頁面 {page_num + 1} / {self.pdf_handler.page_count}"
        )
    
    def on_zoom_changed(self, zoom: float):
        """縮放變更事件"""
        self.current_zoom = zoom
        self.toolbar.set_zoom_level(zoom)
        # 重新渲染當前頁面
        pixmap = self.pdf_handler.render_page(self.current_page, zoom)
        if pixmap:
            self.pdf_viewer.page_widget.set_pixmap(pixmap)
    
    def zoom_in(self):
        """放大"""
        self.pdf_viewer.zoom_in()
    
    def zoom_out(self):
        """縮小"""
        self.pdf_viewer.zoom_out()
    
    def rotate_left(self):
        """逆時針旋轉"""
        self.pdf_viewer.rotate_left()
        # TODO: 重新渲染頁面
    
    def rotate_right(self):
        """順時針旋轉"""
        self.pdf_viewer.rotate_right()
        # TODO: 重新渲染頁面
    
    def save_file(self):
        """儲存檔案"""
        if self.current_file:
            if self.pdf_handler.save_document():
                self.statusBar().showMessage("已儲存")
                QMessageBox.information(self, "成功", "檔案已儲存")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """另存新檔"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存 PDF 檔案", "", "PDF 檔案 (*.pdf)"
        )
        
        if file_path:
            if self.pdf_handler.save_document(file_path):
                self.current_file = file_path
                self.statusBar().showMessage(f"已儲存: {file_path}")
                QMessageBox.information(self, "成功", "檔案已儲存")
    
    def print_document(self):
        """列印文件"""
        QMessageBox.information(self, "列印", "列印功能開發中...")
    
    def search_text(self):
        """搜尋文字"""
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            search_text = dialog.get_search_text()
            if search_text:
                results = self.pdf_handler.search_text(search_text)
                if results:
                    # 跳轉到第一個結果
                    first_page, rects = results[0]
                    self.goto_page(first_page)
                    self.statusBar().showMessage(
                        f"找到 {len(results)} 個結果"
                    )
                else:
                    QMessageBox.information(self, "搜尋", "找不到相符的內容")
    
    def add_bookmark(self):
        """新增書籤"""
        dialog = AddBookmarkDialog(self.current_page, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, description = dialog.get_bookmark_data()
            self.bookmark_manager.add_bookmark(title, self.current_page, description)
    
    def on_bookmark_added(self, bookmark):
        """書籤新增事件"""
        bookmark_widget = self.sidebar.get_bookmark_widget()
        bookmark_widget.add_bookmark_item(bookmark.title, bookmark.page_num)
        self.statusBar().showMessage("已新增書籤")
    
    def on_annotation_tool_selected(self, tool: str):
        """註解工具被選擇"""
        self.annotation_manager.set_tool(tool)
        self.pdf_viewer.set_interaction_mode(tool)
        self.statusBar().showMessage(f"當前工具: {tool}")
    
    def on_area_selected(self, rect):
        """區域被選擇"""
        tool = self.annotation_manager.current_tool
        
        if not tool:
            return
        
        # 將 QRectF 轉換為 fitz.Rect
        fitz_rect = fitz.Rect(rect.x(), rect.y(), 
                              rect.x() + rect.width(), 
                              rect.y() + rect.height())
        
        if tool == "highlight":
            self.annotation_manager.add_highlight(self.current_page, fitz_rect)
            self.statusBar().showMessage("已新增高亮")
        elif tool == "underline":
            self.annotation_manager.add_underline(self.current_page, fitz_rect)
            self.statusBar().showMessage("已新增底線")
        elif tool == "strikeout":
            self.annotation_manager.add_strikeout(self.current_page, fitz_rect)
            self.statusBar().showMessage("已新增刪除線")
        elif tool == "rectangle":
            self.annotation_manager.add_rectangle(self.current_page, fitz_rect)
            self.statusBar().showMessage("已新增矩形")
        elif tool == "circle":
            self.annotation_manager.add_circle(self.current_page, fitz_rect)
            self.statusBar().showMessage("已新增圓形")
        
        # 重新渲染頁面以顯示註解
        QTimer.singleShot(100, lambda: self.goto_page(self.current_page))
    
    def on_point_clicked(self, point):
        """點擊位置"""
        tool = self.annotation_manager.current_tool
        
        if tool == "text":
            dialog = TextAnnotationDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                text = dialog.get_text()
                if text:
                    fitz_point = fitz.Point(point.x(), point.y())
                    self.annotation_manager.add_text_annotation(
                        self.current_page, fitz_point, text
                    )
                    self.statusBar().showMessage("已新增文字註解")
                    # 重新渲染頁面
                    QTimer.singleShot(100, lambda: self.goto_page(self.current_page))
    
    def toggle_annotation_toolbar(self):
        """切換註解工具列"""
        if self.annotation_toolbar.isVisible():
            self.annotation_toolbar.hide()
        else:
            self.annotation_toolbar.show()
    
    def toggle_sidebar(self):
        """切換側邊欄"""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def toggle_fullscreen(self):
        """切換全螢幕"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def toggle_dark_mode(self, enabled: bool):
        """切換深色模式"""
        self.config.set_dark_mode(enabled)
        if enabled:
            QApplication.instance().setStyleSheet(self.get_dark_stylesheet())
        else:
            QApplication.instance().setStyleSheet("")
        self.statusBar().showMessage("深色模式: " + ("開啟" if enabled else "關閉"))
    
    def get_dark_stylesheet(self) -> str:
        """獲取深色樣式表"""
        return """
        QMainWindow, QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }
        QMenu {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QMenu::item:selected {
            background-color: #4a4a4a;
        }
        QToolBar {
            background-color: #3c3c3c;
            border: none;
        }
        QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QListWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #5a5a5a;
        }
        QScrollBar:vertical {
            background-color: #3c3c3c;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            border-radius: 6px;
        }
        """
    
    def edit_form(self):
        """編輯表單"""
        fields = self.form_editor.form_fields
        if not fields:
            QMessageBox.information(self, "表單", "此 PDF 沒有表單欄位")
            return
        
        QMessageBox.information(
            self, "表單編輯", 
            f"找到 {len(fields)} 個表單欄位\n表單編輯功能開發中..."
        )
    
    def add_signature(self):
        """新增簽章"""
        text, ok = QInputDialog.getText(self, "簽章", "輸入簽章文字:")
        if ok and text:
            # 在當前頁面中心新增簽章
            page = self.pdf_handler.get_page(self.current_page)
            if page:
                rect = page.rect
                sig_rect = fitz.Rect(
                    rect.width / 2 - 100,
                    rect.height / 2 - 50,
                    rect.width / 2 + 100,
                    rect.height / 2 + 50
                )
                self.signature_manager.add_visual_signature(
                    self.current_page, sig_rect, text
                )
                self.statusBar().showMessage("已新增簽章")
                # 重新渲染頁面
                QTimer.singleShot(100, lambda: self.goto_page(self.current_page))
    
    def show_about(self):
        """顯示關於對話框"""
        QMessageBox.about(
            self, "關於 PDF 閱讀器",
            "<h2>PDF 閱讀器 v1.0</h2>"
            "<p>一個功能完整的 PDF 閱讀器應用程式</p>"
            "<p>使用 PyQt6 和 PyMuPDF 開發</p>"
            "<p>功能包括:</p>"
            "<ul>"
            "<li>PDF 檢視和導航</li>"
            "<li>註解工具</li>"
            "<li>書籤管理</li>"
            "<li>表單填寫</li>"
            "<li>數位簽章</li>"
            "</ul>"
        )
    
    def show_error(self, message: str):
        """顯示錯誤訊息"""
        QMessageBox.critical(self, "錯誤", message)
        self.statusBar().showMessage(f"錯誤: {message}")
    
    def load_settings(self):
        """載入設定"""
        # 載入視窗幾何
        geometry = self.config.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        # 載入視窗狀態
        state = self.config.get_window_state()
        if state:
            self.restoreState(state)
        
        # 載入深色模式
        dark_mode = self.config.get_dark_mode()
        self.toolbar.dark_mode_action.setChecked(dark_mode)
        if dark_mode:
            self.toggle_dark_mode(True)
    
    def save_settings(self):
        """儲存設定"""
        self.config.set_window_geometry(self.saveGeometry())
        self.config.set_window_state(self.saveState())
        self.config.set_zoom_level(self.current_zoom)
    
    def on_text_selected(self, rect):
        """文字被選取事件"""
        # 提取選取區域的文字
        text = self.pdf_handler.get_text_from_rect(self.current_page, rect)
        if text:
            # 更新翻譯面板的原文
            translation_widget = self.sidebar.get_translation_widget()
            translation_widget.set_selected_text(text)
            
            # 切換到翻譯分頁
            self.sidebar.tab_widget.setCurrentWidget(translation_widget)
            
            self.statusBar().showMessage(f"已選取 {len(text)} 個字元")
    
    def translate_selected_text(self):
        """翻譯選取的文字"""
        translation_widget = self.sidebar.get_translation_widget()
        if translation_widget.selected_text:
            # 切換到翻譯分頁
            self.sidebar.tab_widget.setCurrentWidget(translation_widget)
            # 觸發翻譯
            translation_widget.on_translate_selected()
        else:
            QMessageBox.information(self, "翻譯", "請先選取要翻譯的文字")
    
    def translate_current_page(self):
        """翻譯目前頁面"""
        if not self.pdf_handler.document:
            QMessageBox.information(self, "翻譯", "請先開啟 PDF 文件")
            return
        
        # 獲取目前頁面的文字
        text = self.pdf_handler.get_page_text(self.current_page)
        if not text.strip():
            QMessageBox.information(self, "翻譯", "目前頁面沒有文字")
            return
        
        # 更新翻譯面板
        translation_widget = self.sidebar.get_translation_widget()
        translation_widget.set_selected_text(text)
        
        # 切換到翻譯分頁
        self.sidebar.tab_widget.setCurrentWidget(translation_widget)
        
        # 自動開始翻譯
        translation_widget.on_translate_selected()
    
    def translate_document(self):
        """翻譯整份文件"""
        if not self.pdf_handler.document:
            QMessageBox.information(self, "翻譯", "請先開啟 PDF 文件")
            return
        
        # 確認對話框
        reply = QMessageBox.question(
            self, "翻譯整份文件",
            f"確定要翻譯整份文件嗎？（共 {self.pdf_handler.page_count} 頁）\n"
            "這可能需要較長時間。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # 切換到翻譯分頁
        translation_widget = self.sidebar.get_translation_widget()
        self.sidebar.tab_widget.setCurrentWidget(translation_widget)
        
        # 觸發翻譯
        translation_widget.on_translate_document()
    
    def on_translate_selected_requested(self, from_lang: str, to_lang: str):
        """處理翻譯選取文字請求"""
        translation_widget = self.sidebar.get_translation_widget()
        text = translation_widget.selected_text
        
        if not text.strip():
            translation_widget.show_error("沒有要翻譯的文字")
            return
        
        # 清除之前的翻譯結果
        translation_widget.clear_translation()
        translation_widget.enable_buttons(False)
        
        # 獲取語言代碼
        from_code = self.translation_manager.get_language_code(from_lang)
        to_code = self.translation_manager.get_language_code(to_lang)
        
        # 執行翻譯
        self.statusBar().showMessage("翻譯中...")
        translated = self.translation_manager.translate(text, from_code, to_code)
        
        # 顯示結果
        translation_widget.set_translation_result(translated)
        translation_widget.enable_buttons(True)
        translation_widget.hide_progress()
        self.statusBar().showMessage("翻譯完成")
    
    def on_translate_document_requested(self, from_lang: str, to_lang: str):
        """處理翻譯整份文件請求"""
        if not self.pdf_handler.document:
            return
        
        translation_widget = self.sidebar.get_translation_widget()
        translation_widget.clear_translation()
        translation_widget.enable_buttons(False)
        
        # 收集所有頁面的文字
        texts = []
        for page_num in range(self.pdf_handler.page_count):
            page_text = self.pdf_handler.get_page_text(page_num)
            texts.append(page_text)
        
        # 獲取語言代碼
        from_code = self.translation_manager.get_language_code(from_lang)
        to_code = self.translation_manager.get_language_code(to_lang)
        
        # 使用批次翻譯
        self.statusBar().showMessage("開始翻譯文件...")
        self.translation_manager.translate_batch(
            texts, from_code, to_code,
            callback=translation_widget.show_progress
        )
    
    def on_translation_ready(self, translated_text: str):
        """翻譯完成"""
        translation_widget = self.sidebar.get_translation_widget()
        translation_widget.set_translation_result(translated_text)
        translation_widget.enable_buttons(True)
        translation_widget.hide_progress()
        self.statusBar().showMessage("翻譯完成")
    
    def on_translation_error(self, error_message: str):
        """翻譯錯誤"""
        translation_widget = self.sidebar.get_translation_widget()
        translation_widget.show_error(error_message)
        translation_widget.enable_buttons(True)
        self.statusBar().showMessage(f"翻譯錯誤: {error_message}")
    
    def closeEvent(self, event):
        """關閉事件"""
        self.save_settings()
        
        # 停止翻譯工作
        if self.translation_manager.translation_worker:
            if self.translation_manager.translation_worker.isRunning():
                self.translation_manager.translation_worker.quit()
                self.translation_manager.translation_worker.wait()
        
        # 關閉文件
        if self.pdf_handler.document:
            self.pdf_handler.close_document()
        
        event.accept()

