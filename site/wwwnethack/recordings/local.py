"""The mock local backend for listing recordings."""

import os

def make_url(prefix):
    def make_path_url(path):
        return path, '/ttyrec/' + prefix + '/' + path

    return make_path_url
    

class ListFiles:
    def __init__(self, config):
        pass

    def list_files(self, name):
        try:
            files = os.listdir(name)
            files.sort()
            return map(make_url(name), files)
        except:
            return []
