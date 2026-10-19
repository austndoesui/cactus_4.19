# Linux 4.19 Kernel Bring-Up for MediaTek MT6765 (Xiaomi Redmi 6A / cactus)

An open-source effort to port and bring up Linux Kernel 4.19 for the Xiaomi Redmi 6A (cactus), upgrading the legacy chipset baseline from Android kernel 4.9 to modern Linux 4.19 LTS infrastructure.

This repository provides the underlying kernel source, backported drivers, and devicetrees required to boot modern Android Generic System Images (GSIs) and custom ROMs on EOL hardware.

---

## Project Status & Bring-Up Progress

* Kernel Boot: Working (Boots 4.19 baseline with custom bring-up patches)
* Display / LCM: Working (GCE / CMDQ, pinctrl/eint, mtkfb fixed)
* Backlight: Working (Resolved dead backlight issue & panel auto-detect logic)
* Touchscreen: Working (FocalTech FT5x26 bring-up completed)
* USB Subsystem: Working (USB bring-up & irq non-fatal handlers)
* Stability / Panic Watchdog: Working (Cleared late-initcall panics for GPU/SCP/thermal & stall watchdogs)
* Audio / Sound: WIP (Bring-up in progress)
* Sensors & Connectivity: WIP (Under active testing)

---

## Technical Highlights & Modifications

* Driver Backports & Re-Architecture: Adapted legacy MediaTek display (mtkfb, GCE/CMDQ) and touch driver stacks (FocalTech FT5x26) to function under Linux 4.19 kernel interfaces.
* Boot & Observability Fixes: Resolved pcs_canary memory drops during free_initmem, suppressed non-fatal MT6370 IRQ errors, and stabilized idle guard/stall watchdog routines during early boot.
* Modern GSI Support: Refactored kernel structures to ensure compatibility with modern Android HALs and Treble/GSI environments (Android 14+).

---

## Building the Kernel

### Prerequisites
* A standard Linux build host (Ubuntu 22.04 LTS or Debian recommended)
* A compatible aarch64-linux-android- or clang cross-compiler toolchain

### Quick Build Guide

export ARCH=arm64
export SUBARCH=arm64
export CROSS_COMPILE=aarch64-linux-android-

# Generate default configuration
make cactus_defconfig

# Compile kernel image
make -j$(nproc)

---

## Credits & Acknowledgments

* Base Source: Derived and backported from oppo-source/android_kernel_oppo_mt6765 baseline.
* Maintainer: [austndoesui](https://github.com/austndoesui)
