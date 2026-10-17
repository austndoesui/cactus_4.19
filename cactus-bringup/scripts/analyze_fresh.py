import struct, re, gzip, os

FRESH = '/mnt/c/Users/lapdq/AppData/Local/Temp/opencode/expdb_fresh.bin'
OLD   = '/mnt/c/Users/lapdq/AppData/Local/Temp/opencode/expdb.bin'
IMG   = '/home/lapdq/cactus-kernel/src/kernel_oppo_4.19r/out/arch/arm64/boot/Image.gz'

d = open(FRESH, 'rb').read()
o = open(OLD, 'rb').read()

print('==== TOC (first 0x800 bytes as text-ish) ====')
hdr = d[:0x800]
for m in re.finditer(rb'[ -~]{4,}', hdr):
    print('  @0x%03x %r' % (m.start(), m.group()))

print('\n==== section name scan (whole file, unique) ====')
for name in [b'SYS_RAMCONSOLE_RAW', b'SYS_PSTORE_RAW', b'KEDUMP_CRC', b'SYS_MINI_RDUMP',
             b'PROC_CUR_TSK', b'SYS_KERNEL_LOG_RAW_0', b'SYS_RR_DESC_RAW', b'SYS_LAST_DRAM',
             b'SYS_LAST_CPU_BUS', b'SYS_LAST_SPM_DATA', b'SYS_MODULES_INFO', b'SYS_ATF',
             b'SYS_SCP_DUMP', b'DFD30']:
    hits = [hex(m.start()) for m in re.finditer(re.escape(name), d)]
    print('  %-22s %s' % (name.decode(), hits[:4]))

print('\n==== key strings in fresh expdb ====')
for s in [b'Linux version', b'4.19.127', b'4.9.190', b'TWRP', b'twrp', b'SELinux',
          b'recovery', b'init:', b'lapdq', b'oppo', b'__primary_switched',
          b'PCS-K', b'setup_arch ok', b'Kernel panic', b'Internal error',
          b'BUG:', b'Unable to handle', b'Call trace']:
    hits = [hex(m.start()) for m in re.finditer(re.escape(s), d)]
    print('  %-20s n=%d %s' % (s.decode('latin1'), len(hits), hits[:6]))

print('\n==== map KEDUMP_CRC window to Image ====')
raw = open(IMG, 'rb').read()
img = gzip.decompress(raw)
print('  Image size', len(img))
X = img.find(b'Linux version')
print('  "Linux version" in Image @ 0x%x' % X if X >= 0 else '  banner not found in Image')
F = d.find(b'Linux version')
print('  "Linux version" in expdb  @ 0x%x' % F)
if X >= 0 and F >= 0:
    KSTART = 0xe1a08
    W = X - (F - KSTART)
    print('  => KEDUMP_CRC window starts at Image offset 0x%x' % W)
    # verify with a second string
    for probe in [b'%s version %s', b'oppo6765', b'lapdq']:
        xi = img.find(probe); fi = d.find(probe)
        if xi >= 0 and fi >= 0:
            print('     probe %-14r img=0x%-8x expdb=0x%-8x delta=0x%x' % (probe, xi, fi, xi - (fi - KSTART)))
