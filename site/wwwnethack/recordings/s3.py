""" S3 file listing backend."""

import boto3

def make_url(bucket, strip):
    def make_url_tuple(key):
        pretty_key = key[strip:]
        return pretty_key, 'https://{}.s3.amazonaws.com/{}'.format(
            bucket, key)
    return make_url_tuple

class ListFiles:
    def __init__(self, config):
        cfg = config['S3_RECORDINGS_CONFIG']
        self.__bucket = cfg['bucket']

    def list_files(self, name):
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
        except:
            return []
