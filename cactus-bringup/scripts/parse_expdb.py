import re

P = '/mnt/c/Users/lapdq/AppData/Local/Temp/opencode/expdb.bin'
data = open(P, 'rb').read()
print('size', len(data), 'magic', hex(int.from_bytes(data[0:4], 'little')))

entries = []
off = 0x40
while off + 64 <= len(data):
    name = data[off+8:off+8+32].split(b'\0')[0]
    if not name or not re.match(rb'^[A-Za-z0-9_.]+$', name):
        break
    o = int.from_bytes(data[off+0x30:off+0x34], 'little')
    s = int.from_bytes(data[off+0x34:off+0x38], 'little')
    n2 = int.from_bytes(data[off+0x38:off+0x3c], 'little')
    entries.append((name.decode(), o, s, n2))
    off += 64

print('--- TOC (%d entries) ---' % len(entries))
for n, o, s, n2 in entries:
    print('%-24s off=0x%08x size=0x%08x (%d) size2=0x%x' % (n, o, s, s, n2))

print('--- global markers ---')
for pat in [b'Linux version', b'PCS-K', b'4.19.127', b'4.9.190', b'ramoops', b'machine_restart',
            b'Rebooting', b'Kernel panic', b'Unable to handle', b'lk version']:
    idxs = [m.start() for m in re.finditer(re.escape(pat), data)]
    print('%-18s %3d %s' % (pat.decode('latin1'), len(idxs), [hex(i) for i in idxs[:8]]))
