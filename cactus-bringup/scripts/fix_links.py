#!/usr/bin/env python3
import os, subprocess

K = "/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r"
P = "/home/lapdq/cactus-kernel/src/peacock_mods/source"

out = subprocess.run(["find", K, "-xtype", "l", "-printf", "%p\t%l\n"],
                     capture_output=True, text=True).stdout.strip().split("\n")
out = [l for l in out if l]
print(f"broken symlinks: {len(out)}")

fixed, failed = [], []
for line in out:
    link, target = line.split("\t", 1)
    t = target
    while t.startswith("../"):
        t = t[3:]
    # take substring from first 'vendor/' segment
    idx = t.find("vendor/")
    rel = t[idx:] if idx >= 0 else t
    cand = os.path.join(P, rel)
    if os.path.exists(cand):
        os.remove(link)
        os.symlink(cand, link)
        fixed.append((os.path.relpath(link, K), rel))
    else:
        failed.append((os.path.relpath(link, K), rel))

print(f"FIXED: {len(fixed)}   FAILED: {len(failed)}")
for rel, t in failed:
    print(f"  FAILED {rel} -> {t}")
# verify remaining broken
rem = subprocess.run(["find", K, "-xtype", "l"], capture_output=True, text=True).stdout.strip()
print("remaining broken symlinks:", len([x for x in rem.split('\n') if x]))
