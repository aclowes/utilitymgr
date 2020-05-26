import os

import utilitymgr.jendobson_gb as gb
import matplotlib.pyplot as plt


def main():
    accounts = os.environ['SCE_ACCOUNTS'].split(' ')
    plt.figure(figsize=(14, 2))
    lines = []
    for index, account in enumerate(accounts):
        df = gb.dataframe_from_xml(f'data/sce_{account}.xml')
        line = plt.plot(df['Start Time'], df['Wh'], label=account)
        lines.append(line)
    plt.ylabel('Wh')
    plt.legend()
    plt.savefig(f'data/sce.png')


if __name__ == '__main__':
    main()
