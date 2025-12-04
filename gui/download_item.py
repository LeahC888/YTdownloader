# -*- coding: utf-8 -*-
"""
下載項目 Widget - 顯示單個下載任務的狀態與進度（簡化版：文字+百分比）
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class DownloadItemWidget(QFrame):
    """單個下載項目的 Widget - 文字進度顯示"""
    
    cancel_requested = pyqtSignal(str)  # 發送 URL 信號請求取消
    
    def __init__(self, url: str, title: str = "載入中...", parent=None):
        super().__init__(parent)
        self.url = url
        self.title = title
        self._setup_ui()
        
    def _setup_ui(self):
        """設置 UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            DownloadItemWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                margin: 3px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ff6b7a;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 8, 10, 8)
        
        # 左側：標題和狀態
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Microsoft JhengHei", 10, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumWidth(500)
        left_layout.addWidget(self.title_label)
        
        self.status_label = QLabel("等待中...")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        left_layout.addWidget(self.status_label)
        
        main_layout.addLayout(left_layout, stretch=1)
        
        # 中間：進度百分比（大字體）
        self.progress_label = QLabel("0%")
        self.progress_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.progress_label.setStyleSheet("color: #00d4aa; min-width: 70px;")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.progress_label)
        
        # 右側：取消按鈕
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedWidth(60)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        main_layout.addWidget(self.cancel_btn)
        
    def _on_cancel_clicked(self):
        """取消按鈕點擊處理"""
        self.cancel_requested.emit(self.url)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("取消中")
        
    def update_title(self, title: str):
        """更新標題"""
        self.title = title
        # 截斷過長標題
        if len(title) > 60:
            title = title[:57] + "..."
        self.title_label.setText(title)
        
    def update_progress(self, data: dict):
        """更新進度"""
        status = data.get('status', '')
        
        if status == 'downloading':
            percent = data.get('percent', 0)
            self.progress_label.setText(f"{int(percent)}%")
            
            # 更新速度資訊
            speed = data.get('speed', 0)
            eta = data.get('eta', 0)
            
            status_text = "下載中"
            if speed:
                speed_str = self._format_speed(speed)
                status_text += f" | {speed_str}"
            if eta:
                eta_str = self._format_time(eta)
                status_text += f" | 剩餘 {eta_str}"
                
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet("color: #00d4aa; font-size: 11px;")
            
        elif status == 'processing':
            self.progress_label.setText("100%")
            self.status_label.setText("正在合併/轉檔...")
            self.status_label.setStyleSheet("color: #ffa502; font-size: 11px;")
            
        elif status == 'completed':
            self.progress_label.setText("✓")
            self.progress_label.setStyleSheet("color: #2ed573; min-width: 70px; font-size: 20px;")
            self.status_label.setText("下載完成")
            self.status_label.setStyleSheet("color: #2ed573; font-size: 11px;")
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setText("完成")
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ed573;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
            """)
            
        elif status == 'error':
            error_msg = data.get('error', '未知錯誤')
            self.progress_label.setText("✗")
            self.progress_label.setStyleSheet("color: #ff4757; min-width: 70px; font-size: 20px;")
            self.status_label.setText(f"失敗: {error_msg[:40]}")
            self.status_label.setStyleSheet("color: #ff4757; font-size: 11px;")
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setText("失敗")
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
            """)
            
        elif status == 'cancelled':
            self.progress_label.setText("-")
            self.progress_label.setStyleSheet("color: #888888; min-width: 70px;")
            self.status_label.setText("已取消")
            self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setText("已取消")
            
    def update_status(self, message: str):
        """更新狀態訊息"""
        self.status_label.setText(message)
        
    def _format_speed(self, speed: float) -> str:
        """格式化速度"""
        if not speed or speed <= 0:
            return ""
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.1f} KB/s"
        else:
            return f"{speed/(1024*1024):.2f} MB/s"
            
    def _format_time(self, seconds: int) -> str:
        """格式化時間"""
        if not seconds or seconds <= 0:
            return ""
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}分{secs}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}時{minutes}分"
