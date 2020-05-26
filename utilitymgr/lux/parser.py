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
        plt.figure(figsize=(14, 2))
        plt.plot(ambient.index, ambient.values)
        plt.ylabel('Temperature °F')
        ax2 = plt.twinx()
        ax2.bar(heat.index, heat.values, label='heat', align='edge')
        ax2.bar(cool.index, cool.values, bottom=heat.values, label='cool', align='edge')
        ax2.set_ylabel('Runtime minutes')
        plt.legend()
        plt.savefig(f'data/lux_{index}.png')


if __name__ == '__main__':
    main()
