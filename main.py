# -*- coding: utf-8 -*-
"""
YouTube 影片下載器
主程式入口
"""
import sys
import os

# 確保當前目錄在路徑中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.main_window import MainWindow


def main():
    """主函數"""
    # 啟用高 DPI 支援
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube Downloader")
    app.setApplicationDisplayName("YouTube 影片下載器")
    app.setOrganizationName("YTDownloader")
    
    # 設定預設字體
    font = QFont("Microsoft JhengHei", 10)
    app.setFont(font)
    
    # 創建主視窗
    window = MainWindow()
    window.show()
    
    # 執行應用程式
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

