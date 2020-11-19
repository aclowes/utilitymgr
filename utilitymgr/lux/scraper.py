import datetime
import os
import pytz

import requests

TOKEN_URL = 'https://connecteddevicesjci.b2clogin.com/te/' \
            'connecteddevicesjci.onmicrosoft.com/B2C_1A_SignIn/oauth2/v2.0/token'
TOKEN_DATA = {
    'refresh_token': os.environ['LUX_TOKEN'],
    'client_id': 'b335ca43-3bde-4406-b281-8816afb7cc91',
    'grant_type': 'refresh_token',
}
THERMOSTAT_URL = 'https://www.myluxstat.io/api/device/runtime?deviceid={device}&currentdate={date}'


def main():
    # refresh the access token
    response = requests.post(TOKEN_URL, data=TOKEN_DATA)
    response.raise_for_status()
    body = response.json()

    # setup request headers
    headers = {
        'Authorization': f'Bearer {body["access_token"]}',
        'Content-Type': 'application/json'
    }

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
