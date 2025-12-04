# -*- coding: utf-8 -*-
"""
yt-dlp 下載核心模組
"""
import os
import shutil
import glob
from typing import Callable, Optional
import yt_dlp

from utils.config import QUALITY_OPTIONS, ARIA2C_OPTIONS, ensure_download_path


def get_aria2c_path() -> str:
    """獲取 aria2c 可執行檔路徑"""
    # 首先檢查系統 PATH
    system_aria2c = shutil.which('aria2c')
    if system_aria2c:
        return system_aria2c
    
    # 搜尋常見安裝位置
    search_paths = [
        # WinGet 安裝位置
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\aria2*\*\aria2c.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\aria2*\*\aria2c.EXE'),
        # Chocolatey 安裝位置
        r'C:\ProgramData\chocolatey\bin\aria2c.exe',
        # Scoop 安裝位置
        os.path.expandvars(r'%USERPROFILE%\scoop\apps\aria2\current\aria2c.exe'),
        # 手動安裝位置
        r'C:\Program Files\aria2\aria2c.exe',
        r'C:\aria2\aria2c.exe',
    ]
    
    for pattern in search_paths:
        matches = glob.glob(pattern)
        if matches:
            for match in matches:
                if os.path.isfile(match):
                    return match
    
    return None


def setup_aria2c_env():
    """設置 aria2c 環境變數"""
    aria2c_path = get_aria2c_path()
    if aria2c_path:
        aria2c_dir = os.path.dirname(aria2c_path)
        if aria2c_dir:
            current_path = os.environ.get('PATH', '')
            if aria2c_dir not in current_path:
                os.environ['PATH'] = aria2c_dir + os.pathsep + current_path
        return aria2c_path
    return None


def get_ffmpeg_path() -> str:
    """獲取 FFmpeg 可執行檔路徑"""
    # 首先檢查系統 PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg
    
    # 嘗試使用 imageio-ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
    except ImportError:
        pass
    
    return None


def setup_ffmpeg_env():
    """設置 FFmpeg 環境變數，並確保 ffmpeg.exe 存在"""
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return None
        
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    ffmpeg_basename = os.path.basename(ffmpeg_path)
    
    # 如果 FFmpeg 檔名不是標準的 ffmpeg.exe，創建一個副本
    if ffmpeg_basename.lower() != 'ffmpeg.exe':
        standard_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        if not os.path.exists(standard_path):
            try:
                shutil.copy2(ffmpeg_path, standard_path)
                print(f"已創建 ffmpeg.exe: {standard_path}")
            except Exception as e:
                print(f"無法創建 ffmpeg.exe 副本: {e}")
    
    # 將 FFmpeg 目錄加入 PATH
    if ffmpeg_dir:
        current_path = os.environ.get('PATH', '')
        if ffmpeg_dir not in current_path:
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + current_path
    
    return ffmpeg_dir


class VideoDownloader:
    """影片下載器類別"""
    
    def __init__(
        self,
        url: str,
        output_path: str,
        quality: str = "最高畫質",
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        use_aria2c: bool = True
    ):
        self.url = url
        self.output_path = ensure_download_path(output_path)
        self.quality = quality
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.use_aria2c = use_aria2c
        self.video_title = ""
        self._cancelled = False
        
    def _progress_hook(self, d: dict):
        """進度回調處理"""
        if self._cancelled:
            raise Exception("下載已取消")
            
        if d['status'] == 'downloading':
            # 計算進度百分比
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                percent = 0
                
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            
            if self.progress_callback:
                self.progress_callback({
                    'percent': percent,
                    'downloaded': downloaded,
                    'total': total,
                    'speed': speed,
                    'eta': eta,
                    'filename': d.get('filename', ''),
                    'status': 'downloading'
                })
                
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback({
                    'percent': 100,
                    'status': 'processing',
                    'filename': d.get('filename', '')
                })
                
    def _check_aria2c(self) -> bool:
        """檢查 aria2c 是否可用"""
        return get_aria2c_path() is not None
    
    def _check_ffmpeg(self) -> bool:
        """檢查 ffmpeg 是否可用"""
        return get_ffmpeg_path() is not None
        
    def get_video_info(self) -> dict:
        """獲取影片資訊"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            self.video_title = info.get('title', 'Unknown')
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
            }
    
    def download(self) -> bool:
        """執行下載"""
        try:
            if self.status_callback:
                self.status_callback("正在獲取影片資訊...")
                
            # 獲取影片資訊
            info = self.get_video_info()
            
            if self.status_callback:
                self.status_callback(f"開始下載: {info['title']}")
            
            # 構建 yt-dlp 選項
            format_string = QUALITY_OPTIONS.get(self.quality, QUALITY_OPTIONS["最高畫質"])
            
            # 設置 FFmpeg 環境
            ffmpeg_dir = setup_ffmpeg_env()
            
            ydl_opts = {
                'format': format_string,
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'merge_output_format': 'mp4',
                'quiet': False,
                'no_warnings': False,
                'ignoreerrors': False,
                # 後處理：確保轉換為 H.264 + AAC 格式
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                }],
                # 全局 FFmpeg 輸出參數：強制轉換音頻為 AAC
                'postprocessor_args': [
                    '-c:v', 'copy',         # 視訊直接複製（不重新編碼）
                    '-c:a', 'aac',          # 音訊轉換為 AAC
                    '-b:a', '192k',         # 音訊比特率
                    '-strict', 'experimental',
                    '-movflags', '+faststart'
                ],
            }
            
            # 設置 FFmpeg 路徑
            if ffmpeg_dir:
                ydl_opts['ffmpeg_location'] = ffmpeg_dir
            
            # 檢查 aria2c 是否可用
            aria2c_available = self._check_aria2c()
            
            # 如果 aria2c 可用且啟用，使用 aria2c 進行下載加速
            if self.use_aria2c and aria2c_available:
                ydl_opts['external_downloader'] = 'aria2c'
                ydl_opts['external_downloader_args'] = {
                    'aria2c': ARIA2C_OPTIONS
                }
                if self.status_callback:
                    self.status_callback("使用 aria2c 加速下載中...")
            else:
                if self.status_callback:
                    if not aria2c_available:
                        self.status_callback("aria2c 未找到，使用預設下載器...")
                    else:
                        self.status_callback("下載中...")
            
            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                
            if self.status_callback:
                self.status_callback("下載完成!")
                
            if self.progress_callback:
                self.progress_callback({
                    'percent': 100,
                    'status': 'completed'
                })
                
            return True
            
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"下載失敗: {str(e)}")
            if self.progress_callback:
                self.progress_callback({
                    'percent': 0,
                    'status': 'error',
                    'error': str(e)
                })
            return False
    
    def cancel(self):
        """取消下載"""
        self._cancelled = True


def check_dependencies() -> dict:
    """檢查外部依賴"""
    # 設置環境
    setup_ffmpeg_env()
    setup_aria2c_env()
    
    return {
        'ffmpeg': get_ffmpeg_path() is not None,
        'aria2c': get_aria2c_path() is not None,
    }

