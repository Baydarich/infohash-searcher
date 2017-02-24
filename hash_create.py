from bencode import bdecode, bencode
from hashlib import sha1

filename = "[rutracker.org].t80349-kris.torrent"
with open(filename) as _file:
    info_hash = sha1(bencode(bdecode(_file.read())['info'])).hexdigest()
    print info_hash
