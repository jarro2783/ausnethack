"""The mock local backend for listing recordings."""

import os
import sys

def make_url(prefix):
    '''Returns a function that makes a URL with the given prefix.'''
    def make_path_url(path):
        '''Make the URL from a path.'''
        return path, '/ttyrec/' + prefix + '/' + path

    return make_path_url


class ListFiles:
    '''List files from a local directory.'''
    def __init__(self, config):
        pass

    @staticmethod
    def backend():
        '''The backend name.'''
        return 'local'

    @staticmethod
    def list_files(name):
        '''Do the actual file listing.'''
        try:
            files = os.listdir(name)
            files.sort()
            return [make_url(name)(x) for x in files]
        except OSError:
            print("Warning: unable to list {}".format(name), out=sys.stdout)
            return []
