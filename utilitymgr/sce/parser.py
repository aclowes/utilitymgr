import utilitymgr.jendobson_gb as gb
import matplotlib.pyplot as plt


def main(data_file):
    df = gb.dataframe_from_xml(data_file)

    plt.figure(figsize=(14, 2))
    plt.plot(df['Start Time'], df['Wh'])
    plt.ylabel('Wh')
    plt.show()
    pass


if __name__ == '__main__':
    main('data/data.xml')
