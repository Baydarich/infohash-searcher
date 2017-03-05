#!/usr/env/python

from bencode import bdecode, bencode
import os

b = 1024 * 1024

ranges = [{1: (1, 1024 * 1024)}]
t = 1
for j in range(18):
    t = 1024 * 1024
    ranges.append({j + 2: (t * 2 ** j + 1, t * 2 ** (j + 1))})

bs = {}

# bs = {piece_length:[{ran:count}, {ran:count}]}

base_path = "/home/horn/Documents/SNE/CCF/proj/test-torrents/"
files = os.listdir(base_path)
stat = []
r = 0
for i in files:
    length = 0
    with open("%s%s" % (base_path, i)) as _file:
        info_orig = bdecode(_file.read())['info']
        piece_length = info_orig['piece length']
        try:
            length = info_orig['length']
        except KeyError:
            for j in info_orig['files']:
                length += j['length']
        finally:
            for j, k in enumerate(ranges):
                if k[j + 1][0] <= length <= k[j + 1][1]:
                    r = j + 1
                    break
            try:
                bs[piece_length][r] += 1
            except KeyError:
                try:
                    bs[piece_length][r] = 1
                except KeyError:
                    bs[piece_length] = {r: 1}


for k, v in bs.iteritems():
    print k, sorted(v, reverse=True)
print bs