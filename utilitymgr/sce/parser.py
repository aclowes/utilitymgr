import datetime
import os

import pytz

import utilitymgr.jendobson_gb as gb
import matplotlib.pyplot as plt


def main():
    accounts = os.environ['SCE_ACCOUNTS'].split(' ')
    plt.figure(figsize=(12, 2))
    lines = []
    for index, account in enumerate(accounts):
        df = gb.dataframe_from_xml(f'data/sce_{account}.xml')
        line = plt.plot(df['Start Time'], df['Wh'], label=f'Account {str(account)[-2:]}')
        lines.append(line)
    plt.ylabel('Wh')
    now = datetime.datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific'))
    x_start = now.date() - datetime.timedelta(days=6)
    x_end = now.date() + datetime.timedelta(days=1)
    plt.xlim(x_start, x_end)
    plt.legend()
    plt.savefig(f'data/sce.png')


if __name__ == '__main__':
    main()
