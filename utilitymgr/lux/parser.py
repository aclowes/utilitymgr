import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utilitymgr import utils


def main():
    accounts = os.environ['LUX_THERMOSTATS'].split(' ')
    for index, account in enumerate(accounts):
        data = json.load(open(f'data/lux_{account}.json'))
        rows = [
            row
            for day in reversed(data["dailyruntime"])
            for row in day["sample"]
            # todo remove hacky filter
            if row['airtemp'] != -1
        ]
        df = pd.DataFrame.from_records(rows)
        # convert timestamp to dates and runtime to minutes
        df.timestamp = pd.to_datetime(df.timestamp)
        df.runtime = pd.to_timedelta(df.runtime) / pd.Timedelta(minutes=1)
        df.airtemp = df.airtemp.replace(-1, np.nan)
        plt.figure(figsize=(12, 2))
        ax1 = plt.gca()
        bar_config = {'width': 0.05, 'align': 'edge'}
        ax1.bar(df.timestamp, df.runtime, color='royalblue', **bar_config)
        ax1.set_ylabel('Runtime minutes')
        ax1.set_ylim(0, 60)
        ax2 = plt.twinx()
        ax2.plot(df.timestamp, df.airtemp, color='darkslategrey')
        ax2.set_ylabel('Temperature °F')
        ax2.set_ylim(50, 85)
        plt.xlim(utils.week_start_end())
        plt.savefig(f'data/lux_{index}.png')


if __name__ == '__main__':
    main()
