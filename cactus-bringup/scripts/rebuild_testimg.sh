#!/bin/bash
set -e
O=/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r/out/arch/arm64/boot/Image.gz
I=/home/lapdq/cactus-kernel/images/Image.gz
P=/home/lapdq/cactus-kernel/pack
OUTF="/mnt/f/ROM/patching/kernel 4.19 6a/test.img"

echo "out : size=$(wc -c < "$O") sha=$(sha256sum "$O" | cut -c1-16)"
cp -f "$O" "$I"
echo "imgs: size=$(wc -c < "$I") sha=$(sha256sum "$I" | cut -c1-16)"

echo "compiling DTB from cactus_patched.dts ..."
dtc -I dts -O dtb -o "$P/cactus_dtb.raw" "$P/cactus_patched.dts" 2>/dev/null
echo "cactus_dtb.raw size: $(wc -c < "$P/cactus_dtb.raw")"

cat "$I" "$P/cactus_dtb.raw" > "$P/Image.gz-dtb"
echo "Image.gz-dtb size: $(wc -c < "$P/Image.gz-dtb")"

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
  --cmdline "bootopt=64S3,32N2,64N2 androidboot.selinux=permissive buildvariant=eng log_buf_len=8M pcsbuild=23obs pcs_deadman=8 ignore_loglevel panic=15" \
  -o "$P/test.img"

echo "test.img size: $(wc -c < "$P/test.img") kernel_size=$(python3 -c "import struct;print(struct.unpack_from('<I',open('$P/test.img','rb').read(),8)[0])")"
cp -f "$P/test.img" "$OUTF"
echo "copied -> $OUTF"
