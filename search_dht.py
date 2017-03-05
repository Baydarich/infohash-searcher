# http://stackoverflow.com/questions/32866890/creating-daemon-using-python-libtorrent-for-fetching-meta-data-of-100k-torrents

import libtorrent as lt # libtorrent library
import tempfile # for settings parameters while fetching metadata as temp dir
from time import sleep #sleep
import time
import shutil # removing directory tree from temp directory

import btdht
import binascii

def search_dht_hashes(hashes):
    session = lt.session(lt.fingerprint("UT", 3, 4, 5, 0), flags=0)
    session.listen_on(6881, 6891)
    session.add_extension('ut_metadata')
    session.add_extension('ut_pex')
    # session.add_extension('smart_ban')
    session.add_extension('metadata_transfer')

    session.add_dht_router("router.utorrent.com", 6881)
    session.add_dht_router("router.bittorrent.com", 6881)
    session.add_dht_router("dht.transmissionbt.com", 6881)
    session.add_dht_router("dht.aelitis.com", 6881)

    session.start_dht()
    session.start_lsd()
    session.start_upnp()
    session.start_natpmp()

    #hashes = ['1468A075C7AE4936572C39E2E5D4640659D634E2']
    handles = []

    for hash in hashes:
        tempdir = tempfile.mkdtemp()
        add_magnet_uri_params = {
            'save_path': tempdir,
            # 'duplicate_is_error': True,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        magnet_uri = "magnet:?xt=urn:btih:" + hash.upper()
        #magnet_uri = "magnet:?xt=urn:btih:" + hash.upper() + "&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80"
        handle = lt.add_magnet_uri(session, magnet_uri, add_magnet_uri_params)
        handles.append(handle) #push handle in handles list


    torr_info = {}
    while(len(handles) != 0):
        for h in handles:
            if h.has_metadata():
                info = h.get_torrent_info()
                info_hash = str(info.info_hash())
                name = str(info.name())
                piece_length = info.piece_length()
                torr_info = {'name': name, 'info hash': info_hash, 'piece length': piece_length}
                shutil.rmtree(h.save_path())

                session.stop_dht()
                session.stop_lsd()
                session.stop_upnp()
                session.stop_natpmp()

                return torr_info

            elif h.status().has_incoming:
                print "found"

            elif h.status().list_peers != 0:
                print "found"

            elif h.status().connect_candidates != 0:
                print "found"

            else:
                if(h.status().active_time > 100):   # check if handle is more than 100 seconds
                    # shutil.rmtree(h.save_path())    #   remove temp data directory
                    session.remove_torrent(h) # remove torrnt handle from session
                    handles.remove(h) #remove handle from list
            sleep(1)

    session.stop_dht()
    session.stop_lsd()
    session.stop_upnp()
    session.stop_natpmp()

    return torr_info



def search_dht_hashes2(hashes):
    dht = btdht.DHT()
    dht.start()
    print "bootstrapping for 15 seconds"
    sleep(15)

    print "searching hashes"
    attempts = 10
    for i in range(attempts):
        for hash in hashes:
            peers = dht.get_peers(binascii.a2b_hex(hash), 0, False)
            if peers:
                # print peers
                dht.stop()
                return hash
        sleep(2)

    dht.stop()
    return False


def test():
    a = ['a3924d99366463f8fdb9647afafbf60b0b111f63']

    time1 = time.time()
    print search_dht_hashes2(a)
    print time.time() - time1

    a = ['3bdbf004d0be3a74316cb4664b7b9234ff4e9932', 'a973220f1ad8db879dfbac1500e9ffe1ea58f709',
         '085030a8573b228d2bfa54c4c90fb95a19bd0383', '79f30f02f3a18ed6e45b4b9323ed082c94b26a70',
         '1468A075C7AE4936572C39E2E5D4640659D634E3', '1468A075C7AE4936572C39E2E5D4640659D634E4']

    time1 = time.time()
    print search_dht_hashes2(a)
    print time.time() - time1


    a = ['1468A075C7AE4936572C39E2E5D4640659D634E4', 'a973220f1ad8db879dfbac1500e9ffe1ea58f709',
         '085030a8573b228d2bfa54c4c90fb95a19bd0383', '79f30f02f3a18ed6e45b4b9323ed082c94b26a70',
         '1468A075C7AE4936572C39E2E5D4640659D634E3', '7ef0145bc19f53251df9ff7e11a795e9e088b65c']

    time1 = time.time()
    print search_dht_hashes2(a)
    print time.time() - time1


if __name__ == "__main__":
    test()