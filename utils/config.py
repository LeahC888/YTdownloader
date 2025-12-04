# -*- coding: utf-8 -*-
"""
配置管理模組
"""
import os
from pathlib import Path

# 預設下載路徑
DEFAULT_DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YTDownloader")

# 畫質選項 - 優先選擇 m4a 音頻（AAC），避免 opus 格式相容性問題
QUALITY_OPTIONS = {
    "最高畫質": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]/best",
}

# 最大同時下載數
MAX_CONCURRENT_DOWNLOADS = 6

# aria2c 配置
ARIA2C_OPTIONS = [
    "--min-split-size=1M",
    "--max-connection-per-server=16",
    "--split=16",
    "--max-concurrent-downloads=16",
]

def get_aria2c_args():
    """獲取 aria2c 參數字串"""
    return " ".join(ARIA2C_OPTIONS)

def ensure_download_path(path: str) -> str:
    """確保下載路徑存在"""
    os.makedirs(path, exist_ok=True)
    return path

