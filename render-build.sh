#!/usr/bin/env bash
# Exit on error
set -o errexit

# Python libraries install karo
pip install -r requirements.txt

# FFmpeg download aur setup karo
if [ ! -f ffmpeg-master-latest-linux64-gpl.tar.xz ]; then
    curl -O https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
fi
tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz
mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg .
mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe .
