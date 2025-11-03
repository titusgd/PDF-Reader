"""
PDF 閱讀器應用程式入口點
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow


def main():
    """主函數"""
    # 啟用高 DPI 縮放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 建立應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("PDF 閱讀器")
    app.setOrganizationName("PDFReader")
    
    # 建立並顯示主視窗
    window = MainWindow()
    window.show()
    
    # 執行應用程式
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

