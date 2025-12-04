# YouTube 影片下載器

一個功能強大的 YouTube 影片下載工具，使用 PyQt6 圖形介面，支援批量下載、畫質選擇和切片加速。

## ✨ 功能特色

- 🎬 **批量下載** - 一次下載多個影片，每行一個連結
- 🎥 **畫質選擇** - 支援最高畫質、1080p、720p、480p、360p
- 📦 **MP4 + H.264** - 輸出標準 MP4 格式，確保相容性
- ⚡ **切片加速** - 使用 aria2c 多線程下載，速度更快
- 🚀 **並行下載** - 同時下載 6 部影片
- 📊 **進度顯示** - 即時顯示每個下載任務的進度、速度和剩餘時間

## 📋 系統需求

- Python 3.8+
- Windows / macOS / Linux

## 🔧 安裝依賴

### 1. Python 套件

```bash
pip install -r requirements.txt
```

### 2. 外部工具

#### FFmpeg (必要)
FFmpeg 用於影片轉碼，確保輸出為 H.264 格式。

**Windows:**
1. 下載 FFmpeg: https://github.com/BtbN/FFmpeg-Builds/releases
2. 解壓縮並將 `bin` 資料夾加入系統 PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

#### aria2c (選用，建議安裝)
aria2c 用於切片加速下載，可顯著提升下載速度。

**Windows:**
1. 下載 aria2: https://github.com/aria2/aria2/releases
2. 解壓縮並將資料夾加入系統 PATH

**macOS:**
```bash
brew install aria2
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install aria2
```

## 🚀 使用方法

### 啟動程式

```bash
python main.py
```

### 操作步驟

1. 在文字框中貼上 YouTube 連結（每行一個）
2. 選擇想要的畫質（預設為最高畫質）
3. 選擇儲存位置
4. 點擊「開始下載」

### 支援的連結格式

- `https://www.youtube.com/watch?v=xxxxx`
- `https://youtu.be/xxxxx`
- `https://www.youtube.com/playlist?list=xxxxx`

## 📁 專案結構

```
YTdownloader/
├── main.py              # 程式入口
├── downloader.py        # 下載核心模組
├── gui/
│   ├── __init__.py
│   ├── main_window.py   # 主視窗
│   └── download_item.py # 下載項目元件
├── utils/
│   ├── __init__.py
│   └── config.py        # 配置檔
├── requirements.txt     # 依賴套件
└── README.md            # 說明文件
```

## ⚙️ 配置說明

主要配置位於 `utils/config.py`:

- `MAX_CONCURRENT_DOWNLOADS` - 最大同時下載數 (預設: 6)
- `DEFAULT_DOWNLOAD_PATH` - 預設下載路徑
- `QUALITY_OPTIONS` - 畫質選項與對應的格式字串

## 🔍 常見問題

### Q: 下載速度很慢？
A: 確保已安裝 aria2c，程式會自動啟用切片加速功能。

### Q: 影片沒有聲音？
A: 確保已安裝 FFmpeg，程式需要它來合併音視訊。

### Q: 無法下載某些影片？
A: 部分影片可能有地區限制或年齡限制，請確認可以在瀏覽器中正常觀看。

## 📝 授權

MIT License

