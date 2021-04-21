#!/usr/bin/python

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

def expandedRead(file, pos, count):
    orig = file.tell()
    file.seek(pos)
    res = file.read(count)
    file.seek(orig)
    return res

def interpretDir(tags, types, counts, data, file):
    res = []
    tiles = []
    tileByteCounts = []
    for i in range(len(tags)):
        src = tagmap.get(tags[i], tags[i])
        dst = data[i]
        type = datatypes.get(types[i], types[i])
        if type == "ASCII":
            dst = expandedRead(file, dst, counts[i])
        if src == "TileOffsets":
            dst = expandedRead(file, dst, counts[i])
        if src == "TileByteCounts":
            dst = expandedRead(file, dst, counts[i])
        res.append(str(src) + " : " + str(dst) + " dt: " + str(type) + " len: " + str(counts[i]))
    return res

# grab a file

with open("./sample.svs", "rb") as f:
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
        tags = []
        types = []
        elem_counts = []
        datas = []

        for i in range(dir_entries):
            tags.append(int.from_bytes(f.read(2), endianness))
            types.append(int.from_bytes(f.read(2), endianness))
            elem_counts.append(int.from_bytes(f.read(4), endianness))
            datas.append(int.from_bytes(f.read(4), endianness))

        next_dir = f.read(4)
        next_dir = int.from_bytes(next_dir, endianness)
        print("offset", next_dir)
        if not next_dir:
            more_data = False
        else:
            f.seek(next_dir, 0)


        if print_dir_info:
            print("=====DIRECTORY=====")
            print("# of entries", dir_entries)
            print("\n".join(interpretDir(tags, types, elem_counts, datas, f)))

print("I found a total of " + str(dir_count) + " directories")
