import datetime
import os
import traceback

from google.cloud import storage

from utilitymgr import ecobee
from utilitymgr import emporia


def run():
    print('Fetching ecobee')
    try:
        ecobee.main()
    except:  # noqa
        traceback.print_exc()

    print('Fetching Emporia')
    try:
        emporia.main()
    except:  # noqa
        traceback.print_exc()

    # upload files
    print('Uploading data')
    client = storage.Client()
    bucket = client.bucket('static.yawn.live')
    upload(bucket, 'index.html')
    upload(bucket, 'data/emporia.png')
    for index in range(3):
        upload(bucket, f'data/ecobee_{index}.png')
    upload(bucket, 'data/emporia.json', True)
    upload(bucket, 'data/ecobee.json', True)
    print('View the results at http://static.yawn.live/utilitymgr/')


def upload(bucket, filename, archive=False):
    target = os.path.split(filename)[-1]
    if archive:
        target = f'archive/{datetime.date.today().isoformat()}_{filename}'
    blob = bucket.blob(f'utilitymgr/{target}')
    blob.cache_control = 'no-store'
    try:
        blob.upload_from_filename(filename)
        if not archive:
            blob.make_public()
    except:  # noqa
        traceback.print_exc()


if __name__ == '__main__':
    run()
