#!/usr/env/python

from bencode import bdecode, bencode
from hashlib import sha1
import os

keys_presented = {"private_name-utf8": 0, "private": 0, "name-utf-8": 0, "other": 0}

base_path = "/home/horn/Documents/SNE/CCF/proj/test-torrents"
files = os.listdir(base_path)
# filename2 = "kris_kaspersky.rar-deluge-32.torrent"
for j in files:
    keys_only = []
    stat = []
    total_length = 0
    with open("%s/%s" % (base_path, j)) as _file:
        info_orig = bdecode(_file.read())['info']
        try:
            stat.append((info_orig['length'], info_orig['piece length']))
        except KeyError:
            for j in info_orig['files']:
                total_length += j['length']
        try:
            del info_orig['pieces']
            del info_orig['name']
            del info_orig['files']
        except KeyError:
            pass
        try:
            del info_orig['length']
        except KeyError:
            pass
        #
        try:
            del info_orig['piece length']
        except KeyError:
            pass
        #
        if "private" in info_orig and "name.utf-8" in info_orig:
            keys_presented["private_name-utf8"] += 1
        elif "name.utf-8" in info_orig:
            keys_presented["name-utf-8"] += 1
        elif "private" in info_orig:
            keys_presented["private"] += 1
        else:
            keys_presented["other"] += 1
        for k in info_orig:
            keys_only.append(k)
        if keys_only:
            print keys_only
            # print info_orig
            # if keys_only:
            # 	print ','.join(keys_only)
            # print info_orig
            # print info_orig
            # print sha1(bencode(info_orig)).hexdigest()
print keys_presented

# with open(filename2) as _file:
# print bdecode(_file.read())['info']
# print sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
#    info_hash = sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
#    print info_hash
