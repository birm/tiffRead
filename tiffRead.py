#!/usr/bin/python

print_dir_info = True

# grab a file

#f = open("CMU-3.svs", "rb")
f = open("sample.svs", "rb")
#endianness
endianness = f.read(2).decode("utf-8")
if endianness == "MM":
    endianness = "big"
else:
    endianness = "little"

print("endianness", endianness)
# constant
res = f.read(2)
print("constant", res.hex())
# version
res = f.read(2)
print("version", res.hex())
# first offset
res = f.read(4)
first_offset = int.from_bytes(res, endianness)
print("offset", first_offset)


dir_count = 0

print("-", first_offset)
f.seek(first_offset, 0)
res = f.read(2)
dir_entries = int.from_bytes(res, endianness)
more_data = True

while more_data:
    dir_count += 1
    print(dir_count)
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
    if not next_dir:
        more_data = False
    else:
        f.seek(next_dir, 0)


    if print_dir_info:
        print("=====DIRECTORY=====")
        print("# of entries", dir_entries)
        print("tags", tags)
        print("types", types)
        print("counts", elem_counts)
        print("data", datas)

print("I found a total of " + str(dir_count) + " directories")

# see http://bigtiff.org/

# read file

# header
# is this tiff or bigtiff?
# bytesize of offsets, if applicable (bigtiff)
# offset to first directory

# number of directory entries

# for each one...
# datatype (TODO what do these mean??)
# elements in entry
# data -- offset or data itself
# offset to next directory, or 0
