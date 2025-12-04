# -*- coding: utf-8 -*-
"""
主視窗 UI
"""
import os
from typing import Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QPushButton,
    QFileDialog, QScrollArea, QFrame, QLineEdit,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

from downloader import VideoDownloader, check_dependencies
from utils.config import QUALITY_OPTIONS, DEFAULT_DOWNLOAD_PATH, MAX_CONCURRENT_DOWNLOADS
from gui.download_item import DownloadItemWidget


class WorkerSignals(QObject):
    """工作執行緒信號"""
    progress = pyqtSignal(str, dict)  # url, progress_data
    status = pyqtSignal(str, str)     # url, status_message
    finished = pyqtSignal(str, bool)  # url, success
    title_fetched = pyqtSignal(str, str)  # url, title


class DownloadWorker(QRunnable):
    """下載工作執行緒"""
    
    def __init__(self, url: str, output_path: str, quality: str, use_aria2c: bool = True):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.use_aria2c = use_aria2c
        self.signals = WorkerSignals()
        self.downloader = None
        
    def run(self):
        """執行下載"""
        def progress_callback(data):
            self.signals.progress.emit(self.url, data)
            
        def status_callback(message):
            self.signals.status.emit(self.url, message)
            
        self.downloader = VideoDownloader(
            url=self.url,
            output_path=self.output_path,
            quality=self.quality,
            progress_callback=progress_callback,
            status_callback=status_callback,
            use_aria2c=self.use_aria2c
        )
        
        # 先獲取標題
        try:
            info = self.downloader.get_video_info()
            self.signals.title_fetched.emit(self.url, info['title'])
        except Exception as e:
            self.signals.title_fetched.emit(self.url, f"未知標題 ({self.url[:30]}...)")
        
        # 執行下載
        success = self.downloader.download()
        self.signals.finished.emit(self.url, success)
        
    def cancel(self):
        """取消下載"""
        if self.downloader:
            self.downloader.cancel()


