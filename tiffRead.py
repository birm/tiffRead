#!/usr/bin/python

import struct

# grab a file
f = open("CMU-3.svs", "rb")
#f = open("sample.svs", "rb")
# constant
res = f.read(2)
print("constant", res.hex())
# version
res = f.read(2)
print("version", res.hex())
# first offset
res = f.read(4)
first_offset = int.from_bytes(res, "little")
print("offset", first_offset)

f.seek(first_offset)
res = f.read(2)
dirs = int.from_bytes(res, "little")
print("dirs", dirs)
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
