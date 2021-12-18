import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt


def parse_tree(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    print(f'root tag: {root.tag}')

    drawing = root.find('drawing')

    layers = drawing.find('layers')
    library = drawing.find('library')
    if library is None:
        return

    packages = library.find('packages')
    symbols = library.find('symbols')
    devicesets = library.find('devicesets')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    parse_tree(args.filename)
