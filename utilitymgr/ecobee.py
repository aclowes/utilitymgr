import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
from google.cloud import storage
from pyecobee import Ecobee
from pyecobee.errors import InvalidTokenError

from utilitymgr import utils

# seeded once by `bootstrap_auth.py ecobee`, then refreshed on every run
TOKEN_BLOB = 'utilitymgr/ecobee_token.json'
REPORT_URL = 'https://api.ecobee.com/1/runtimeReport'
# runtime columns are seconds of equipment runtime per 5 minute interval
COLUMNS = ['zoneAveTemp', 'compCool1', 'compHeat1', 'auxHeat1', 'fan']
# chart order (ecobee_0.png, ecobee_1.png, ...) must match the headings in index.html
ORDER = ['Office West', 'Office Center', 'Bevi Bene']


def sort_key(thermostat):
    # unknown/renamed thermostats go last, by identifier
    name = thermostat['name']
    return (ORDER.index(name) if name in ORDER else len(ORDER), thermostat['identifier'])


def main():
    bucket = storage.Client().bucket('static.yawn.live')
    client = authenticate(bucket)
    client.get_thermostats()
    thermostats = sorted(client.thermostats, key=sort_key)

    report = runtime_report(client.access_token, [t['identifier'] for t in thermostats])
    with open('data/ecobee.json', 'w') as data_file:
        json.dump(report, data_file)

    rows = {r['thermostatIdentifier']: r['rowList'] for r in report['reportList']}
    for index, thermostat in enumerate(thermostats):
        plot(rows.get(thermostat['identifier'], []), f'data/ecobee_{index}.png')


def authenticate(bucket):
    blob = bucket.blob(TOKEN_BLOB)
    tokens = json.loads(blob.download_as_text())
    client = Ecobee(config={
        'ACCESS_TOKEN': tokens['access_token'],
        'REFRESH_TOKEN': tokens['refresh_token'],
        'USERNAME': os.environ.get('ECOBEE_USERNAME'),
        'PASSWORD': os.environ.get('ECOBEE_PASSWORD'),
    })
    try:
        client.refresh_tokens()
    except InvalidTokenError:
        # refresh token revoked/expired: full login (fails if ecobee demands an MFA code)
        client.request_tokens_web()
    tokens = {'access_token': client.access_token, 'refresh_token': client.refresh_token}
    blob.upload_from_string(json.dumps(tokens), content_type='application/json')
    return client


def runtime_report(access_token, identifiers):
    start, end = utils.week_start_end()
    body = {
        'startDate': start.isoformat(),
        'endDate': end.isoformat(),
        'columns': ','.join(COLUMNS),
        'selection': {'selectionType': 'thermostats', 'selectionMatch': ','.join(identifiers)},
    }
    response = requests.get(
        REPORT_URL,
        params={'format': 'json', 'body': json.dumps(body)},
        headers={'Authorization': f'Bearer {access_token}'},
    )
    response.raise_for_status()
    return response.json()


def plot(rows, filename):
    df = pd.DataFrame([row.split(',') for row in rows], columns=['date', 'time'] + COLUMNS)
    df.index = pd.to_datetime(df.pop('date') + ' ' + df.pop('time'))
    df = df.apply(pd.to_numeric, errors='coerce')
    hourly = df.resample('h').agg({
        'zoneAveTemp': 'mean', 'compCool1': 'sum', 'compHeat1': 'sum', 'auxHeat1': 'sum',
    })
    heat = (hourly.compHeat1 + hourly.auxHeat1) / 60
    cool = hourly.compCool1 / 60

    plt.figure(figsize=(12, 2))
    ax1 = plt.gca()
    bar_config = {'width': 1 / 24, 'align': 'edge'}
    ax1.bar(hourly.index, heat, color='indianred', label='Heat', **bar_config)
    ax1.bar(hourly.index, cool, bottom=heat, color='royalblue', label='Cool', **bar_config)
    ax1.set_ylabel('Runtime minutes')
    ax1.set_ylim(0, 60)
    ax1.legend(loc='upper left')
    ax2 = plt.twinx()
    ax2.plot(hourly.index, hourly.zoneAveTemp, color='darkslategrey')
    ax2.set_ylabel('Temperature °F')
    ax2.set_ylim(50, 85)
    plt.xlim(utils.week_start_end())
    plt.savefig(filename)
    plt.close()


if __name__ == '__main__':
    main()
