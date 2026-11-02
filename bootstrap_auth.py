"""One-time auth bootstrap for ecobee and Emporia.

    venv/bin/python bootstrap_auth.py ecobee    # logs in (prompts for MFA code), saves ecobee_tokens.json
    venv/bin/python bootstrap_auth.py emporia   # reads emporia_store.json (see README), saves emporia_tokens.json

Then copy the token files to where runner.py reads them:

    gsutil cp ecobee_tokens.json gs://static.yawn.live/utilitymgr/ecobee_token.json
    gsutil cp emporia_tokens.json gs://static.yawn.live/utilitymgr/emporia_token.json

All token files are gitignored. Passwords are never written to them.
"""
import datetime
import json
import os
import sys

import requests

ECOBEE_TOKENS = 'ecobee_tokens.json'
EMPORIA_TOKENS = 'emporia_tokens.json'
EMPORIA_STORE = 'emporia_store.json'
PYEMVUE_CLIENT_ID = '4qte47jbstod8apnfic0bunmrq'


def load_env(path='.env'):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def save_private(path, data):
    with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
        json.dump(data, f, indent=2)


def ecobee():
    from pyecobee import Ecobee
    from pyecobee.errors import EcobeeAuthMfaRequiredError

    client = Ecobee(config={
        'USERNAME': os.environ['ECOBEE_USERNAME'],
        'PASSWORD': os.environ['ECOBEE_PASSWORD'],
    })
    try:
        client.request_tokens_web()
    except EcobeeAuthMfaRequiredError as err:
        challenge = err.challenge
        code = input(f'ecobee {challenge.mfa_type} code: ').strip()
        client.submit_mfa_code(challenge, code)
    print('ecobee login OK')

    save_private(ECOBEE_TOKENS, {
        'access_token': client.access_token,
        'refresh_token': client.refresh_token,
    })
    print(f'saved {ECOBEE_TOKENS}')

    client.get_thermostats()
    ids = []
    for t in client.thermostats:
        ids.append(t['identifier'])
        print(f"  thermostat {t['identifier']}  {t['name']!r}  model={t.get('modelNumber')}")

    # the key unknown: does a web-login token work for the historical runtimeReport endpoint?
    end = datetime.date.today()
    body = {
        'startDate': (end - datetime.timedelta(days=1)).isoformat(),
        'endDate': end.isoformat(),
        'columns': 'zoneAveTemp,compCool1,compHeat1,auxHeat1,fan',
        'selection': {'selectionType': 'thermostats', 'selectionMatch': ','.join(ids)},
    }
    response = requests.get(
        'https://api.ecobee.com/1/runtimeReport',
        params={'format': 'json', 'body': json.dumps(body)},
        headers={'Authorization': f'Bearer {client.access_token}'},
    )
    print(f'runtimeReport HTTP {response.status_code}')
    if response.ok:
        for report in response.json().get('reportList', []):
            rows = report['rowList']
            print(f"  {report['thermostatIdentifier']}: {len(rows)} rows, e.g. {rows[len(rows) // 2] if rows else None}")
    else:
        print(response.text[:500])


def emporia():
    if os.path.exists(EMPORIA_STORE):
        # dump of IndexedDB com.amplify.awsCognitoAuthPlugin/default.store from web.emporiaenergy.com
        store = json.load(open(EMPORIA_STORE))
        key = next(k for k in store if k.endswith('.hostedUi.refreshToken'))
        save_private(EMPORIA_TOKENS, {'client_id': key.split('.')[0], 'refresh_token': store[key]})
    tokens = json.load(open(EMPORIA_TOKENS))
    client_id = tokens.get('client_id', PYEMVUE_CLIENT_ID)
    print(f'browser client_id={client_id} (pyemvue uses {PYEMVUE_CLIENT_ID}: '
          f'{"MATCH" if client_id == PYEMVUE_CLIENT_ID else "DIFFERENT"})')

    # verify the refresh token works against the client that issued it
    response = requests.post(
        'https://cognito-idp.us-east-2.amazonaws.com/',
        headers={
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
        },
        json={
            'AuthFlow': 'REFRESH_TOKEN_AUTH',
            'ClientId': client_id,
            'AuthParameters': {'REFRESH_TOKEN': tokens['refresh_token']},
        },
    )
    print(f'cognito refresh HTTP {response.status_code}')
    if not response.ok:
        print(response.text[:500])
        return
    result = response.json()['AuthenticationResult']
    print(f"  new id_token, expires in {result['ExpiresIn']}s; "
          f"refresh token rotated: {'RefreshToken' in result}")
    tokens['id_token'] = result['IdToken']
    tokens['access_token'] = result['AccessToken']
    tokens['refresh_token'] = result.get('RefreshToken', tokens['refresh_token'])
    tokens['client_id'] = client_id
    save_private(EMPORIA_TOKENS, tokens)

    # list devices/circuits with the fresh id token (same call pyemvue makes)
    response = requests.get(
        'https://api.emporiaenergy.com/customers/devices',
        headers={'authtoken': tokens['id_token']},
    )
    print(f'devices HTTP {response.status_code}')
    response.raise_for_status()
    for device in response.json().get('devices', []):
        print(f"  device {device['deviceGid']}  {device.get('locationProperties', {}).get('deviceName')!r}  "
              f"model={device.get('model')}")
        for channel in device.get('channels', []):
            print(f"    channel {channel['channelNum']:>8}  {channel.get('name')!r}")


if __name__ == '__main__':
    load_env()
    {'ecobee': ecobee, 'emporia': emporia}[sys.argv[1]]()
