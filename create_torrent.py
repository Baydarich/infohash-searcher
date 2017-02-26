import logging
import os.path
import sys
import time
from hashlib import sha1 as sha
from bencode import bdecode, bencode
import argparse

from search_dht import search_dht_hashes
from search_dht import search_dht_hashes2


noncharacter_translate = {}
ignore = ['core', 'CVS', 'Thumbs.db', 'desktop.ini']


def get_filesystem_encoding():
    return sys.getfilesystemencoding()

def decode_from_filesystem(path):
    encoding = get_filesystem_encoding()
    if encoding is None:
        assert isinstance(path, unicode), 'Path should be unicode not %s' % type(path)
        decoded_path = path
    else:
        assert isinstance(path, str), 'Path should be str not %s' % type(path)
        decoded_path = path.decode(encoding)

    return decoded_path

def makeinfo(path, piece_length, name=None, content_type=None, private=False):
    # HEREDAVE. If path is directory, how do we assign content type?
    def to_utf8(name):
        if isinstance(name, unicode):
            u = name
        else:
            try:
                u = decode_from_filesystem(name)
            except Exception:
                raise Exception('Could not convert file/directory name %r to '
                                'Unicode. Either the assumed filesystem '
                                'encoding "%s" is wrong or the filename contains '
                                'illegal bytes.' % (name, get_filesystem_encoding()))

        if u.translate(noncharacter_translate) != u:
            raise Exception('File/directory name "%s" contains reserved '
                            'unicode values that do not correspond to '
                            'characters.' % name)
        return u.encode('utf-8')
    path = os.path.abspath(path)
    piece_count = 0
    if os.path.isdir(path):
        subs = sorted(subfiles(path))
        pieces = []
        sh = sha()
        done = 0
        fs = []
        totalsize = 0.0
        totalhashed = 0
        for p, f in subs:
            totalsize += os.path.getsize(f)
        if totalsize >= piece_length:
            import math
            num_pieces = math.ceil(totalsize / piece_length)
        else:
            num_pieces = 1

        for p, f in subs:
            pos = 0
            size = os.path.getsize(f)
            p2 = [to_utf8(n) for n in p]
            if content_type:
                fs.append({'length': size, 'path': p2,
                           'content_type': content_type})  # HEREDAVE. bad for batch!
            else:
                fs.append({'length': size, 'path': p2})
            h = open(f, 'rb')
            while pos < size:
                a = min(size - pos, piece_length - done)
                sh.update(h.read(a))
                done += a
                pos += a
                totalhashed += a

                if done == piece_length:
                    pieces.append(sh.digest())
                    piece_count += 1
                    done = 0
                    sh = sha()
                    # progress(piece_count, num_pieces)
            h.close()
        if done > 0:
            pieces.append(sh.digest())
            piece_count += 1
            # progress(piece_count, num_pieces)

        if name is not None:
            assert isinstance(name, unicode)
            name = to_utf8(name)
        else:
            name = to_utf8(os.path.split(path)[1])

        # return {'pieces': ''.join(pieces),
        #         'piece length': piece_length,
        #         'files': fs,
        #         'name': name,
        #         'private': private}
        return {'pieces': ''.join(pieces),
                'piece length': piece_length,
                'files': fs,
                'name': name}
    else:
        size = os.path.getsize(path)
        if size >= piece_length:
            num_pieces = size // piece_length
        else:
            num_pieces = 1

        pieces = []
        p = 0
        h = open(path, 'rb')
        while p < size:
            x = h.read(min(piece_length, size - p))
            pieces.append(sha(x).digest())
            piece_count += 1
            p += piece_length
            if p > size:
                p = size
            # progress(piece_count, num_pieces)
        h.close()
        if content_type is not None:
            return {'pieces': ''.join(pieces),
                    'piece length': piece_length, 'length': size,
                    'name': to_utf8(os.path.split(path)[1]),
                    'content_type': content_type,
                    'private': private}
        # return {'pieces': ''.join(pieces),
        #         'piece length': piece_length, 'length': size,
        #         'name': to_utf8(os.path.split(path)[1]),
        #         'private': private}
        return {'pieces': ''.join(pieces),
                'piece length': piece_length, 'length': size,
                'name': to_utf8(os.path.split(path)[1])}


