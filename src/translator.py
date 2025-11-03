"""
翻譯模組
提供線上和離線翻譯功能
"""

from deep_translator import GoogleTranslator
from typing import Optional, List, Tuple, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import os
import pickle
from pathlib import Path

# 嘗試匯入離線翻譯模組（使用 googletrans 的離線快取）
try:
    from googletrans import Translator as GoogletransTranslator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

# 離線翻譯快取
OFFLINE_AVAILABLE = True  # 使用快取式離線翻譯


class TranslationWorker(QThread):
    """翻譯工作執行緒"""
    
    progress_updated = pyqtSignal(int, int)  # 當前進度, 總數
    translation_completed = pyqtSignal(str)  # 翻譯完成
    error_occurred = pyqtSignal(str)  # 錯誤發生
    
    def __init__(self, texts: List[str], from_code: str, to_code: str):
        super().__init__()
        self.texts = texts
        self.from_code = from_code
        self.to_code = to_code
        self.translation_manager = None
    
    def set_translation_manager(self, manager):
        """設定翻譯管理器"""
        self.translation_manager = manager
    
    def run(self):
        """執行翻譯"""
        try:
            if not self.translation_manager:
                self.error_occurred.emit("翻譯管理器未設定")
                return
            
            results = []
            total = len(self.texts)
            
            for i, text in enumerate(self.texts):
                if text.strip():
                    translated = self.translation_manager.translate(
                        text, self.from_code, self.to_code
                    )
                    results.append(translated)
                else:
                    results.append("")
                
                self.progress_updated.emit(i + 1, total)
            
            self.translation_completed.emit("\n\n".join(results))
            
        except Exception as e:
            self.error_occurred.emit(f"翻譯錯誤: {str(e)}")


class TranslationManager(QObject):
    """翻譯管理器"""
    
    # 信號定義
    translation_ready = pyqtSignal(str)  # 翻譯完成
    error_occurred = pyqtSignal(str)  # 錯誤發生
    
    # 常用語言代碼
    LANGUAGES = {
        "自動偵測": "auto",
        "英文": "en",
        "繁體中文": "zh-TW",
        "簡體中文": "zh-CN",
        "日文": "ja",
        "韓文": "ko",
        "法文": "fr",
        "德文": "de",
        "西班牙文": "es",
        "義大利文": "it",
        "俄文": "ru",
        "阿拉伯文": "ar",
        "葡萄牙文": "pt",
    }
    
    def __init__(self, use_offline=False):
        super().__init__()
        self.translation_worker = None
        self.use_offline = use_offline
        self.translation_cache = {}  # 翻譯快取
        self.cache_file = Path.home() / ".pdfreader_translation_cache.pkl"
        self._load_cache()
    
    def get_available_languages(self) -> List[str]:
        """獲取可用語言列表"""
        return list(self.LANGUAGES.keys())
    
    def get_language_code(self, language_name: str) -> str:
        """獲取語言代碼"""
        return self.LANGUAGES.get(language_name, "en")
    
    def _load_cache(self):
        """載入翻譯快取"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    self.translation_cache = pickle.load(f)
        except Exception as e:
            print(f"載入快取失敗: {e}")
            self.translation_cache = {}
    
    def _save_cache(self):
        """儲存翻譯快取"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.translation_cache, f)
        except Exception as e:
            print(f"儲存快取失敗: {e}")
    
    def _get_cache_key(self, text: str, from_code: str, to_code: str) -> str:
        """生成快取鍵值"""
        return f"{from_code}:{to_code}:{hash(text)}"
    
    def translate(self, text: str, from_code: str = "en", to_code: str = "zh-TW") -> str:
        """
        翻譯文字（支援離線快取）
        
        Args:
            text: 要翻譯的文字
            from_code: 來源語言代碼
            to_code: 目標語言代碼
            
        Returns:
            翻譯後的文字
        """
        if not text or not text.strip():
            return ""
        
        # 檢查快取
        cache_key = self._get_cache_key(text, from_code, to_code)
        if cache_key in self.translation_cache:
            print("使用快取的翻譯")
            return self.translation_cache[cache_key]
        
        # 離線模式：只使用快取
        if self.use_offline:
            error_msg = "離線模式：無法翻譯新文字（未在快取中）\n\n請先在有網路時翻譯此文字以建立快取"
            self.error_occurred.emit(error_msg)
            return f"[{error_msg}]"
        
        # 線上翻譯
        try:
            translator = GoogleTranslator(source=from_code, target=to_code)
            
            # 處理長文字（Google Translate 有字數限制）
            max_length = 4500
            if len(text) > max_length:
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                result = " ".join(translated_chunks)
            else:
                result = translator.translate(text)
            
            # 儲存到快取
            self.translation_cache[cache_key] = result
            self._save_cache()
            
            return result
            
        except Exception as e:
            error_msg = f"翻譯失敗 (請檢查網路連線): {str(e)}"
            self.error_occurred.emit(error_msg)
            return f"[{error_msg}]"
    
    def set_offline_mode(self, enabled: bool):
        """設定是否使用離線模式（僅使用快取）"""
        self.use_offline = enabled
    
    def is_offline_available(self) -> bool:
        """檢查離線翻譯是否可用（快取式離線）"""
        return OFFLINE_AVAILABLE
    
    def get_cache_size(self) -> int:
        """獲取快取大小"""
        return len(self.translation_cache)
    
    def clear_cache(self):
        """清除翻譯快取"""
        self.translation_cache = {}
        self._save_cache()
    
    def translate_batch(self, texts: List[str], from_code: str = "en", 
                       to_code: str = "zh-TW", callback: Optional[Callable] = None):
        """
        批次翻譯（使用後台執行緒）
        
        Args:
            texts: 要翻譯的文字列表
            from_code: 來源語言代碼
            to_code: 目標語言代碼
            callback: 進度回調函數
        """
        # 停止之前的翻譯工作
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.quit()
            self.translation_worker.wait()
        
        # 創建新的翻譯工作
        self.translation_worker = TranslationWorker(texts, from_code, to_code)
        self.translation_worker.set_translation_manager(self)
        
        # 連接信號
        self.translation_worker.translation_completed.connect(self.translation_ready.emit)
        self.translation_worker.error_occurred.connect(self.error_occurred.emit)
        
        if callback:
            self.translation_worker.progress_updated.connect(callback)
        
        # 啟動執行緒
        self.translation_worker.start()
    