class MainWindow(QMainWindow):
    """主視窗"""
    
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(MAX_CONCURRENT_DOWNLOADS)
        self.download_items: Dict[str, DownloadItemWidget] = {}
        self.download_workers: Dict[str, DownloadWorker] = {}
        self.output_path = DEFAULT_DOWNLOAD_PATH
        
        self._setup_ui()
        self._check_dependencies()
        
    def _setup_ui(self):
        """設置 UI"""
        self.setWindowTitle("YouTube 影片下載器")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                font-family: "Microsoft JhengHei", "Segoe UI", sans-serif;
            }
            QLabel {
                color: #eaeaea;
            }
            QTextEdit, QLineEdit {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 10px;
                color: #eaeaea;
                font-size: 13px;
            }
            QTextEdit:focus, QLineEdit:focus {
                border-color: #e94560;
            }
            QComboBox {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 8px 15px;
                color: #eaeaea;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #e94560;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #e94560;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #0f3460;
                color: #eaeaea;
                selection-background-color: #e94560;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e94560, stop:1 #0f3460
                );
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:1 #1a5490
                );
            }
            QPushButton:disabled {
                background: #404040;
                color: #888888;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 標題
        title_label = QLabel("🎬 YouTube 影片下載器")
        title_label.setFont(QFont("Microsoft JhengHei", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #e94560; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 依賴狀態
        self.deps_label = QLabel()
        self.deps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.deps_label.setStyleSheet("font-size: 11px; margin-bottom: 10px;")
        main_layout.addWidget(self.deps_label)
        
        # URL 輸入區
        url_frame = QFrame()
        url_frame.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        url_layout = QVBoxLayout(url_frame)
        
        url_label = QLabel("📋 貼上 YouTube 連結 (每行一個):")
        url_label.setFont(QFont("Microsoft JhengHei", 12))
        url_layout.addWidget(url_label)
        
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "範例:\n"
            "https://www.youtube.com/watch?v=xxxxx\n"
            "https://youtu.be/xxxxx\n"
            "https://www.youtube.com/playlist?list=xxxxx"
        )
        self.url_input.setMinimumHeight(120)
        self.url_input.setMaximumHeight(150)
        url_layout.addWidget(self.url_input)
        
        main_layout.addWidget(url_frame)
        
        # 設定列
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(20)
        
        # 畫質選擇
        quality_layout = QHBoxLayout()
        quality_label = QLabel("🎥 畫質:")
        quality_label.setFont(QFont("Microsoft JhengHei", 12))
        quality_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(list(QUALITY_OPTIONS.keys()))
        self.quality_combo.setCurrentIndex(0)  # 預設最高畫質
        quality_layout.addWidget(self.quality_combo)
        settings_layout.addLayout(quality_layout)
        
        settings_layout.addStretch()
        
        # 輸出資料夾
        path_layout = QHBoxLayout()
        path_label = QLabel("📁 儲存位置:")
        path_label.setFont(QFont("Microsoft JhengHei", 12))
        path_layout.addWidget(path_label)
        
        self.path_input = QLineEdit()
        self.path_input.setText(self.output_path)
        self.path_input.setMinimumWidth(300)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("瀏覽")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #0f3460;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #1a5490;
            }
        """)
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)
        settings_layout.addLayout(path_layout)
        
        main_layout.addLayout(settings_layout)
        
        # aria2c 選項
        self.aria2c_enabled = True
        aria2c_layout = QHBoxLayout()
        aria2c_label = QLabel("⚡ 切片加速下載 (aria2c):")
        aria2c_label.setFont(QFont("Microsoft JhengHei", 11))
        aria2c_layout.addWidget(aria2c_label)
        
        self.aria2c_status = QLabel()
        aria2c_layout.addWidget(self.aria2c_status)
        aria2c_layout.addStretch()
        
        main_layout.addLayout(aria2c_layout)
        
        # 下載按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.download_btn = QPushButton("🚀 開始下載")
        self.download_btn.setMinimumWidth(200)
        self.download_btn.setMinimumHeight(50)
        self.download_btn.clicked.connect(self._start_downloads)
        btn_layout.addWidget(self.download_btn)
        
        self.clear_btn = QPushButton("🗑️ 清除列表")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: #555555;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_downloads)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # 下載進度列表
        progress_label = QLabel("📊 下載進度:")
        progress_label.setFont(QFont("Microsoft JhengHei", 14, QFont.Weight.Bold))
        progress_label.setStyleSheet("margin-top: 20px;")
        main_layout.addWidget(progress_label)
        
        # 滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0f0f23;
                border: 2px solid #0f3460;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background: #16213e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #e94560;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        self.download_list_widget = QWidget()
        self.download_list_layout = QVBoxLayout(self.download_list_widget)
        self.download_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.download_list_layout.setSpacing(10)
        self.download_list_layout.setContentsMargins(10, 10, 10, 10)
        
        # 預設提示
        self.empty_label = QLabel("尚無下載任務\n請貼上 YouTube 連結後點擊「開始下載」")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #666666; font-size: 14px; padding: 50px;")
        self.download_list_layout.addWidget(self.empty_label)
        
        scroll_area.setWidget(self.download_list_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # 狀態列
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就緒")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        concurrent_label = QLabel(f"最大同時下載: {MAX_CONCURRENT_DOWNLOADS} 個")
        concurrent_label.setStyleSheet("color: #888888; font-size: 11px;")
        status_layout.addWidget(concurrent_label)
        
        main_layout.addLayout(status_layout)
        
    def _check_dependencies(self):
        """檢查外部依賴"""
        deps = check_dependencies()
        
        status_parts = []
        if deps['ffmpeg']:
            status_parts.append("✓ FFmpeg")
        else:
            status_parts.append("✗ FFmpeg (需要安裝)")
            
        if deps['aria2c']:
            status_parts.append("✓ aria2c")
            self.aria2c_enabled = True  # 啟用 aria2c
            self.aria2c_status.setText("已啟用 - 切片加速下載")
            self.aria2c_status.setStyleSheet("color: #2ed573;")
        else:
            status_parts.append("✗ aria2c (選用)")
            self.aria2c_enabled = False
            self.aria2c_status.setText("未安裝 (將使用預設下載器)")
            self.aria2c_status.setStyleSheet("color: #ffa502;")
            
        self.deps_label.setText(" | ".join(status_parts))
        
        if deps['ffmpeg']:
            self.deps_label.setStyleSheet("color: #2ed573; font-size: 11px;")
        else:
            self.deps_label.setStyleSheet("color: #ff4757; font-size: 11px;")
            QMessageBox.warning(
                self,
                "缺少依賴",
                "未檢測到 FFmpeg。\n\n"
                "請安裝 FFmpeg 並確保已加入系統 PATH。\n"
                "下載地址: https://ffmpeg.org/download.html"
            )
            
    def _browse_folder(self):
        """瀏覽資料夾"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "選擇儲存位置",
            self.output_path
        )
        if folder:
            self.output_path = folder
            self.path_input.setText(folder)
            
    def _start_downloads(self):
        """開始下載"""
        # 獲取 URL 列表
        text = self.url_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "請輸入至少一個 YouTube 連結")
            return
            
        urls = [url.strip() for url in text.split('\n') if url.strip()]
        
        # 過濾有效 URL
        valid_urls = []
        for url in urls:
            if 'youtube.com' in url or 'youtu.be' in url:
                if url not in self.download_items:
                    valid_urls.append(url)
                    
        if not valid_urls:
            QMessageBox.warning(self, "提示", "沒有有效的新 YouTube 連結")
            return
            
        # 隱藏空提示
        self.empty_label.hide()
        
        # 獲取設定
        quality = self.quality_combo.currentText()
        output_path = self.path_input.text() or self.output_path
        
        # 創建下載項目
        for url in valid_urls:
            # 創建 UI 項目
            item_widget = DownloadItemWidget(url)
            item_widget.cancel_requested.connect(self._cancel_download)
            self.download_items[url] = item_widget
            self.download_list_layout.addWidget(item_widget)
            
            # 創建工作執行緒
            worker = DownloadWorker(url, output_path, quality, self.aria2c_enabled)
            worker.signals.progress.connect(self._on_progress)
            worker.signals.status.connect(self._on_status)
            worker.signals.finished.connect(self._on_finished)
            worker.signals.title_fetched.connect(self._on_title_fetched)
            
            self.download_workers[url] = worker
            self.thread_pool.start(worker)
            
        self.status_label.setText(f"正在下載 {len(valid_urls)} 個影片...")
        
    def _clear_downloads(self):
        """清除已完成的下載項目"""
        urls_to_remove = []
        for url, item in self.download_items.items():
            if url not in self.download_workers:
                urls_to_remove.append(url)
                
        for url in urls_to_remove:
            item = self.download_items.pop(url)
            self.download_list_layout.removeWidget(item)
            item.deleteLater()
            
        if not self.download_items:
            self.empty_label.show()
            
    @pyqtSlot(str)
    def _cancel_download(self, url: str):
        """取消下載"""
        if url in self.download_workers:
            self.download_workers[url].cancel()
            if url in self.download_items:
                self.download_items[url].update_progress({'status': 'cancelled'})
                
    @pyqtSlot(str, dict)
    def _on_progress(self, url: str, data: dict):
        """進度更新處理"""
        if url in self.download_items:
            self.download_items[url].update_progress(data)
            
    @pyqtSlot(str, str)
    def _on_status(self, url: str, message: str):
        """狀態更新處理"""
        if url in self.download_items:
            self.download_items[url].update_status(message)
            
    @pyqtSlot(str, str)
    def _on_title_fetched(self, url: str, title: str):
        """標題獲取處理"""
        if url in self.download_items:
            self.download_items[url].update_title(title)
            
    @pyqtSlot(str, bool)
    def _on_finished(self, url: str, success: bool):
        """下載完成處理"""
        if url in self.download_workers:
            del self.download_workers[url]
            
        # 更新狀態
        active_count = len(self.download_workers)
        if active_count > 0:
            self.status_label.setText(f"正在下載 {active_count} 個影片...")
        else:
            self.status_label.setText("所有下載已完成")
            
    def closeEvent(self, event):
        """關閉視窗處理"""
        # 取消所有進行中的下載
        for worker in self.download_workers.values():
            worker.cancel()
        self.thread_pool.waitForDone(3000)
        event.accept()

