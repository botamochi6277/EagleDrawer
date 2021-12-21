from posixpath import basename
import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

from colorful_logger import get_colorful_logger
from EagleDraw import draw_package, draw_symbol

logger = get_colorful_logger(__name__)

# matplotlib config
plt.style.use('dark_background')
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = '#2b2b2b'
plt.rcParams["axes.facecolor"] = '#2b2b2b'
plt.rcParams["savefig.facecolor"] = '#2b2b2b'
plt.rcParams["font.family"] = 'sans-serif'


def parse_tree(filename, outputdir='imgs'):
    tree = ET.parse(filename)
    root = tree.getroot()
    logger.info(f'parse {filename}')
    logger.debug(f'root tag: {root.tag}')

    basename = os.path.basename(filename).split('.')[0]
    # dirpath = os.path.join(os.path.dirname(__file__), f'{outputdir}')
    dirpath = os.path.join(outputdir, basename)
    os.makedirs(dirpath, exist_ok=True)
    logger.debug(f'make {os.path.normpath(dirpath)}')

    drawing = root.find('drawing')

    layers = drawing.find('layers')
    library = drawing.find('library')
    if library is None:
        logger.error('No Library')
        return

    packages = library.find('packages')
    symbols = library.find('symbols')
    devicesets = library.find('devicesets')

    logger.info(f'# packages: {len(packages)}')
    logger.info(f'# symbols: {len(symbols)}')
    logger.info(f'# devicesets: {len(devicesets)}')

    os.makedirs(os.path.join(dirpath, f'packages'), exist_ok=True)
    for package in packages:
        fig = plt.figure()
        ax = plt.axes()
        draw_package(package, layers, ax=ax)
        name = package.attrib['name']
        ax.set_title(name)
        figpath = os.path.join(dirpath, f'packages/{name}.svg')
        plt.savefig(figpath)

    os.makedirs(os.path.join(dirpath, f'symbols'), exist_ok=True)
    for symbol in symbols:
        fig = plt.figure()
        ax = plt.axes()
        draw_symbol(symbol, layers, ax=ax)
        name = symbol.attrib['name']
        ax.set_title(name)
        figpath = os.path.join(dirpath, f'symbols/{name}.svg')
        plt.savefig(figpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    parser.add_argument(
        '--output', '-o', default='imgs', help='output path')
    args = parser.parse_args()
    print(args.filenames)
    for filename in args.filenames:
        parse_tree(filename, args.output)
