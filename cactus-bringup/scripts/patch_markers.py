import io, sys

HS = "/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r/arch/arm64/kernel/head.S"
src = io.open(HS, "r", encoding="utf-8", errors="surrogateescape").read()

BUILD = b"PCSB0007"
TAGVAL = "0x%016x" % int.from_bytes(BUILD, "little")

if "PCS_STEP" in src:
    print("PCS_STEP already present -> re-run aborted")
    sys.exit(0)

def rep(anchor, repl, s, n=1):
    c = s.count(anchor)
    if c != 1:
        print("ANCHOR NOT UNIQUE (%d): %r" % (c, anchor)); sys.exit(1)
    return s.replace(anchor, repl, 1)

# 1) macro definition just before ENTRY(stext)
macro = ("\t.macro\tPCS_STEP num\n"
         "\tldr\tx9, =0x47d60018\n"
         "\tmov\tx10, #\\num\n"
         "\tstr\tx10, [x9]\n"
         "\t.endm\n\n")
src = rep("ENTRY(stext)\n", macro + "ENTRY(stext)\n", src)

# 2) extend ASM0 block: build tag + step 1
asm0 = ("\tldr\tx9, =0x47d60000\n"
        "\tldr\tx10, =0x304d53412d534350\t/* 'PCS-ASM0' */\n"
        "\tstr\tx10, [x9]\n"
        "\tstr\tx0, [x9, #8]\n")
if asm0 not in src:
    print("ASM0 block not found"); sys.exit(1)
add0 = ("\tldr\tx10, =%s\t/* '%s' build tag */\n"
        "\tstr\tx10, [x9, #0x28]\n"
        "\tPCS_STEP 1\n") % (TAGVAL, BUILD.decode())
src = rep(asm0, asm0 + add0, src)

# 3) progressive steps (anchors disambiguated)
src = rep("\tbl\tpreserve_boot_args\n",
          "\tbl\tpreserve_boot_args\n\tPCS_STEP 2\n", src)
src = rep("\tbl\tel2_setup\t\t\t// Drop to EL1, w0=cpu_boot_mode\n\tadrp\tx23, __PHYS_OFFSET\n",
          "\tbl\tel2_setup\t\t\t// Drop to EL1, w0=cpu_boot_mode\n\tPCS_STEP 3\n\tadrp\tx23, __PHYS_OFFSET\n", src)
src = rep("\tbl\tset_cpu_boot_mode_flag\n\tbl\t__create_page_tables\n",
          "\tbl\tset_cpu_boot_mode_flag\n\tPCS_STEP 4\n\tbl\t__create_page_tables\n", src)
src = rep("\tbl\t__create_page_tables\n\t/* PCS_ASM_MARK PCS-ASM1 */\n",
          "\tbl\t__create_page_tables\n\tPCS_STEP 5\n\t/* PCS_ASM_MARK PCS-ASM1 */\n", src)
src = rep("__create_page_tables:\n\tmov\tx28, lr\n",
          "__create_page_tables:\n\tmov\tx28, lr\n\tPCS_STEP 6\n", src)
src = rep("\tsubs\tx1, x1, #64\n\tb.ne\t1b\n",
          "\tsubs\tx1, x1, #64\n\tb.ne\t1b\n\tPCS_STEP 7\n", src)
src = rep("\tmap_memory x0, x1, x3, x6, x7, x3, x4, x10, x11, x12, x13, x14\n",
          "\tmap_memory x0, x1, x3, x6, x7, x3, x4, x10, x11, x12, x13, x14\n\tPCS_STEP 8\n", src)
src = rep("\tmap_memory x0, x1, x5, x6, x7, x3, x4, x10, x11, x12, x13, x14\n",
          "\tmap_memory x0, x1, x5, x6, x7, x3, x4, x10, x11, x12, x13, x14\n\tPCS_STEP 9\n", src)

io.open(HS, "w", encoding="utf-8", errors="surrogateescape").write(src)
print("patched: macro + ASM0 tag + steps 1..9")
