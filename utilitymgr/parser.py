from lxml import etree


def main(data):
    root = etree.fromstring(data)
    pass


if __name__ == '__main__':
    with open('data.xml', 'rb') as data_file:
        main(data_file.read())
