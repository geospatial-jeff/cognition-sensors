import requests

def get_metadata(url):
    """ Convert Landsat MTL file to dictionary of metadata values """
    """https://github.com/sat-utils/sat-stac-landsat/blob/master/satstac/landsat/main.py"""

    # Read MTL file remotely
    #r = requests.get(url, stream=True)
    mtl = dict()
    #for line in r.iter_lines():
    for line in read_remote(url):
        meta = line.replace('\"', "").strip().split('=')
        if len(meta) > 1:
            key = meta[0].strip()
            item = meta[1].strip()
            if key != "GROUP" and key != "END_GROUP":
                mtl[key] = item
    return mtl


def read_remote(url):
    """ Return a line iterator for a remote file """
    r = requests.get(url, stream=True)
    """https://github.com/sat-utils/sat-stac-landsat/blob/master/satstac/landsat/main.py"""
    for line in r.iter_lines():
        yield line.decode()