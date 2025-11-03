"""
書籤管理模組
提供書籤的新增、編輯、刪除功能
"""

from typing import List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
import json


class Bookmark:
    """書籤類別"""
    
    def __init__(self, title: str, page_num: int, description: str = ""):
        self.title = title
        self.page_num = page_num
        self.description = description
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "title": self.title,
            "page_num": self.page_num,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Bookmark':
        """從字典建立書籤"""
        return Bookmark(
            title=data.get("title", ""),
            page_num=data.get("page_num", 0),
            description=data.get("description", "")
        )


class BookmarkManager(QObject):
    """書籤管理器"""
    
    # 信號定義
    bookmark_added = pyqtSignal(object)  # 新增書籤
    bookmark_removed = pyqtSignal(int)  # 刪除書籤（索引）
    bookmark_modified = pyqtSignal(int, object)  # 修改書籤
    bookmarks_loaded = pyqtSignal()  # 書籤載入完成
    
    def __init__(self):
        super().__init__()
        self.bookmarks: List[Bookmark] = []
        self.file_path: Optional[str] = None
    
    def add_bookmark(self, title: str, page_num: int, description: str = "") -> Bookmark:
        """
        新增書籤
        
        Args:
            title: 書籤標題
            page_num: 頁碼
            description: 描述
            
        Returns:
            新建的書籤物件
        """
        bookmark = Bookmark(title, page_num, description)
        self.bookmarks.append(bookmark)
        self.bookmark_added.emit(bookmark)
        return bookmark
    
    def remove_bookmark(self, index: int) -> bool:
        """
        刪除書籤
        
        Args:
            index: 書籤索引
            
        Returns:
            成功返回 True
        """
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.bookmark_removed.emit(index)
            return True
        return False
    
    def update_bookmark(self, index: int, title: Optional[str] = None, 
                       page_num: Optional[int] = None, 
                       description: Optional[str] = None) -> bool:
        """
        更新書籤
        
        Args:
            index: 書籤索引
            title: 新標題
            page_num: 新頁碼
            description: 新描述
            
        Returns:
            成功返回 True
        """
        if 0 <= index < len(self.bookmarks):
            bookmark = self.bookmarks[index]
            if title is not None:
                bookmark.title = title
            if page_num is not None:
                bookmark.page_num = page_num
            if description is not None:
                bookmark.description = description
            
            self.bookmark_modified.emit(index, bookmark)
            return True
        return False
    
    def get_bookmark(self, index: int) -> Optional[Bookmark]:
        """獲取書籤"""
        if 0 <= index < len(self.bookmarks):
            return self.bookmarks[index]
        return None
    
    def get_all_bookmarks(self) -> List[Bookmark]:
        """獲取所有書籤"""
        return self.bookmarks.copy()
    
    def find_bookmarks_by_page(self, page_num: int) -> List[Tuple[int, Bookmark]]:
        """
        查找指定頁面的所有書籤
        
        Args:
            page_num: 頁碼
            
        Returns:
            [(索引, 書籤)] 列表
        """
        results = []
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.page_num == page_num:
                results.append((i, bookmark))
        return results
    
    def clear_all(self):
        """清除所有書籤"""
        self.bookmarks.clear()
        self.bookmarks_loaded.emit()
    
    def save_to_file(self, file_path: str) -> bool:
        """
        儲存書籤到檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            成功返回 True
        """
        try:
            data = {
                "bookmarks": [b.to_dict() for b in self.bookmarks]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"儲存書籤失敗: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """
        從檔案載入書籤
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            成功返回 True
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.bookmarks.clear()
            for bookmark_data in data.get("bookmarks", []):
                bookmark = Bookmark.from_dict(bookmark_data)
                self.bookmarks.append(bookmark)
            
            self.bookmarks_loaded.emit()
            return True
        except Exception as e:
            print(f"載入書籤失敗: {e}")
            return False
    
    def sort_by_page(self):
        """按頁碼排序書籤"""
        self.bookmarks.sort(key=lambda b: b.page_num)
        self.bookmarks_loaded.emit()
    
    def sort_by_title(self):
        """按標題排序書籤"""
        self.bookmarks.sort(key=lambda b: b.title)
        self.bookmarks_loaded.emit()

