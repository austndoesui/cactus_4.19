#!/bin/bash
set -e
K=/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r
P=/home/lapdq/cactus-kernel/pack
OUT="/mnt/f/ROM/patching/kernel 4.19 6a"
KIMG=$K/out/arch/arm64/boot/Image.gz
CDTB=$P/cactus_dtb.raw
ODTB=$K/out/arch/arm64/boot/dts/mediatek/mt6765.dtb
RD=$P/twrp_ramdisk
CMDLINE="bootopt=64S3,32N2,64N2 androidboot.selinux=permissive buildvariant=eng"

echo "Image.gz=$(wc -c < "$KIMG")  cactus_dtb=$(wc -c < "$CDTB")  oppo_dtb=$(wc -c < "$ODTB")"

cat "$KIMG" "$CDTB" > "$P/canny_cactus.gz"
cat "$KIMG" "$ODTB" > "$P/canny_oppo.gz"

python3 "$P/mkbootimg.py" --kernel "$P/canny_cactus.gz" --ramdisk "$RD" \
  --base 0x40078000 --kernel_offset 0x00008000 --ramdisk_offset 0x11A88000 \
  --second_offset 0x000E8000 --tags_offset 0x07808000 --pagesize 2048 \
  --header_version 1 --os_version 11.0.0 --cmdline "$CMDLINE" \
  -o "$P/test_canary.img"

python3 "$P/mkbootimg.py" --kernel "$P/canny_oppo.gz" --ramdisk "$RD" \
  --base 0x40078000 --kernel_offset 0x00008000 --ramdisk_offset 0x11A88000 \
  --second_offset 0x000E8000 --tags_offset 0x07808000 --pagesize 2048 \
  --header_version 1 --os_version 11.0.0 --cmdline "$CMDLINE" \
  -o "$P/test_canary_oppo.img"

echo "test_canary.img=$(wc -c < "$P/test_canary.img")  test_canary_oppo.img=$(wc -c < "$P/test_canary_oppo.img")"
cp -f "$P/test_canary.img" "$OUT/test.img"
cp -f "$P/test_canary_oppo.img" "$OUT/test_oppo.img"
echo "copied to $OUT"
