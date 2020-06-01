import datetime
import os

from google.cloud import storage

from utilitymgr.sce import scraper as sce_scraper
from utilitymgr.sce import parser as sce_parser
from utilitymgr.lux import scraper as lux_scraper
from utilitymgr.lux import parser as lux_parser


def run():
    # scrape lux
    lux_scraper.main()
    lux_parser.main()

    # scrape sce
    sce_scraper.main()
    sce_parser.main()

    # upload files
    client = storage.Client()
    bucket = client.bucket('static.yawn.live')
    upload(bucket, 'index.html')
    upload(bucket, 'data/sce.png')
    upload(bucket, 'data/lux_0.png')
    upload(bucket, 'data/lux_1.png')
    upload(bucket, 'data/lux_2.png')
    for account in os.environ['SCE_ACCOUNTS'].split(' '):
        upload(bucket, f'data/sce_{account}.xml', True)
    for thermostat in os.environ['LUX_THERMOSTATS'].split(' '):
        upload(bucket, f'data/lux_{thermostat}.json', True)
    print('View the results at http://static.yawn.live/utilitymgr/')


def upload(bucket, filename, archive=False):
    target = os.path.split(filename)[-1]
    if archive:
        target = f'archive/{datetime.date.today().isoformat()}_{filename}'
    blob = bucket.blob(f'utilitymgr/{target}')
    blob.cache_control = 'no-store'
    blob.upload_from_filename(filename)
    if not archive:
        blob.make_public()


if __name__ == '__main__':
    run()
