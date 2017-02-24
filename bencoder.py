#!/usr/env/python

from bencode import bdecode, bencode
from hashlib import sha1

base_path = "test-torrents"
# filename2 = "kris_kaspersky.rar-deluge-32.torrent"
for j in range(1, 35):
    keys_only = []
    with open("%s/%s.torrent" % (base_path, str(j))) as _file:
        info_orig = bdecode(_file.read())['info']
        info_orig.pop('pieces')
        for k in info_orig:
            keys_only.append(k)
        print keys_only
        # print info_orig
        #    print sha1(bencode(info_orig)).hexdigest()

        # with open(filename2) as _file:
        # print bdecode(_file.read())['info']
        # print sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
        #    info_hash = sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
        #    print info_hash
