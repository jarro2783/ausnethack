""" S3 file listing backend."""

import boto3
import botocore
import sys
import traceback

def make_url(bucket, strip):
    '''Return a function to make an amazon s3 url.'''
    def make_url_tuple(key):
        '''Makes an s3 url given a bucket name.'''
        pretty_key = key[strip:]
        return pretty_key, 'https://{}.s3.amazonaws.com/{}'.format(
            bucket, key)
    return make_url_tuple

class ListFiles:
    '''Class to list the files in a recordings bucket.'''
    def __init__(self, config):
        cfg = config['S3_RECORDINGS_CONFIG']
        self.__bucket = cfg['bucket']

    def list_files(self, name):
        '''List the recordings.'''
        try:
            client = boto3.client('s3')
            response = client.list_objects(
                Bucket=self.__bucket,
                Prefix=name)

            recordings = []
            for result in response['Contents']:
                recordings.append(result['Key'])

            return map(
                make_url(
                    self.__bucket,
                    len(name)+1),
                sorted(recordings))
        except botocore.exceptions.ClientError as err:
            print(err, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return []
