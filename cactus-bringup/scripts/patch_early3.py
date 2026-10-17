import io, sys

K = "/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r"
HS = K + "/arch/arm64/kernel/head.S"
MC = K + "/init/main.c"

def rw(p, fn):
    s = io.open(p, "r", encoding="utf-8", errors="surrogateescape").read()
    s2 = fn(s)
    if s2 != s:
        io.open(p, "w", encoding="utf-8", errors="surrogateescape").write(s2)
    return s, s2

# ---- head.S: ASM1 (after __create_page_tables) and ASM2 (start of __primary_switch) ----
src = io.open(HS, "r", encoding="utf-8", errors="surrogateescape").read()

def asm(addr, magic, tag):
    return ("\t/* PCS_ASM_MARK %s */\n"
            "\tldr\tx9, =%s\n"
            "\tldr\tx10, =%s\t/* '%s' */\n"
            "\tstr\tx10, [x9]\n") % (tag, addr, magic, tag)

if "PCS_ASM_MARK ASM1" in src:
    print("ASM1 already present")
else:
    a = "\tbl\t__create_page_tables\n"
    if a not in src:
        print("ANCHOR create_page_tables not found"); sys.exit(1)
    src = src.replace(a, a + asm("0x47d60010", "0x314d53412d534350", "PCS-ASM1"), 1)
    print("inserted ASM1")

if "PCS_ASM_MARK ASM2" in src:
    print("ASM2 already present")
else:
    a = "\n__primary_switch:\n"
    if a not in src:
        print("ANCHOR __primary_switch not found"); sys.exit(1)
    src = src.replace(a, a + asm("0x47d60020", "0x324d53412d534350", "PCS-ASM2"), 1)
    print("inserted ASM2")

io.open(HS, "w", encoding="utf-8", errors="surrogateescape").write(src)

# ---- main.c: remove the unsafe K0 canary (before paging_init) ----
m = io.open(MC, "r", encoding="utf-8", errors="surrogateescape").read()
old = '\tset_task_stack_end_magic(&init_task);\n\tpcs_canary("PCS-K0 start_kernel\\n");\n'
if old in m:
    m = m.replace(old, '\tset_task_stack_end_magic(&init_task);\n', 1)
    io.open(MC, "w", encoding="utf-8", errors="surrogateescape").write(m)
    print("removed unsafe K0 canary")
elif 'pcs_canary("PCS-K0 start_kernel\\n");' not in m:
    print("K0 already absent")
else:
    print("K0 anchor not matched exactly (leaving as-is)")

print("done")
