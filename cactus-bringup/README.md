# cactus_4.19 — Redmi 6A (MT6765) kernel bring-up

Working port of the **OPPO/ColorOS 11.1.4 (Android 11) MediaTek MT6765 kernel** to the
**Xiaomi Redmi 6A** (codename `cactus`), developed and tested on real hardware using
**TWRP on the recovery partition** as a non-destructive boot harness.

This repository is the upstream OPPO source tree plus our bring-up patches. The branch
`main` is based on OPPO's `oppo/mt6765_r_11.1.4_a16` history so the change set stays
auditable against the vendor drop.

---

## Sources / provenance

| Item | Value |
|------|-------|
| Upstream kernel | https://github.com/oppo-source/android_kernel_oppo_mt6765 |
| Upstream branch | `oppo/mt6765_r_11.1.4_a16` |
| Upstream commit | `220d8e1a7` — "Synchronize codes for OPPO A16/A16s/A16k/A16e/A54 ColorOS11.1.4" |
| Kernel version | Linux `4.19.127` |
| Vendor source drop | `peacock_mods/source` (OPPO/oplus `vendor/oplus/...` trees) |

The OPPO tree contains ~57 **symlinks** into OPPO-internal `vendor/oplus/...` paths that
are not part of the public drop. In our working tree these are repointed as **relative
symlinks** to a sibling checkout at `../peacock_mods/source/...`. As a result this repo
does **not build standalone**; you must place a compatible vendor source drop next to the
kernel tree (see *Layout*).

---

## Device

| Item | Value |
|------|-------|
| Device | Xiaomi Redmi 6A |
| Codename | `cactus` |
| SoC | MediaTek MT6765 (reported as `MT6762V/CN`), octa-core Cortex-A53 |
| Bootloader | MTK LK (locked/verified boot caveats apply) |

---

## Layout

```
kernel_oppo_4.19r/          # this kernel tree (repo root)
../peacock_mods/source/     # vendor/oplus source drop, referenced by the relative symlinks
cactus-bringup/
  README.md                 # this file
  scripts/                  # build / pack / patch / capture tooling
  notes/                    # device config + DTBO decompiles
```

---

## Toolchain

Builds use the AOSP MTK clang toolchain plus GNU 4.9 assemblers/linkers:

* `clang-r353983c` (AOSP prebuilt)
* `aarch64-linux-android-4.9` (`CROSS_COMPILE`)
* `arm-linux-androideabi-4.9` (`CROSS_COMPILE_ARM32`), GNU `ld` 2.27

Environment contract used by `scripts/build_only.sh` / `scripts/build_full.sh`:

```
ARCH=arm64
CLANG_TRIPLE=aarch64-linux-gnu-
CROSS_COMPILE=aarch64-linux-androidkernel-
CROSS_COMPILE_ARM32=arm-linux-androideabi-
KCFLAGS="-Wno-missing-braces"
```

The OPLUS build glue must be sourced before `make`:

```
source ./oplus_native_features.sh
```

(a symlink `src/kernel-4.19 -> kernel_oppo_4.19r` is expected by the OPLUS scripts).

---

## Building

Defconfig: `oppo6765_defconfig`. Build target: `Image.gz`.

```
# full build (also regenerates the OPPO DTB)
scripts/build_full.sh

# incremental kernel-only build
scripts/build_only.sh
```

Both write `arch/arm64/boot/Image.gz` and drop a completion marker in `logs/build.done`.

---

## Packaging & boot harness

We never touch the `boot`/`system` partitions. The harness repacks **cactus stock TWRP**
(`twrp_kernel.gz` + `twrp_ramdisk` + `cactus_dtb.raw`) with our kernel as the boot image:

```
scripts/rebuild_testimg.sh     # -> test.img   (Image.gz-dtb + twrp_ramdisk)
```

`mkbootimg` v1 parameters:

```
--base            0x40078000
--kernel_offset   0x8000
--ramdisk_offset  0x11A88000
--second_offset   0xE8000
--tags_offset     0x7808000
--pagesize        2048
```

### Boot command (important)

On this MTK LK, `fastboot boot <img>` and `fastboot reboot recovery` are **no-ops**.
The recovery partition is booted with:

```
fastboot flash recovery test.img
fastboot oem reboot-recovery
```

---

## Crash capture (no UART/serial)

There is no serial console. Early-boot evidence is captured from the MTK **`expdb`**
partition, snapshotted by LK at crash/next boot:

```
# device in TWRP
adb exec-out cat /dev/block/platform/bootdevice/by-name/expdb > expdb.bin
python3 scripts/parse_expdb.py expdb.bin
```

Clean-capture protocol: flash `test.img` → `fastboot oem reboot-recovery` (crash) →
restore stock TWRP → boot TWRP → pull `expdb`. Because TWRP boots through the same
kernel path, this must be done before any clean reboot or markers get overwritten.

Boot progress is additionally tracked with in-kernel markers written to reserved RAM
(`arch/arm64/kernel/head.S`: `PCS_STEP` counter + `PCS-ASM0/1/2`), which persist into
the `expdb`/ramoops snapshot.

---

## Current status

* Kernel now boots through `start_kernel`, most of `init`, and into the **idle loop**.
* Boot markers in `head.S` confirm execution reaches `PCS_STEP = 9` and `PCS-ASM2`.
* **Fixed (verification pending):** a ~6.5 s idle-path panic
  `Unable to handle kernel read ... at 0000000000000028`,
  `pc : memcpy_from_sspm+0x34`, `lr : sspm_mbox_read+0x50`, reached via
  `mcdi_heart_beat_log_dump → menu_reflect → cpuidle_reflect → do_idle → start_kernel`.
  Root cause: the 4.19 SSPM platform driver (`sspm_mt6765.c`) matches only
  `mediatek,mt6765-sspm`, but the cactus DT node uses `mediatek,sspm`, so the driver
  never probed and `sspmmbox[].base == NULL`. See *Applied patches*.
* Not yet functional: display, touch, storage, and full userspace bring-up.

---

## Applied patches (vs upstream)

| File | Change |
|------|--------|
| `arch/arm64/kernel/head.S` | `PCS_STEP` progress-counter macro + `PCS-ASM0/1/2` markers |
| `init/main.c` | `pcs_canary` K1–K4 checkpoints; removed `K0` (faulted before `paging_init()`) |
| `drivers/misc/mediatek/sspm/sspm_mt6765.c` | also match `mediatek,sspm` (cactus 4.9 DT binding) |
| `drivers/misc/mediatek/sspm/sspm_mbox.c` | NULL-`base` guards in `addr`/`read`/`write`/`polling` |
| `fs/pstore/ram.c` | ramoops tuning used for capture |
| (symlinks) | 57 `vendor/oplus/...` symlinks repointed to relative `../peacock_mods/source/...` |

---

## TODO

- [ ] Verify the SSPM/MCDI fix boots past 6.5 s (repeat clean expdb capture).
- [ ] Bring up cactus hardware under 4.19: display (mtkfb), touchscreen, UFS/eMMC storage.
- [ ] Port remaining 4.9 → 4.19 device-tree bindings (SSPM was the first mismatch).
- [ ] Full Android userspace bring-up (init, mount `system`/`vendor`, boot to UI).
- [ ] Remove debug markers/canaries once stable.

---

## Disclaimer

Kernel source is **GPLv2**; vendor additions remain the property of their respective
owners. This is a personal, non-commercial bring-up project. Flash at your own risk.
