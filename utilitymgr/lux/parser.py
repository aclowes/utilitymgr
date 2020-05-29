import datetime
import json
import os

import pandas as pd
import matplotlib.pyplot as plt


def main():
    accounts = os.environ['LUX_THERMOSTATS'].split(' ')
    for index, account in enumerate(accounts):
        data = json.load(open(f'data/lux_{account}.json'))
        # subtract timezone offset to show in local time
        dates = pd.to_datetime(
            pd.Series(data['series']['dates']) +
            pd.Series(data['series']['dateOffsetMilliseconds']),
            unit='ms'
        )
        heat = pd.Series(data['series']['results']['heat'], index=dates)
        cool = pd.Series(data['series']['results']['cool'], index=dates)
        ambient = pd.Series(
            index=pd.to_datetime(
                pd.Series(data['events']['ambient_change']['dates']) +
                pd.Series(data['events']['ambient_change']['dateOffsetMilliseconds']),
                unit='ms'
            ),
            data=data['events']['ambient_change']['values']
        )
        plt.figure(figsize=(12, 2))
        ax1 = plt.gca()
        bar_config = {'width': 0.05, 'align': 'edge'}
        ax1.bar(heat.index, heat.values, label='heat', color='orangered', **bar_config)
        ax1.bar(cool.index, cool.values, bottom=heat.values, label='cool', color='royalblue', **bar_config)
        ax1.set_ylabel('Runtime minutes')
        ax1.legend(bbox_to_anchor=(-.06, 0), loc='lower right', edgecolor='white')
        ax2 = plt.twinx()
        ax2.plot(ambient.index, ambient.values, color='darkslategrey')
        ax2.set_ylabel('Temperature °F')
        x_start = datetime.date.today() - datetime.timedelta(days=6)
        x_end = datetime.date.today() + datetime.timedelta(days=1)
        plt.xlim(x_start, x_end)
        plt.savefig(f'data/lux_{index}.png')


if __name__ == '__main__':
    main()
