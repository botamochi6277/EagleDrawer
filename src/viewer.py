from posixpath import basename
import xml.etree.ElementTree as ET
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from enum import Enum

from DiagramDataUnit import CircleDataUnit, TextDataUnit, Text


class Unit(Enum):
    MM = 0
    INCH = 1
    MIL = 2


# matplotlib config
plt.style.use('dark_background')
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = '#2b2b2b'
plt.rcParams["axes.facecolor"] = '#2b2b2b'
plt.rcParams["savefig.facecolor"] = '#2b2b2b'
plt.rcParams["font.family"] = 'sans-serif'

# https://coolors.co/0696d7-0dab76-32c8c8-c90d15-ffba08
# https://coolors.co/c8c832-808080-8252c2-ffcd07-afd108
eagle_colors = ['#ffffff', '#0696D7', '#0DAB76', '32C8C8',
                '#C90D15', '#FFBA08', '#C8C832', '#808080',
                '#282828', '#8252C2', '#00ff00', '#00ffff',
                '#ff0000', '#ff00ff', '#FFCD07', '#AFD134']


def inch_to_point(inch):
    dpi = 72  # dot per inch
    return inch * dpi


def mm_to_point(mm):
    dpi = 72  # dot per inch
    return (mm/25.4) * dpi


def search_layer(layers: ET.ElementTree, no: int):
    for l in layers:
        attr = l.attrib
        if no == int(attr['number']):
            return l

    return None


def draw_pad(pad: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = pad.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    drill = float(attr['drill'])
    diameter = float(attr['diameter'])

    # print(f'pad')
    # print(f'drill : {drill}, diameter : {diameter}')

    w = 0.5*(diameter-drill)
    r = 0.5*drill + 0.5*w
    # print(f'width: {w}, pt: {mm_to_point(w)}')
    layer_no = 17  # Pad layer no. may be fixed
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    c = patches.Circle(xy=(x, y), radius=0.5*diameter,
                       ec=None, fc=eagle_colors[color_id], zorder=-layer_no)
    ax.add_patch(c)

    d = patches.Circle(xy=(x, y), radius=0.5*drill, ec=None,
                       fc='#a0a0a0', zorder=-layer_no)
    ax.add_patch(d)


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
    c = CircleDataUnit(xy=(x, y), radius=r, ec=eagle_colors[color_id],
                       fill=False, linewidth=w, zorder=-layer_no)
    ax.add_patch(c)


def draw_text(text: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = text.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    size = float(attr['size'])
    font = 'monospace'
    if 'font' in attr:
        font = attr['font']
    align = 'left'
    if 'align' in attr:
        align = attr['align']
    txt = text.text

    # inch to point
    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    ax.text(x, y, txt, fontfamily='sans-serif',
            fontsize=mm_to_point(size), zorder=-layer_no)

    # t = TextDataUnit(x, y, txt, fontfamily='monospace',
    #                  fontsize=size, zorder=-layer_no, transform=ax.transAxes)

    # ax.add_artist(t)


def draw_package(package: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):

    name = package.attrib['name']

    for pad in package.findall('pad'):
        draw_pad(pad, layers, ax)

    for circle in package.findall('circle'):
        draw_circle(circle, layers, ax)

    for text in package.findall('text'):
        draw_text(text, layers, ax)

    # ax.plot([0, 1], [0, 1])
    plt.axis('scaled')
    ax.set_aspect('equal')


def parse_tree(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    print(f'root tag: {root.tag}')

    basename = os.path.basename(filename).split('.')[0]
    dirpath = os.path.join(os.path.dirname(__file__), f'../dst/{basename}')
    os.makedirs(dirpath, exist_ok=True)

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

    os.makedirs(os.path.join(dirpath, f'packages'), exist_ok=True)
    for package in packages:
        fig = plt.figure()
        ax = plt.axes()
        draw_package(package, layers, ax=ax)
        name = package.attrib['name']
        ax.set_title(name)
        figpath = os.path.join(dirpath, f'packages/{name}.svg')
        plt.savefig(figpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    parse_tree(args.filename)