def subfiles(d):
    r = []
    stack = [([], d)]
    while stack:
        p, n = stack.pop()
        if os.path.isdir(n):
            for s in os.listdir(n):
                if s not in ignore and not s.startswith('.'):
                    stack.append((p + [s], os.path.join(n, s)))
        else:
            r.append((p, n))
    return r


def calc_hashes(info):
    info_candidates = []
    # initial variant
    info_hash = sha(bencode(info)).hexdigest()
    info_candidates.append(info_hash)

    # 1st variant
    private = False
    info_tmp = info.copy()
    info_tmp['private'] = private
    info_hash = sha(bencode(info_tmp)).hexdigest()
    info_candidates.append(info_hash)

    # 2nd variant
    private = True
    info_tmp = info.copy()
    info_tmp['private'] = private
    info_hash = sha(bencode(info_tmp)).hexdigest()
    info_candidates.append(info_hash)

    # 3rd variant
    info_tmp = info.copy()
    info_tmp['name.utf-8'] = info['name']
    info_hash = sha(bencode(info_tmp)).hexdigest()
    info_candidates.append(info_hash)

    # 4th variant
    private = False
    info_tmp = info.copy()
    info_tmp['private'] = private
    info_tmp['name.utf-8'] = info['name']
    info_hash = sha(bencode(info_tmp)).hexdigest()
    info_candidates.append(info_hash)

    # 5th variant
    private = True
    info_tmp = info.copy()
    info_tmp['private'] = private
    info_tmp['name.utf-8'] = info['name']
    info_hash = sha(bencode(info_tmp)).hexdigest()
    info_candidates.append(info_hash)

    return info_candidates


def calc_length(path):
    length = 0
    path = os.path.abspath(path)
    if os.path.isdir(path):
        subs = sorted(subfiles(path))
        for p, f in subs:
            length += os.path.getsize(f)
    else:
        length = os.path.getsize(path)
    return length


def make_query(info_candidates):
    pass


def brute_force(path):
    total_size = calc_length(path)
    if total_size < 20971520:   # 20M
        piece_length_variants = [16384, 32768, 65536]
    elif total_size < 157286400:    # 150M
        piece_length_variants = [65536, 131072, 262144]
    elif total_size < 576716800:    # 550M
        piece_length_variants = [524288, 1048576, 262144]
    elif total_size < 1572864000:    # 1500M
        piece_length_variants = [1048576, 2097152, 524288]
        # piece_length_variants = [2097152,1048576, 524288]
    elif total_size < 2621440000:    # 2500M
        piece_length_variants = [2097152, 1048576, 4194304]
    elif total_size < 5767168000:  # 5500M
        piece_length_variants = [2097152, 4194304, 8388608]
    else:
        piece_length_variants = [8388608, 4194304, 16777216]

    for piece_length in piece_length_variants:
        info = makeinfo(path, piece_length)
        info_candidates = calc_hashes(info)

        # debug
        print info_candidates
        print

        result = search_dht_hashes2(info_candidates)
        if result:
            return result

        result = make_query(info_candidates)
        if result:
            return result

    return "No matches found"


if __name__ == "__main__":
    # path = "/home/a/random_torr/zero1024m"

    #parser = argparse.ArgumentParser(description="This program calculates different info hashes of given files and searches them in database or DHT")
    #parser.add_argument("filelist", help="Specify a file containing list of paths to calculate info hashes and compare")
    #parser.add_argument("-d", "--dht", action="store_true", default=False, help="Search info hashes in DHT as well")
    #args = parser.parse_args()
    #filelist = args.filelist

    #print filelist

    #if args.dht == True:
    #    print "search in DHT"

    path = "/home/a/PycharmProjects/torrents/Pulp.Fiction.1994.BDRip-AVC.DUB.AVO.ENG.Subs.mkv"
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        print "Please specify a file or folder to inspect"
        # sys.exit()
    print brute_force(path)
