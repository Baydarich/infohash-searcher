import libtorrent
import os
# maybe switch to bencode


# torrent_list = ["[rutracker.org].t80349-kris.torrent", "kris_kaspersky.rar.torrent",
#                 "[rutracker.org].t1149720-pulp-fiction.torrent", "Pulp.Fiction.1994.BDRip-AVC.DUB.AVO.ENG.Subs.mkv.torrent",
#                 "kris_kaspersky.rar-deluge-32.torrent"]

filename_list = ["kris_kaspersky.rar"]

path = "/home/a/random_torr/torrents"

def basic_info(torrent):
    info = libtorrent.torrent_info(torrent)
    print "%s;%s;%s;%s" % (torrent, str(info.info_hash()), str(info.piece_length()), str(info.num_pieces()))

def advanced_info(torrent):
    info = libtorrent.torrent_info(torrent)
    client_names = ["utorrent", "tixati", "transmission", "deluge", "qbittorrent"]
    file_sizes = [["zero10m", 10], ["zero100m", 100], ["zero512m", 512], ["zero1024m", 1024],
                  ["zero2048m", 2048], ["zero5120m", 5120]]
    client_name = ""
    file_size = ""
    for i in range(len(client_names)):
        if client_names[i] in torrent:
            client_name = client_names[i]
            break
    for i in range(len(file_sizes)):
        if file_sizes[i][0] in torrent:
            file_size = file_sizes[i][1]
            break
    print "%s;%s;%s;%s;%s" % (client_name, str(info.info_hash()), str(info.piece_length()), str(info.num_pieces()), file_size)

def create_torrent(filename):
    fs = libtorrent.file_storage()
    libtorrent.add_files(fs, filename)
    fs.set_piece_length(32768)
    print fs.piece_length()
    #fs.set_num_pieces(367)
    t = libtorrent.create_torrent(fs)
    libtorrent.set_piece_hashes(t, ".")
    torrent = t.generate()
    newname = filename + "-lt.torrent"
    f = open(newname, "wb")
    f.write(libtorrent.bencode(torrent))
    f.close()
    print "created: " + newname
    basic_info(newname)

def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


if __name__ == "__main__":
    torrent_list = get_filepaths(path)
    # print "client_name;info_hash;piece_length;num_pieces"
    print "client_name;info_hash;piece_length;num_pieces;file_size"
    for torrent in torrent_list:
        advanced_info(torrent)

    # for file in filename_list:
    #     create_torrent(file)