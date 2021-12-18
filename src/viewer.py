import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = 'black'
plt.rcParams["axes.facecolor"] = 'black'


def draw_circle(circle: ET.ElementTree, ax: plt.Axes):
    attr = circle.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    r = float(attr['radius'])
    w = float(attr['width'])
    layer = int(attr['layer'])
    c = patches.Circle(xy=(x, y), radius=r, ec='#ffffff', fill=False)
    ax.add_patch(c)


def draw_package(package: ET.ElementTree):
    fig = plt.figure()
    ax = plt.axes()

    for circle in package.findall('circle'):
        draw_circle(circle, ax)

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
        draw_package(package)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    parse_tree(args.filename)
