"""
工具函數模組
提供各種輔助功能
"""

import os
from typing import Optional, Tuple
from PyQt6.QtCore import QSettings


class Config:
    """應用程式配置管理"""
    
    def __init__(self):
        self.settings = QSettings("PDFReader", "PDFReaderApp")
    
    def get_recent_files(self) -> list:
        """獲取最近開啟的檔案清單"""
        recent = self.settings.value("recent_files", [])
        if isinstance(recent, str):
            return [recent] if recent else []
        return recent if recent else []
    
    def add_recent_file(self, file_path: str):
        """新增檔案到最近開啟清單"""
        recent = self.get_recent_files()
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        # 保留最近 10 個檔案
        recent = recent[:10]
        self.settings.setValue("recent_files", recent)
    
    def get_window_geometry(self) -> Optional[bytes]:
        """獲取視窗幾何資訊"""
        return self.settings.value("window_geometry")
    
    def set_window_geometry(self, geometry: bytes):
        """保存視窗幾何資訊"""
        self.settings.setValue("window_geometry", geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        """獲取視窗狀態"""
        return self.settings.value("window_state")
    
    def set_window_state(self, state: bytes):
        """保存視窗狀態"""
        self.settings.setValue("window_state", state)
    
    def get_zoom_level(self) -> float:
        """獲取縮放級別"""
        return float(self.settings.value("zoom_level", 1.0))
    
    def set_zoom_level(self, zoom: float):
        """保存縮放級別"""
        self.settings.setValue("zoom_level", zoom)
    
    def get_dark_mode(self) -> bool:
        """獲取深色模式設定"""
        return self.settings.value("dark_mode", False, type=bool)
    
    def set_dark_mode(self, enabled: bool):
        """設定深色模式"""
        self.settings.setValue("dark_mode", enabled)


def format_file_size(size: int) -> str:
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_page_dimensions(page) -> Tuple[float, float]:
    """獲取頁面尺寸"""
    rect = page.rect
    return rect.width, rect.height


def ensure_directory_exists(directory: str):
    """確保目錄存在"""
    os.makedirs(directory, exist_ok=True)

