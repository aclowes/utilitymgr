import datetime
import json

import matplotlib.pyplot as plt
import pandas as pd
import pytz
import requests
from google.cloud import storage

from utilitymgr import utils

# seeded once by `bootstrap_auth.py emporia`, then refreshed on every run
TOKEN_BLOB = 'utilitymgr/emporia_token.json'
COGNITO_URL = 'https://cognito-idp.us-east-2.amazonaws.com/'
API_URL = 'https://api.emporiaenergy.com'
MAINS = '1,2,3'
MAX_RANGE = datetime.timedelta(hours=168)
PACIFIC = pytz.timezone('US/Pacific')


def main():
    bucket = storage.Client().bucket('static.yawn.live')
    id_token = authenticate(bucket)
    headers = {'authtoken': id_token}

    response = requests.get(f'{API_URL}/customers/devices', headers=headers)
    response.raise_for_status()
    devices = response.json()['devices']

    start, end = (
        PACIFIC.localize(datetime.datetime.combine(day, datetime.time())).astimezone(pytz.utc)
        for day in utils.week_start_end()
    )
    # the API rejects 15 minute ranges over 168h (DST weeks are 169h); stop at now
    end = min(end, datetime.datetime.now(pytz.utc).replace(microsecond=0))
    start = max(start, end - MAX_RANGE)
    usage = {}
    for device in devices:
        if not any(channel['channelNum'] == MAINS for channel in device['channels']):
            continue
        name = device.get('locationProperties', {}).get('deviceName') or str(device['deviceGid'])
        usage[name] = chart_usage(headers, device['deviceGid'], start, end)
    with open('data/emporia.json', 'w') as data_file:
        json.dump(usage, data_file)
    plot(usage, 'data/emporia.png')


def authenticate(bucket):
    """Exchange the stored Cognito refresh token for an id token (valid 1 hour)."""
    blob = bucket.blob(TOKEN_BLOB)
    tokens = json.loads(blob.download_as_text())
    response = requests.post(
        COGNITO_URL,
        headers={
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
        },
        json={
            'AuthFlow': 'REFRESH_TOKEN_AUTH',
            'ClientId': tokens['client_id'],
            'AuthParameters': {'REFRESH_TOKEN': tokens['refresh_token']},
        },
    )
    if not response.ok:
        # an expired refresh token means re-running bootstrap_auth.py emporia with a fresh browser login
        raise RuntimeError(f'Emporia token refresh failed: {response.status_code} {response.text}')
    result = response.json()['AuthenticationResult']
    if 'RefreshToken' in result:
        tokens['refresh_token'] = result['RefreshToken']
        blob.upload_from_string(json.dumps(tokens), content_type='application/json')
    return result['IdToken']


def chart_usage(headers, device_gid, start, end):
    """15 minute kWh readings for the whole meter, as {iso timestamp: kWh}."""
    response = requests.get(f'{API_URL}/AppAPI', headers=headers, params={
        'apiMethod': 'getChartUsage',
        'deviceGid': device_gid,
        'channel': MAINS,
        'start': start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end': end.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'scale': '15MIN',
        'energyUnit': 'KilowattHours',
    })
    response.raise_for_status()
    body = response.json()
    first = pd.Timestamp(body['firstUsageInstant'])
    return {
        (first + i * pd.Timedelta(minutes=15)).isoformat(): kwh
        for i, kwh in enumerate(body.get('usageList', []))
    }


def plot(usage, filename):
    plt.figure(figsize=(12, 2))
    for name, readings in usage.items():
        series = pd.Series(readings, dtype=float)
        series.index = pd.to_datetime(series.index).tz_convert(PACIFIC).tz_localize(None)
        # kWh per 15 minutes -> average watts
        plt.plot(series.index, series * 4000, label=name)
    plt.ylabel('Watts')
    plt.xlim(utils.week_start_end())
    if len(usage) > 1:
        plt.legend()
    plt.savefig(filename)
    plt.close()


if __name__ == '__main__':
    main()
