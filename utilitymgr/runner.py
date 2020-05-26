from google.cloud import storage

from utilitymgr.sce import scraper as sce_scraper
from utilitymgr.sce import parser as sce_parser
from utilitymgr.lux import scraper as lux_scraper
from utilitymgr.lux import parser as lux_parser


def run():
    # scrape lux
    sce_scraper.main()
    sce_parser.main()

    # scrape sce

    # generate graphs

    # upload html file
    client = storage.Client()
    bucket = client.bucket('static.yawn.live')
    blob = bucket.blob('utilitymgr/index.html')
    blob.upload_from_filename('index.html')
    blob.make_public()
    print('View the results at http://static.yawn.live/utilitymgr/')


if __name__ == '__main__':
    run()