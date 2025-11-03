"""
PDF 處理核心模組
負責 PDF 檔案的讀取、渲染和基本操作
"""

import fitz  # PyMuPDF
from typing import Optional, List, Tuple
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, pyqtSignal


class PDFHandler(QObject):
    """PDF 文件處理器"""
    
    # 信號定義
    document_loaded = pyqtSignal(int)  # 文件載入完成，參數為總頁數
    page_rendered = pyqtSignal(int, QPixmap)  # 頁面渲染完成
    error_occurred = pyqtSignal(str)  # 發生錯誤
    
    def __init__(self):
        super().__init__()
        self.document: Optional[fitz.Document] = None
        self.file_path: Optional[str] = None
        self.page_count: int = 0
        self.current_page: int = 0
        
    def open_document(self, file_path: str) -> bool:
        """
        開啟 PDF 文件
        
        Args:
            file_path: PDF 檔案路徑
            
        Returns:
            成功返回 True，失敗返回 False
        """
        try:
            if self.document:
                self.close_document()
            
            self.document = fitz.open(file_path)
            self.file_path = file_path
            self.page_count = len(self.document)
            self.current_page = 0
            
            self.document_loaded.emit(self.page_count)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"無法開啟 PDF 檔案: {str(e)}")
            return False
    
    def close_document(self):
        """關閉當前文件"""
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None
            self.page_count = 0
            self.current_page = 0
    
    def get_page(self, page_num: int) -> Optional[fitz.Page]:
        """
        獲取指定頁面
        
        Args:
            page_num: 頁碼（從 0 開始）
            
        Returns:
            頁面物件，如果頁面不存在則返回 None
        """
        if not self.document or page_num < 0 or page_num >= self.page_count:
            return None
        return self.document[page_num]
    
    def render_page(self, page_num: int, zoom: float = 1.0, rotation: int = 0) -> Optional[QPixmap]:
        """
        渲染指定頁面
        
        Args:
            page_num: 頁碼（從 0 開始）
            zoom: 縮放比例
            rotation: 旋轉角度（0, 90, 180, 270）
            
        Returns:
            QPixmap 物件，如果渲染失敗則返回 None
        """
        try:
            page = self.get_page(page_num)
            if not page:
                return None
            
            # 設定渲染矩陣（縮放和旋轉）
            mat = fitz.Matrix(zoom, zoom).prerotate(rotation)
            
            # 渲染頁面為像素圖
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # 轉換為 QImage
            img_format = QImage.Format.Format_RGB888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
            
            # 轉換為 QPixmap
            pixmap = QPixmap.fromImage(img)
            
            self.page_rendered.emit(page_num, pixmap)
            return pixmap
            
        except Exception as e:
            self.error_occurred.emit(f"渲染頁面失敗: {str(e)}")
            return None
    
    def render_thumbnail(self, page_num: int, max_size: int = 150) -> Optional[QPixmap]:
        """
        渲染縮圖
        
        Args:
            page_num: 頁碼
            max_size: 最大尺寸
            
        Returns:
            縮圖 QPixmap
        """
        page = self.get_page(page_num)
        if not page:
            return None
        
        # 計算縮放比例以適應最大尺寸
        rect = page.rect
        zoom = min(max_size / rect.width, max_size / rect.height)
        
        return self.render_page(page_num, zoom)
    
    def get_page_text(self, page_num: int) -> str:
        """獲取頁面文字"""
        page = self.get_page(page_num)
        if not page:
            return ""
        return page.get_text()
    
    def get_text_from_rect(self, page_num: int, rect) -> str:
        """
        從指定矩形區域獲取文字
        
        Args:
            page_num: 頁碼
            rect: 矩形區域 (QRectF 或 fitz.Rect)
            
        Returns:
            區域內的文字
        """
        page = self.get_page(page_num)
        if not page:
            return ""
        
        # 轉換 QRectF 為 fitz.Rect
        if hasattr(rect, 'x'):  # QRectF
            fitz_rect = fitz.Rect(rect.x(), rect.y(), 
                                 rect.x() + rect.width(), 
                                 rect.y() + rect.height())
        else:
            fitz_rect = rect
        
        # 使用 get_text 方法並指定 clip 區域，比 get_textbox 更準確
        try:
            # 使用 "text" 模式提取純文字，並限制在指定區域
            text = page.get_text("text", clip=fitz_rect)
            return text.strip() if text else ""
        except:
            # 如果失敗，回退到 get_textbox
            text = page.get_textbox(fitz_rect)
            return text.strip() if text else ""
    
    def get_text_words(self, page_num: int):
        """
        獲取頁面上所有文字及其位置（用於智能選取）
        
        Args:
            page_num: 頁碼
            
        Returns:
            文字區塊列表 [(x0, y0, x1, y1, word, block_no, line_no, word_no)]
        """
        page = self.get_page(page_num)
        if not page:
            return []
        
        # 使用 "words" 模式獲取每個單詞的位置
        words = page.get_text("words")
        return words
    
    def get_text_from_words(self, page_num: int, selected_words):
        """
        從選取的單詞列表提取文字
        
        Args:
            page_num: 頁碼
            selected_words: 選取的單詞列表 (from get_text("words"))
            
        Returns:
            組合的文字
        """
        if not selected_words:
            return ""
        
        # 按行和位置排序
        sorted_words = sorted(selected_words, key=lambda w: (w[5], w[6], w[7]))  # block_no, line_no, word_no
        
        # 組合文字
        result_parts = []
        prev_line = None
        
        for word_info in sorted_words:
            word = word_info[4]  # 文字內容
            line_no = word_info[6]  # 行號
            
            # 如果換行，添加空格分隔
            if prev_line is not None and line_no != prev_line:
                result_parts.append('\n')
            elif prev_line is not None:
                result_parts.append(' ')
            
            result_parts.append(word)
            prev_line = line_no
        
        return "".join(result_parts)
    
    def search_text(self, text: str, page_num: Optional[int] = None) -> List[Tuple[int, List]]:
        """
        搜尋文字
        
        Args:
            text: 搜尋的文字
            page_num: 指定頁面搜尋，None 表示搜尋全部頁面
            
        Returns:
            搜尋結果列表 [(頁碼, [矩形區域列表])]
        """
        if not self.document:
            return []
        
        results = []
        pages = [page_num] if page_num is not None else range(self.page_count)
        
        for pnum in pages:
            page = self.get_page(pnum)
            if page:
                rects = page.search_for(text)
                if rects:
                    results.append((pnum, rects))
        
        return results
    
    def get_toc(self) -> List:
        """獲取文件目錄（Table of Contents）"""
        if not self.document:
            return []
        return self.document.get_toc()
    
    def get_metadata(self) -> dict:
        """獲取文件元資料"""
        if not self.document:
            return {}
        return self.document.metadata
    
    def save_document(self, output_path: Optional[str] = None) -> bool:
        """
        儲存文件
        
        Args:
            output_path: 輸出路徑，None 表示覆蓋原檔案
            
        Returns:
            成功返回 True
        """
        if not self.document:
            return False
        
        try:
            save_path = output_path or self.file_path
            self.document.save(save_path)
            return True
        except Exception as e:
            self.error_occurred.emit(f"儲存文件失敗: {str(e)}")
            return False

