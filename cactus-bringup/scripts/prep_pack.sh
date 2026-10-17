#!/bin/bash
set -e
B=/home/lapdq/cactus-kernel
mkdir -p "$B/pack" "$B/images"
# fetch AOSP mkbootimg (android11, supports header v2 + --dtb)
if [ ! -s "$B/pack/mkbootimg.py" ]; then
  curl -sL -o "$B/pack/mkbootimg.py.b64" \
    "https://android.googlesource.com/platform/system/tools/mkbootimg/+/android-11.0.0_r1/mkbootimg.py?format=TEXT"
  base64 -d "$B/pack/mkbootimg.py.b64" > "$B/pack/mkbootimg.py"
fi
echo "mkbootimg size: $(wc -c < "$B/pack/mkbootimg.py")"
head -3 "$B/pack/mkbootimg.py"
python3 "$B/pack/mkbootimg.py" --help 2>&1 | grep -iE 'header_version|--dtb|--os_version|--cmdline' | head

# stage kernel + dtbo
cp -f "$B/src/kernel_oppo_4.19r/out/arch/arm64/boot/Image.gz" "$B/images/Image.gz"
cp -f "$B/notes/stock_boot_extract/dtb" "$B/images/cactus_dtbo.img"
echo "== staged =="
ls -la "$B/images"
