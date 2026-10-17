#!/bin/bash
set -e
P=/home/lapdq/cactus-kernel/pack
I=/home/lapdq/cactus-kernel/images
OUTF="/mnt/f/ROM/patching/kernel 4.19 6a/test.img"

# 1) compose Image.gz-dtb = our 4.19 Image.gz + cactus raw dtb
cat "$I/Image.gz" "$P/cactus_dtb.raw" > "$P/Image.gz-dtb"
echo "Image.gz-dtb size: $(wc -c < "$P/Image.gz-dtb")  (gz $(wc -c < "$I/Image.gz") + dtb $(wc -c < "$P/cactus_dtb.raw"))"

# 2) repack as header v1, matching recovery.img layout
python3 "$P/mkbootimg.py" \
  --kernel "$P/Image.gz-dtb" \
  --ramdisk "$P/twrp_ramdisk" \
  --base 0x40078000 \
  --kernel_offset 0x00008000 \
  --ramdisk_offset 0x11A88000 \
  --second_offset 0x000E8000 \
  --tags_offset 0x07808000 \
  --pagesize 2048 \
  --header_version 1 \
  --os_version 11.0.0 \
  --cmdline "bootopt=64S3,32N2,64N2 androidboot.selinux=permissive buildvariant=eng ramoops.mem_address=0x47c90000 ramoops.mem_size=0xe0000 ramoops.record_size=0x1000 ramoops.console_size=0x40000 ramoops.pmsg_size=0x10000 ramoops.ftrace_size=0x1000 ramoops.dump_oops=1 ramoops.mem_type=0 ramoops.ecc=0" \
  -o "$P/test.img"

echo "== built test.img =="
ls -la "$P/test.img"
cp -f "$P/test.img" "$OUTF"
echo "copied to: $OUTF"
