#!/bin/bash
T=/home/lapdq/cactus-kernel/toolchain
K=/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r
LOG=/home/lapdq/cactus-kernel/logs/build_run.log
DONE=/home/lapdq/cactus-kernel/logs/build.done
rm -f "$DONE"
export PATH="$T/clang-r353983c/bin:$T/aarch64-linux-android-4.9/bin:$T/arm-linux-androideabi-4.9/bin:$PATH"
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-androidkernel-
export CROSS_COMPILE_ARM32=arm-linux-androideabi-
export CLANG_TRIPLE=aarch64-linux-gnu-
cd "$K" || exit 1
# shellcheck disable=SC1091
source ./oplus_native_features.sh
echo "=== START(full build) $(date) ===" >> "$LOG"
start=$(date +%s)
make O=out ARCH=arm64 oppo6765_defconfig </dev/null >> "$LOG" 2>&1
rc1=$?
echo "=== DEFCONFIG_EXIT=$rc1 ===" >> "$LOG"
make O=out ARCH=arm64 olddefconfig </dev/null >> "$LOG" 2>&1
echo "=== OLDDEFCONFIG_EXIT=$? ===" >> "$LOG"
make O=out ARCH=arm64 -j"$(nproc)" CC=clang KCFLAGS="-Wno-missing-braces" Image.gz </dev/null >> "$LOG" 2>&1
rc=$?
end=$(date +%s)
echo "=== IMG_BUILD_EXIT=$rc elapsed=$((end-start))s $(date) ===" >> "$LOG"
echo "$rc" > "$DONE"
