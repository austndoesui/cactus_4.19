# TODO: GPU (PowerVR RGX) + gpufreq bring-up

**Status:** DISABLED for boot bring-up.

Disabled via `arch/arm64/configs/oppo6765_defconfig`:
```
# CONFIG_MTK_GPU_SUPPORT is not set
# CONFIG_MTK_GPU_COMMON_DVFS_SUPPORT is not set
```
(re-enable both = `y` to attempt GPU bring-up again.)

## Symptom (before disable)
Late-initcall panic, boot never reaches userspace:

```
pvr_init (late_initcall)
  -> pvr_probe -> pvr_drm_load -> PVRSRVCommonDeviceCreate -> SysDevInit
  -> MTKRGXDeviceInit
  -> mt_gpufreq_voltage_enable_set
  -> __mt_gpufreq_bucks_enable
  -> __mt_gpufreq_vcore_volt_switch
  -> mtk_pm_qos_update_request(&g_pmic->mtk_pm_vgpu, ...)
Internal error: Oops: 96000005  (x0 = 0x18 == offsetof(g_pmic_info, mtk_pm_vgpu))
Kernel panic - not syncing: Attempted to kill init! exitcode=0x0000000b
```

## Root cause
The gpufreq platform driver never initializes on cactus:
- Driver: `drivers/gpu/mediatek/gpufreq/mt6765/mtk_gpufreq_core.c`,
  compatible `mediatek,mt6765-gpufreq`, `module_init(__mt_gpufreq_init)` @2426,
  probe `__mt_gpufreq_pdrv_probe` @2154, allocates `g_pmic` @2290 and `g_clk` @~2200.
- DTB node `/gpufreq` is present, top-level and enabled (verified by DTB parse of
  `pack/cactus_dtb.raw`), with `clocks`/`clock-names` incl. `clk_mux`, `mtcmos_mfg*`.
  (No `vcore-supply` / `nvmem-cell-names` in the cactus node — in-tree ref has them.)
- Platform device IS created: device links to `10000000.topckgen` and
  `10001000.scpsys` are logged at t=0.278s, i.e. `device_link_add()`
  (`drivers/base/core.c:444`, "Linked as a consumer to ...").
- `__mt_gpufreq_init` runs at t=1.404s ("start to initialize gpufreq driver",
  `[GPU/FREQ][INFO]`), then `platform_driver_register()` — no error printed.
- BUT `__mt_gpufreq_pdrv_probe` never runs: no "gpufreq driver probe",
  no "clk_mux is at ...", no "cannot get clk_mux/..." messages anywhere.
- => `g_pmic` and `g_clk` stay NULL; the GPU DVFS path derefs them.

## Hypothesis to investigate
Probe is never started, likely blocked by device-link / fw_devlink supplier
ordering: consumer `gpufreq` waits on supplier `scpsys` (`10001000.scpsys`)
which may never probe/complete (or defers in a loop). `/gpufreq` never binds.

Investigation ideas:
- Boot with `initcall_debug` (or add `pr_err` at `__mt_gpufreq_pdrv_probe` entry
  and print `platform_driver_register()` ret) to see if the probe is skipped vs deferred.
- Check whether `scpsys` (mtk-scpsys) probes; look for `-EPROBE_DEFER` cycles.
- Inspect MTK's `device_link_add`/fw_devlink usage and whether a supplier
  (`topckgen`/`scpsys`) blocks the consumer.
- Compare with in-tree `arch/arm64/boot/dts/mediatek/mt6765.dts:2748` gpufreq node
  (has `nvmem-cells=<&efuse_segment>` + `vcore-supply=<&mt_pmic_vcore_buck_reg>`);
  consider adding the missing properties to the cactus DTB.

## Fallback if not fixable
Guard the GPU-facing gpufreq APIs against uninitialized state
(`if (!g_pmic) return;` / `if (!g_clk) return;`) in:
- `__mt_gpufreq_vcore_volt_switch()` @1421
- `__mt_gpufreq_bucks_enable/disable()` @~1586+
- `mt_gpufreq_get_cur_volt()` / `mt_gpufreq_get_cur_vsram()` @~1789
Note: `__mt_gpufreq_set()`/`__mt_gpufreq_clock_switch()` also use `g_clk`,
so guards would be needed along the whole freq+volt path.

## Related files
- `drivers/gpu/mediatek/gpufreq/mt6765/mtk_gpufreq_core.c` (init 2426, probe 2154)
- `drivers/gpu/mediatek/gpu_rgx/m1.11ED5425693/services/system/rgx_mtk/mt6765/mtk_mfgsys.c`
  (`MTKRGXDeviceInit` @1368)
- `drivers/gpu/mediatek/Makefile` (GPU build gate on `CONFIG_MTK_GPU_SUPPORT`)
- `drivers/misc/mediatek/video/*/videox/Makefile` (also keys off `CONFIG_MTK_GPU_SUPPORT`)
- DTB node `/gpufreq` in `pack/cactus_dtb.raw`; in-tree ref `mt6765.dts:2748`
