import io, sys
K = "/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r"
PLT = K + "/drivers/misc/mediatek/sspm/sspm_mt6765.c"
BOX = K + "/drivers/misc/mediatek/sspm/sspm_mbox.c"

def load(p): return io.open(p, "r", encoding="utf-8", errors="surrogateescape").read()
def save(p, s): io.open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)
def rep(s, a, b, what):
    c = s.count(a)
    if c != 1:
        print("ANCHOR %s count=%d" % (what, c)); sys.exit(1)
    return s.replace(a, b, 1)

# --- 1) driver: also match cactus DT's "mediatek,sspm" ---
s = load(PLT)
if '"mediatek,sspm"' in s:
    print("PLT: already patched")
else:
    a = ('static const struct of_device_id mt6765_sspm_of_match[] = {\n'
         '\t{ .compatible = "mediatek,mt6765-sspm", },\n'
         '\t{},\n'
         '};\n')
    b = ('static const struct of_device_id mt6765_sspm_of_match[] = {\n'
         '\t{ .compatible = "mediatek,mt6765-sspm", },\n'
         '\t{ .compatible = "mediatek,sspm", }, /* cactus 4.9 DT */\n'
         '\t{},\n'
         '};\n')
    s = rep(s, a, b, "of_match")
    save(PLT, s)
    print("PLT: added mediatek,sspm")

# --- 2) sspm_mbox: NULL-base guards ---
s = load(BOX)
if "PCS null guard" in s:
    print("BOX: already guarded")
else:
    # addr
    a = ('uint32_t *sspm_mbox_addr(unsigned int mbox, unsigned int slot)\n'
         '{\n'
         '\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\treturn (uint32_t *)(desc->base + (MBOX_SLOT_SIZE * slot));\n')
    b = ('uint32_t *sspm_mbox_addr(unsigned int mbox, unsigned int slot)\n'
         '{\n'
         '\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (!desc->base) /* PCS null guard */\n'
         '\t\treturn NULL;\n'
         '\n'
         '\treturn (uint32_t *)(desc->base + (MBOX_SLOT_SIZE * slot));\n')
    s = rep(s, a, b, "addr")
    # read
    a = ('\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (data)\n'
         '\t\tmemcpy_from_sspm(data, desc->base + (MBOX_SLOT_SIZE * slot),\n')
    b = ('\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (!desc->base) /* PCS null guard */\n'
         '\t\treturn -1;\n'
         '\n'
         '\tif (data)\n'
         '\t\tmemcpy_from_sspm(data, desc->base + (MBOX_SLOT_SIZE * slot),\n')
    s = rep(s, a, b, "read")
    # write
    a = ('\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (data)\n'
         '\t\tmemcpy_to_sspm(desc->base + (MBOX_SLOT_SIZE * slot), data,\n')
    b = ('\tstruct sspm_mbox *desc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (!desc->base) /* PCS null guard */\n'
         '\t\treturn -1;\n'
         '\n'
         '\tif (data)\n'
         '\t\tmemcpy_to_sspm(desc->base + (MBOX_SLOT_SIZE * slot), data,\n')
    s = rep(s, a, b, "write")
    # polling
    a = ('\tdesc = &sspmmbox[mbox];\n'
         '\n'
         '\tirq = 0x1 << irq;\n')
    b = ('\tdesc = &sspmmbox[mbox];\n'
         '\n'
         '\tif (mbox >= sspm_mbox_cnt || !desc->in_out) /* PCS null guard */\n'
         '\t\treturn -1;\n'
         '\n'
         '\tirq = 0x1 << irq;\n')
    s = rep(s, a, b, "polling")
    save(BOX, s)
    print("BOX: guards added (addr/read/write/polling)")
print("done")
