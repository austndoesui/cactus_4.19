import os, subprocess
K = "/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r"
rep = subprocess.run(
    ["find", K, "-path", K + "/out", "-prune", "-o",
     "-path", K + "/.git", "-prune", "-o", "-type", "l", "-print"],
    capture_output=True, text=True).stdout.split()

abs_links, repointed, other, missing = 0, 0, [], []
for link in abs_links if False else rep:
    tgt = os.readlink(link)
    if not os.path.isabs(tgt):
        continue
    abs_links += 1
    if not os.path.exists(tgt):
        missing.append((os.path.relpath(link, K), tgt))
        continue
    if "/peacock_mods/source/" not in tgt:
        other.append((os.path.relpath(link, K), tgt))
        continue
    rel = os.path.relpath(tgt, os.path.dirname(link))
    if rel == tgt:
        continue
    os.remove(link)
    os.symlink(rel, link)
    repointed += 1

print("absolute symlinks:", abs_links)
print("repointed to relative:", repointed)
print("missing targets:", len(missing))
for r, t in missing[:20]:
    print("  MISSING", r, "->", t)
print("other absolute (not peacock):", len(other))
for r, t in other[:20]:
    print("  OTHER", r, "->", t)
