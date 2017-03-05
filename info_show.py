from bencode import bdecode, bencode
from hashlib import sha1

#filename1 = "/home/a/random_torr/torrents/transmission/torr_fold.torrent"
filename1 = "/home/horn/Downloads/[rutracker.org].t5218650.torrent"
filename2 = "kris_kaspersky.rar-deluge-32.torrent"
with open(filename1) as _file:
    info_orig = bdecode(_file.read())['info']
    # info_orig.pop('name.utf-8')
    print info_orig
    print sha1(bencode(info_orig)).hexdigest()

# with open(filename2) as _file:
#     # print bdecode(_file.read())['info']
#     # print sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
#     info_hash = sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
#     print info_hash
