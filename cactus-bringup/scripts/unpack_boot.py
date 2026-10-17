#!/usr/bin/env python3
import struct, sys, os, hashlib

def main(path, outdir):
    data = open(path, "rb").read()
    assert data[:8] == b"ANDROID!", "bad magic %r" % data[:8]
    (kernel_size, kernel_addr, ramdisk_size, ramdisk_addr,
     second_size, second_addr, tags_addr, page_size,
     header_version, os_version) = struct.unpack_from("<10I", data, 8)
    name = data[48:64].split(b"\0")[0].decode("ascii", "replace")
    cmdline = data[64:576].split(b"\0")[0].decode("ascii", "replace")
    # v1+
    (rec_dtbo_size,) = struct.unpack_from("<I", data, 1632)
    (rec_dtbo_offset,) = struct.unpack_from("<Q", data, 1636)
    (header_size,) = struct.unpack_from("<I", data, 1644)
    # v2
    (dtb_size,) = struct.unpack_from("<I", data, 1648)
    (dtb_addr,) = struct.unpack_from("<Q", data, 1652)

    print("== header ==")
    for k,v in dict(magic="ANDROID!", kernel_size=kernel_size, kernel_addr=hex(kernel_addr),
        ramdisk_size=ramdisk_size, ramdisk_addr=hex(ramdisk_addr), second_size=second_size,
        second_addr=hex(second_addr), tags_addr=hex(tags_addr), page_size=page_size,
        header_version=header_version, os_version=hex(os_version), name=name, cmdline=cmdline,
        rec_dtbo_size=rec_dtbo_size, rec_dtbo_offset=rec_dtbo_offset, header_size=header_size,
        dtb_size=dtb_size, dtb_addr=hex(dtb_addr)).items():
        print(f"  {k:16} = {v}")

    def pagesz(n): return ((n + page_size - 1)//page_size)*page_size
    off = page_size
    def grab(size, label):
        nonlocal off
        if size == 0:
            return b""
        blob = data[off:off+size]
        off += pagesz(size)
        if outdir and size:
            p = os.path.join(outdir, label)
            open(p, "wb").write(blob)
            h = hashlib.sha256(blob).hexdigest()[:16]
            print(f"  wrote {label:16} {size:>9} bytes sha256:{h}")
        return blob

    os.makedirs(outdir, exist_ok=True)
    print("== sections ==")
    grab(kernel_size, "kernel")
    grab(ramdisk_size, "ramdisk")
    grab(second_size, "second")
    if rec_dtbo_size:
        grab(rec_dtbo_size, "recovery_dtbo")
    if dtb_size:
        grab(dtb_size, "dtb")
    print("  total file size =", len(data), " consumed =", off)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
