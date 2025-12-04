#!/bin/bash
# Mac 打包腳本
# YouTube 影片下載器

echo "=========================================="
echo "  YouTube 下載器 - Mac 打包腳本"
echo "=========================================="

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 請先安裝 Python 3"
    exit 1
fi

# 檢查 pip
if ! command -v pip3 &> /dev/null; then
    echo "錯誤: 請先安裝 pip3"
    exit 1
fi

echo ""
echo "[1/4] 安裝 Python 依賴..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo ""
echo "[2/4] 檢查外部工具..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg 已安裝"
else
    echo "⚠ FFmpeg 未安裝，建議執行: brew install ffmpeg"
fi

if command -v aria2c &> /dev/null; then
    echo "✓ aria2c 已安裝"
else
    echo "⚠ aria2c 未安裝，建議執行: brew install aria2"
fi

echo ""
echo "[3/4] 開始打包..."
python3 -m PyInstaller build_mac.spec --clean --noconfirm

echo ""
echo "[4/4] 打包完成！"
echo ""
echo "輸出位置: dist/YouTube下載器.app"
echo ""
echo "使用方式:"
echo "  1. 將 YouTube下載器.app 拖到 應用程式 資料夾"
echo "  2. 雙擊執行"
echo ""

