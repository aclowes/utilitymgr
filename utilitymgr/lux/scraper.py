import datetime
import json
import os
import pytz

import requests

from google.cloud import storage


TOKEN_URL = 'https://connecteddevicesjci.b2clogin.com/te/' \
            'connecteddevicesjci.onmicrosoft.com/B2C_1A_SignIn/oauth2/v2.0/token'
THERMOSTAT_URL = 'https://www.myluxstat.io/api/device/runtime?deviceid={device}&currentdate={date}'


def main():
    # download access token for cloud storage
    client = storage.Client()
    bucket = client.bucket('static.yawn.live')
    blob = bucket.blob(f'utilitymgr/lux_token.json')
    tokens = json.loads(blob.download_as_text())

    # check if the access token needs to be refreshed
    headers = {
        'Authorization': f'Bearer {tokens["access_token"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://www.myluxstat.io/api/location/user', headers=headers)

    # refresh the access token if needed
    if response.status_code == 401:
        request = {
            'refresh_token': tokens['refresh_token'],
            'client_id': tokens['client_id'],
            'grant_type': 'refresh_token'
        }
        response = requests.post(TOKEN_URL, data=request)
        response.raise_for_status()
        refresh = response.json()
        tokens['access_token'] = refresh['access_token']
        tokens['refresh_token'] = refresh['refresh_token']
        blob.upload_from_string(json.dumps(tokens), content_type='application/json')
        headers['Authorization'] = f'Bearer {tokens["access_token"]}'

    # get data for each thermostat
    now = datetime.datetime.now(tz=pytz.timezone('US/Pacific')).replace(tzinfo=None).isoformat(timespec='seconds')
    for thermostat in os.environ['LUX_THERMOSTATS'].split(' '):
        url = THERMOSTAT_URL.format(device=thermostat, date=now)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(f'data/lux_{thermostat}.json', 'w') as data_file:
            data_file.write(response.text)


if __name__ == '__main__':
    main()
