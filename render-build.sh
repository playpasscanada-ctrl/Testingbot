#!/usr/bin/env bash
# Exit on error
set -o errexit

# Python libraries install karo
pip install -r requirements.txt

# Purani file ho toh hata do (Taaki fresh download ho)
rm -f ffmpeg-master-latest-linux64-gpl.tar.xz

# FFmpeg download karo (Added -L to follow redirects)
curl -L -O https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz

# Extract karo
tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz

# Move karo
mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg .
mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe .
