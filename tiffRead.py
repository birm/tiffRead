#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(prog="tiffRead", description='Read or Clear Tiff Fields.')
parser.add_argument('--file', dest="file", default="./sample.svs", help='tiff-like file\'s path')
parser.add_argument('--clear', dest="clear", default=False, type=int, help='Tag Number to clear')
parser.add_argument('-s', action='store_true', dest="show", help="Print directory info")
parser.add_argument('-l', dest="maxlen", default=100, type=int, help='Max Dir Entry length before truncation')
args = parser.parse_args()

print_dir_info = True

tagmap = {
254: "NewSubfileType",
256: "ImageWidth",
257: "ImageLength",
258: "BitsPerSample",
259: "Compression",
262: "PhotometricInterpretation",
270: "ImageDescription",
273: "StripOffsets",
277: "SamplesPerPixel",
278: "RowsPerStrip",
279: "StripByteCounts",
282: "XResolution",
283: "YResolution",
284: "PlanarConfiguration",
296: "ResolutionUnit",
320: "ColorMap",
322: "TileWidth",
323: "TileLength",
324: "TileOffsets",
325: "TileByteCounts",
347: "JPEGTables",
530: "YCbCrSubSampling",
32997: "ImageDepth"}

datatypes = {
1: "BYTE",
2: "ASCII",
3: "SHORT",
4: "LONG",
5: "RATIONAL",
6: "SBYTE",
7: "UNDEFINE",
8: "SSHORT",
9: "SLONG",
10: "SRATIONAL",
11: "FLOAT",
12: "DOUBLE"
}
# keep track of things to clear
toClear = []

def expandedRead(file, pos, count):
    orig = file.tell()
    file.seek(pos)
    if count < args.maxlen or args.maxlen == -1:
        res = file.read(count)
    else:
        res = file.read(args.maxlen)
    file.seek(orig)
    return res

with open(args.file, "rb") as f:
    #endianness
    endianness = f.read(2).decode("utf-8")
    if endianness == "MM":
        endianness = "big"
    elif endianness == "II":
        endianness = "little"
    else:
        raise Exception("Expecting II or MM for endianness, got: " + endianness)

    # constant
    res = f.read(2)
    constant = int.from_bytes(res, endianness)

    if not constant == 42:
        raise Exception("Expecting 42 for constant, got: " + str(constant))

    # first offset
    res = f.read(4)
    first_offset = int.from_bytes(res, endianness)
    print("offset", first_offset)


    dir_count = 0

    f.seek(first_offset, 0)
    res = f.read(2)
    dir_entries = int.from_bytes(res, endianness)
    more_data = True

    while more_data:
        dir_count += 1
        res = []

        for i in range(dir_entries):
            pos = f.tell() + 4
            tag = int.from_bytes(f.read(2), endianness)
            tagName = tagmap.get(tag, tag)
            tpe = int.from_bytes(f.read(2), endianness)
            tpe = datatypes.get(tpe, tpe)
            ec = int.from_bytes(f.read(4), endianness)
            d = int.from_bytes(f.read(4), endianness)
            method = "direct"
            if ec > 4: # is this right?
                pos = d
                d = expandedRead(f, d, ec)
                method = "expanded"
            c = {"pos": pos, "tag": tag, "tagName": tagName, "type": tpe, "len": ec, "data": d}
            res.append(c)
            # prepare for a clear
            if args.clear and tag == args.clear:
                # TODO ask for confirm maybe?
                toClear.append(c)
        next_dir = f.read(4)
        next_dir = int.from_bytes(next_dir, endianness)
        print("offset", next_dir)
        if not next_dir:
            more_data = False
        else:
            f.seek(next_dir, 0)
        if args.show:
            print("=====DIRECTORY=====")
            print("# of entries", dir_entries)
            print(res)

print("I found a total of " + str(dir_count) + " directories")

print(toClear)
# clearing time
if args.clear:
    with open(args.file, "r+b") as wf:
        for c in toClear:
            print(c)
            wf.seek(c['pos'])
            if c['type'] == "ASCII":
                l = c['len'] - 1
                wf.write(b' ' * l)
                wf.write(b'\0')
            else:
                wf.write(b'\0' * c['len'])
