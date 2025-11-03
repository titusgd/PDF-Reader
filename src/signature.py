"""
數位簽章模組
提供 PDF 數位簽章功能
"""

import fitz
from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime


class SignatureInfo:
    """簽章資訊類別"""
    
    def __init__(self, page_num: int, rect: fitz.Rect, signer: str, reason: str = "", location: str = ""):
        self.page_num = page_num
        self.rect = rect
        self.signer = signer
        self.reason = reason
        self.location = location
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "page": self.page_num,
            "rect": list(self.rect),
            "signer": self.signer,
            "reason": self.reason,
            "location": self.location,
            "timestamp": self.timestamp.isoformat()
        }


class SignatureManager(QObject):
    """簽章管理器"""
    
    # 信號定義
    signature_added = pyqtSignal(object)  # 新增簽章
    signature_verified = pyqtSignal(bool, str)  # 簽章驗證結果
    
    def __init__(self, pdf_handler):
        super().__init__()
        self.pdf_handler = pdf_handler
        self.signatures: List[SignatureInfo] = []
    
    def add_signature_field(self, page_num: int, rect: fitz.Rect, field_name: str = "Signature") -> bool:
        """
        新增簽章欄位
        
        Args:
            page_num: 頁碼
            rect: 簽章區域
            field_name: 欄位名稱
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            # 新增簽章欄位（使用文字欄位模擬）
            widget = fitz.Widget()
            widget.field_name = field_name
            widget.field_type = fitz.PDF_WIDGET_TYPE_SIGNATURE
            widget.rect = rect
            
            page.add_widget(widget)
            return True
            
        except Exception as e:
            print(f"新增簽章欄位失敗: {e}")
            return False
    
    def add_visual_signature(self, page_num: int, rect: fitz.Rect, 
                            signer: str, reason: str = "", 
                            location: str = "", image_path: Optional[str] = None) -> bool:
        """
        新增視覺化簽章
        
        Args:
            page_num: 頁碼
            rect: 簽章區域
            signer: 簽章者
            reason: 簽章原因
            location: 簽章地點
            image_path: 簽章圖片路徑（可選）
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            # 建立簽章資訊
            sig_info = SignatureInfo(page_num, rect, signer, reason, location)
            
            # 如果有簽章圖片，插入圖片
            if image_path:
                page.insert_image(rect, filename=image_path)
            else:
                # 繪製簽章框和文字
                shape = page.new_shape()
                
                # 繪製邊框
                shape.draw_rect(rect)
                shape.finish(color=(0, 0, 1), width=1)
                
                # 新增簽章文字
                text_rect = fitz.Rect(rect.x0 + 5, rect.y0 + 5, rect.x1 - 5, rect.y1 - 5)
                signature_text = f"簽署者: {signer}\n"
                if reason:
                    signature_text += f"原因: {reason}\n"
                if location:
                    signature_text += f"地點: {location}\n"
                signature_text += f"時間: {sig_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                
                shape.insert_textbox(text_rect, signature_text, 
                                   fontsize=8, color=(0, 0, 0))
                shape.commit()
            
            self.signatures.append(sig_info)
            self.signature_added.emit(sig_info)
            return True
            
        except Exception as e:
            print(f"新增簽章失敗: {e}")
            return False
    
    def add_text_signature(self, page_num: int, rect: fitz.Rect, 
                          signature_text: str, font_size: int = 12) -> bool:
        """
        新增文字簽章
        
        Args:
            page_num: 頁碼
            rect: 簽章區域
            signature_text: 簽章文字
            font_size: 字體大小
            
        Returns:
            成功返回 True
        """
        try:
            page = self.pdf_handler.get_page(page_num)
            if not page:
                return False
            
            # 新增文字簽章
            shape = page.new_shape()
            shape.insert_textbox(rect, signature_text, 
                               fontsize=font_size, 
                               fontname="helv",
                               color=(0, 0, 0.8))
            shape.commit()
            
            return True
            
        except Exception as e:
            print(f"新增文字簽章失敗: {e}")
            return False
    
    def verify_signature(self, signature_index: int) -> bool:
        """
        驗證簽章
        
        注意：這是簡化的驗證，實際的數位簽章驗證需要更複雜的密碼學操作
        
        Args:
            signature_index: 簽章索引
            
        Returns:
            驗證結果
        """
        if 0 <= signature_index < len(self.signatures):
            sig = self.signatures[signature_index]
            # 簡化驗證：檢查簽章資訊是否完整
            is_valid = bool(sig.signer and sig.timestamp)
            message = "簽章有效" if is_valid else "簽章無效"
            self.signature_verified.emit(is_valid, message)
            return is_valid
        return False
    
    def get_all_signatures(self) -> List[SignatureInfo]:
        """獲取所有簽章"""
        return self.signatures.copy()
    
    def get_signatures_on_page(self, page_num: int) -> List[SignatureInfo]:
        """獲取指定頁面的簽章"""
        return [s for s in self.signatures if s.page_num == page_num]
    
    def remove_signature(self, index: int) -> bool:
        """
        移除簽章（僅從列表中移除，不影響 PDF）
        
        Args:
            index: 簽章索引
            
        Returns:
            成功返回 True
        """
        if 0 <= index < len(self.signatures):
            del self.signatures[index]
            return True
        return False
    
    def clear_all_signatures(self):
        """清除所有簽章記錄"""
        self.signatures.clear()

