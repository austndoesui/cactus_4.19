#!/bin/bash
set -e
P=/home/lapdq/cactus-kernel/pack
OUTF="/mnt/f/ROM/patching/kernel 4.19 6a/test_stock.img"

# kernel = stock TWRP Image.gz + cactus raw dtb appended (same layout as stock recovery)
cat "$P/twrp_kernel.gz" "$P/cactus_dtb.raw" > "$P/twrp_kernel_dtb.gz"
echo "twrp_kernel_dtb.gz size: $(wc -c < "$P/twrp_kernel_dtb.gz")"

python3 "$P/mkbootimg.py" \
  --kernel "$P/twrp_kernel_dtb.gz" \
  --ramdisk "$P/twrp_ramdisk" \
  --base 0x40078000 \
  --kernel_offset 0x00008000 \
  --ramdisk_offset 0x11A88000 \
  --second_offset 0x000E8000 \
  --tags_offset 0x07808000 \
  --pagesize 2048 \
  --header_version 1 \
  --os_version 11.0.0 \
  --cmdline "bootopt=64S3,32N2,64N2 androidboot.selinux=permissive buildvariant=eng" \
  -o "$P/test_stock.img"
echo "test_stock.img size: $(wc -c < "$P/test_stock.img")"
cp -f "$P/test_stock.img" "$OUTF"
echo "copied -> $OUTF"
