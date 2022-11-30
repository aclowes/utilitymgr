import os

import utilitymgr.jendobson_gb as gb
import matplotlib.pyplot as plt

from utilitymgr import utils


def main():
    accounts = os.environ['SCE_ACCOUNTS'].split(' ')
    plt.figure(figsize=(12, 2))
    lines = []
    for index, account in enumerate(accounts):
        df = gb.dataframe_from_xml(f'data/sce_{account}.xml')
        line = plt.plot(df['Start Time'], df['Wh'] * 4, label=f'Account {str(account)[-2:]}')
        lines.append(line)
    plt.ylabel('Watts')
    plt.xlim(utils.week_start_end())
    plt.legend()
    plt.savefig(f'data/sce.png')


if __name__ == '__main__':
    main()
