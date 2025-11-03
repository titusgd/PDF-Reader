"""
PDF 處理器測試
"""

import unittest
from src.pdf_handler import PDFHandler


class TestPDFHandler(unittest.TestCase):
    """PDF 處理器測試類別"""
    
    def setUp(self):
        """測試前置設定"""
        self.handler = PDFHandler()
    
    def test_initialization(self):
        """測試初始化"""
        self.assertIsNone(self.handler.document)
        self.assertEqual(self.handler.page_count, 0)
        self.assertEqual(self.handler.current_page, 0)
    
    def tearDown(self):
        """測試後清理"""
        if self.handler.document:
            self.handler.close_document()


if __name__ == '__main__':
    unittest.main()

