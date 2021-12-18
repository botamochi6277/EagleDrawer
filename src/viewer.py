import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from enum import Enum


class Unit(Enum):
    MM = 0
    INCH = 1
    MIL = 2


plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = '#2b2b2b'
plt.rcParams["axes.facecolor"] = '#2b2b2b'

# https://coolors.co/0696d7-0dab76-32c8c8-c90d15-ffba08
# 17
eagle_colors = ['#ffffff', '#0696D7', '#0DAB76', '32C8C8',
                '#C90D15', '#FFBA08', '#C8C832', '#808080',
                '#282828', '#8252C2', '#00ff00', '#00ffff',
                '#ff0000', '#ff00ff', '#FFCD07', '#AFD134']


def inch_to_point(inch):
    dpi = 72  # dot per inch
    return inch * dpi


def search_layer(layers: ET.ElementTree, no: int):
    for l in layers:
        attr = l.attrib
        if no == int(attr['number']):
            return l

    return None


def draw_circle(circle: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = circle.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    r = float(attr['radius'])
    w = float(attr['width'])
    # inch to point
    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    c = patches.Circle(xy=(x, y), radius=r, ec=eagle_colors[color_id],
                       fill=False, linewidth=inch_to_point(w))
    ax.add_patch(c)


def draw_package(package: ET.ElementTree, layers: ET.ElementTree):
    fig = plt.figure()
    ax = plt.axes()

    for circle in package.findall('circle'):
        draw_circle(circle, layers, ax)

    # ax.plot([0, 1], [0, 1])
    plt.axis('scaled')
    ax.set_aspect('equal')
    name = package.attrib['name']
    plt.savefig(f'{name}.svg')


def parse_tree(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    print(f'root tag: {root.tag}')

    drawing = root.find('drawing')

    layers = drawing.find('layers')
    library = drawing.find('library')
    if library is None:
        print('No Library')
        return

    packages = library.find('packages')
    symbols = library.find('symbols')
    devicesets = library.find('devicesets')

    print(f'# packages: {len(packages)}')
    print(f'# symbols: {len(symbols)}')
    print(f'# devicesets: {len(devicesets)}')

    for package in packages:
        draw_package(package, layers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    parse_tree(args.filename)
