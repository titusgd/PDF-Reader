"""
表單編輯模組
提供 PDF 表單欄位的辨識和填寫功能
"""

import fitz
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class FormField:
    """表單欄位類別"""
    
    def __init__(self, widget, page_num: int):
        self.widget = widget
        self.page_num = page_num
        self.field_name = widget.field_name
        self.field_type = widget.field_type
        self.field_value = widget.field_value
        self.rect = widget.rect
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "name": self.field_name,
            "type": self.field_type,
            "value": self.field_value,
            "page": self.page_num,
            "rect": list(self.rect) if self.rect else None
        }


class FormEditor(QObject):
    """表單編輯器"""
    
    # 信號定義
    form_loaded = pyqtSignal(int)  # 表單載入完成，參數為欄位數量
    field_updated = pyqtSignal(str, object)  # 欄位更新
    form_saved = pyqtSignal()  # 表單儲存完成
    
    def __init__(self, pdf_handler):
        super().__init__()
        self.pdf_handler = pdf_handler
        self.form_fields: List[FormField] = []
    
    def load_form_fields(self) -> List[FormField]:
        """
        載入文件中的所有表單欄位
        
        Returns:
            表單欄位列表
        """
        self.form_fields.clear()
        
        if not self.pdf_handler.document:
            return []
        
        try:
            for page_num in range(self.pdf_handler.page_count):
                page = self.pdf_handler.get_page(page_num)
                if not page:
                    continue
                
                # 獲取頁面上的所有欄位
                widgets = page.widgets()
                for widget in widgets:
                    field = FormField(widget, page_num)
                    self.form_fields.append(field)
            
            self.form_loaded.emit(len(self.form_fields))
            return self.form_fields
            
        except Exception as e:
            print(f"載入表單欄位失敗: {e}")
            return []
    
    def get_field_by_name(self, field_name: str) -> Optional[FormField]:
        """根據名稱獲取欄位"""
        for field in self.form_fields:
            if field.field_name == field_name:
                return field
        return None
    
    def get_fields_on_page(self, page_num: int) -> List[FormField]:
        """獲取指定頁面的所有欄位"""
        return [f for f in self.form_fields if f.page_num == page_num]
    
    def update_field_value(self, field_name: str, value: Any) -> bool:
        """
        更新欄位值
        
        Args:
            field_name: 欄位名稱
            value: 新值
            
        Returns:
            成功返回 True
        """
        try:
            field = self.get_field_by_name(field_name)
            if not field:
                return False
            
            # 更新欄位值
            field.widget.field_value = value
            field.widget.update()
            field.field_value = value
            
            self.field_updated.emit(field_name, value)
            return True
            
        except Exception as e:
            print(f"更新欄位失敗: {e}")
            return False
    
    def fill_form(self, data: Dict[str, Any]) -> int:
        """
        批量填寫表單
        
        Args:
            data: 欄位名稱到值的字典
            
        Returns:
            成功更新的欄位數量
        """
        count = 0
        for field_name, value in data.items():
            if self.update_field_value(field_name, value):
                count += 1
        return count
    
    def get_form_data(self) -> Dict[str, Any]:
        """
        獲取所有表單資料
        
        Returns:
            欄位名稱到值的字典
        """
        data = {}
        for field in self.form_fields:
            if field.field_name:
                data[field.field_name] = field.field_value
        return data
    
    def reset_form(self) -> bool:
        """
        重設表單（清空所有欄位）
        
        Returns:
            成功返回 True
        """
        try:
            for field in self.form_fields:
                field.widget.field_value = ""
                field.widget.update()
                field.field_value = ""
            return True
        except Exception as e:
            print(f"重設表單失敗: {e}")
            return False
    
    def export_form_data(self, file_path: str) -> bool:
        """
        匯出表單資料到 JSON 檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            成功返回 True
        """
        try:
            import json
            data = {
                "fields": [f.to_dict() for f in self.form_fields]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"匯出表單資料失敗: {e}")
            return False
    
    def import_form_data(self, file_path: str) -> bool:
        """
        從 JSON 檔案匯入表單資料
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            成功返回 True
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            field_data = {}
            for field_info in data.get("fields", []):
                name = field_info.get("name")
                value = field_info.get("value")
                if name:
                    field_data[name] = value
            
            self.fill_form(field_data)
            return True
            
        except Exception as e:
            print(f"匯入表單資料失敗: {e}")
            return False
    
    def save_form(self) -> bool:
        """
        儲存表單（將變更寫入 PDF）
        
        Returns:
            成功返回 True
        """
        try:
            # PyMuPDF 會自動追蹤欄位變更
            # 只需要儲存文件即可
            success = self.pdf_handler.save_document()
            if success:
                self.form_saved.emit()
            return success
        except Exception as e:
            print(f"儲存表單失敗: {e}")
            return False

