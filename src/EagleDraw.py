import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from enum import Enum
from typing import List, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from colorful_logger import get_colorful_logger
from DiagramDataUnit import (ArcDataUnit, CircleDataUnit, LineDataUnits,
                             RectDataUnit, Text, TextDataUnit, get_arc_param)
from svg_parser import seek_tree

logger = get_colorful_logger(__name__)


class Unit(Enum):
    MM = 0
    INCH = 1
    MIL = 2


# https://coolors.co/0696d7-0dab76-32c8c8-c90d15-ffba08
# https://coolors.co/c8c832-808080-8252c2-ffcd07-afd108
eagle_colors = {
    0: '#ffffff',
    1: '#0696D7',
    2: '#0DAB76',
    3: '32C8C8',
    4: '#C90D15',
    5: '#FFBA08',
    6: '#C8C832',
    7: '#808080',
    8: '#282828',
    9: '#8252C2',
    10: '#00ff00',
    11: '#00ffff',
    12: '#ff0000',
    13: '#ff00ff',
    14: '#FFCD07',
    15: '#AFD134',
    94: '#ff0000',
    95: '#ff0000',
    96: '#ff0000', }

symbol_map = {
    '&': 'and',
    '\'': 'apostrophe',
    '*': 'asterisk',
    '@': 'at',
    '(': 'bracket-l',
    ')': 'bracket-r',
    '^': 'circumflex',
    ':': 'colon',
    ',': 'comma',
    '{': 'curly-bracket-l',
    '}': 'curly-bracket-r',
    '$': 'dollar',
    '=': 'equal',
    '!': 'exclamation',
    '>': 'ge',
    '`': 'grave',
    '-': 'hyphen',
    '<': 'le',
    '#': 'no',
    '%': 'per',
    '.': 'period',
    '+': 'plus',
    '?': 'question',
    '\"': 'quotation',
    ';': 'semicolon',
    '/': 'slash',
    '[': 'sq-bracket-l',
    ']': 'sq-bracket-r',
    '~': 'tilde',
    '_': 'underscore',
    '|': 'vertical',
    ' ': 'space'
}


def offset_from_align(align, width: float, height: float, fullwidth: float):
    offset = [0, 0]
    if align == 'top-left':
        offset = [0, -height*0.5]
    elif align == 'top-center':
        offset = [-0.5*fullwidth, -height*0.5]
    elif align == 'top-right':
        offset = [-fullwidth, -height*0.5]
    elif align == 'center-left':
        offset = [0, 0]
    elif align == 'center':
        offset = [-0.5*fullwidth, 0]
    elif align == 'center-right':
        offset = [-fullwidth, 0]
    elif align == 'bottom-left':
        offset = [-0, height*0.5]
    elif align == 'bottom-center':
        offset = [-0.5*fullwidth, height*0.5]
    elif align == 'bottom-right':
        offset = [-fullwidth, height*0.5]
    offset[0] += 0.5*width
    return offset


def hflip_align(align: str):
    l = align.split('-')
    if len(l) == 0:
        return align
    if l[0] == 'top':
        return f'bottom-{l[1]}'
    if l[0] == 'bottom':
        return f'top-{l[1]}'
    return align


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


def rotate(x, y, angle: float) -> Tuple:
    u = np.cos(angle)*x-np.sin(angle)*y
    v = np.sin(angle)*x+np.cos(angle)*y
    return u, v


def draw_vector_letter(filename: str, offset=[0, 0], ax: plt.Axes = None,
                       w: float = 0.1, size: float = 1.0, angle: float = 0.0,
                       color_id: int = 0, layer_no: int = 0) -> None:
    """Draw A Letter in Vector style from svg file

    Args:
        filename (str): [description]
        offset (list, optional): [description]. Defaults to [0, 0].
        ax (plt.Axes, optional): [description]. Defaults to None.
        w (float, optional): linewidth. Defaults to 0.1.
        size (float, optional): [description]. Defaults to 1.0.
        angle (float, optional): [description]. Defaults to 0.0.
        color_id (int, optional): [description]. Defaults to 0.
        layer_no (int, optional): [description]. Defaults to 0.
    """
    if ax is None:
        ax = plt.gca()
    tree = ET.parse(filename)
    root = tree.getroot()

    pathes = []
    pathes = seek_tree(root, [], pathes)
    if len(pathes) == 0:
        return 0
    # x_all = []
    for p in pathes:
        s = size/12.7
        # centering, flap-y, scaling
        x = np.array([s*(xx[0]-10.0) for xx in p])
        y = np.array([s*(10.0-yy[1]) for yy in p])

        u, v = rotate(x, y, angle)

        # a, b = rotate(offset[0], offset[1], angle)
        l = LineDataUnits(u+offset[0], v+offset[1], linewidth=w,
                          color=eagle_colors[color_id], zorder=-layer_no, solid_capstyle='round')

        ax.add_line(l)
        # x_all.extend(x)
    # width = 2*max(x_all)
    # return width


def draw_pad(pad: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = pad.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    drill = float(attr['drill'])

    diameter = 2*drill
    if 'diameter' in attr:
        diameter = float(attr['diameter'])

    rot = 'R0'
    if 'rot' in attr:
        rot = attr['rot']

    # print(f'pad')
    # print(f'drill : {drill}, diameter : {diameter}')

    w = 0.5*(diameter-drill)
    r = 0.5*drill + 0.5*w
    # print(f'width: {w}, pt: {mm_to_point(w)}')
    layer_no = 17  # Pad layer no. may be fixed
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0
    c = patches.Circle(xy=(x, y), radius=0.5*diameter,
                       ec=None, fc=eagle_colors[color_id], zorder=-layer_no)
    ax.add_patch(c)

    d = patches.Circle(xy=(x, y), radius=0.5*drill, ec=None,
                       fc='#a0a0a0', zorder=-layer_no)
    ax.add_patch(d)


def draw_smd(smd: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = smd.attrib
    # center location of smd land
    x0 = float(attr['x'])
    y0 = float(attr['y'])

    dx = float(attr['dx'])
    dy = float(attr['dy'])

    rot = 'R0'
    if 'rot' in attr:
        rot = attr['rot']

    if rot == 'R0' or rot == 'R180':
        w = dx
        h = dy
    else:
        w = dy
        h = dx

    # lower left corner location
    x = x0-0.5*w
    y = y0-0.5*h

    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])

    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    # rect = patches.FancyBboxPatch(
    #     xy=(x, y), width=w, height=h, fc=eagle_colors[color_id], ec=None, lw=None, zorder=-layer_no,
    #     mutation_scale=0)

    rect = RectDataUnit(
        xy=(x, y), width=w, height=h, fc=eagle_colors[color_id], ec=None, lw=None, zorder=-layer_no
    )
    ax.add_patch(rect)


def draw_wire(wire: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = wire.attrib
    x = [float(attr['x1']), float(attr['x2'])]
    y = [float(attr['y1']), float(attr['y2'])]
    w = float(attr['width'])
    curve = None
    if 'curve' in attr:
        curve = math.radians(float(attr['curve']))

    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    if curve is None:
        # straight line
        l = LineDataUnits(x, y, linewidth=w,
                          color=eagle_colors[color_id], zorder=-layer_no, solid_capstyle='round')

        ax.add_line(l)
    else:
        # draw arc
        x0, y0, r, t1, t2, x3, y3 = get_arc_param(
            x[0], y[0], x[1], y[1], curve)

        arc = ArcDataUnit((x0, y0), r*2, r*2,
                          theta1=math.degrees(t1),
                          theta2=math.degrees(t2),
                          linewidth=w,
                          color=eagle_colors[color_id],  zorder=-layer_no)
        ax.add_patch(arc)

        # debug
        # reference point
        # c = CircleDataUnit(xy=(x3, y3), radius=0.1, ec=eagle_colors[4],
        #                    fill=False, linewidth=w, zorder=-layer_no)
        # ax.add_patch(c)

        # # xy
        # c = CircleDataUnit(xy=(x[0], y[0]), radius=0.1, ec=eagle_colors[6],
        #                    fill=False, linewidth=w, zorder=-layer_no)
        # ax.add_patch(c)
        # c = CircleDataUnit(xy=(x[1], y[1]), radius=0.1, ec=eagle_colors[7],
        #                    fill=False, linewidth=w, zorder=-layer_no)
        # ax.add_patch(c)

        # # mid point
        # m = [0.5*(x[0]+x[1]), 0.5*(y[0]+y[1])]

        # c = CircleDataUnit(xy=m, radius=0.01, ec=eagle_colors[4],
        #                    fill=False, linewidth=w, zorder=-layer_no)
        # ax.add_patch(c)

        # # arc center
        # c = CircleDataUnit(xy=(x0, y0), radius=0.05, ec=eagle_colors[4],
        #                    fill=False, linewidth=w, zorder=-layer_no)
        # ax.add_patch(c)


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
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    c = CircleDataUnit(xy=(x, y), radius=r, ec=eagle_colors[color_id],
                       fill=False, linewidth=w, zorder=-layer_no)
    ax.add_patch(c)


def draw_letter(s: str, x: float, y: float, **kwargs) -> None:
    """Draw a letter

    Args:
        s (str): single letter to draw
        x (float): letter center x-position
        y (float): letter center y-position
    """
    a = re.findall(r'[a-z]', s)
    if len(a) > 0:
        # Lower Alphabet
        f = os.path.join(os.path.dirname(__file__),
                         f'letters/{a[0]}_lower.svg')
        draw_vector_letter(f, (x, y), **kwargs)
        return

    A = re.findall(r'[A-Z]', s)
    if len(A) > 0:
        f = os.path.join(os.path.dirname(__file__),
                         f'letters/{A[0]}_upper.svg')
        draw_vector_letter(f, (x, y), **kwargs)
        return

    n = re.findall(r'[0-9]', s)
    if len(n) > 0:
        f = os.path.join(os.path.dirname(__file__), f'letters/{n[0]}.svg')
        draw_vector_letter(f, (x, y), **kwargs)
        return

    # symbols
    if s in symbol_map:
        f = os.path.join(os.path.dirname(__file__),
                         f'letters/{symbol_map[s]}.svg')
        draw_vector_letter(f, (x, y), **kwargs)
        return

    f = os.path.join(os.path.dirname(__file__), f'letters/tofu.svg')
    draw_vector_letter(f, (x, y), **kwargs)
    return


def draw_text(text: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):

    # <text x="-12.7" y="-10.16" size="1.778" layer="95">&gt;VALUE</text>

    attr = text.attrib
    x = float(attr['x'])
    y = float(attr['y'])
    size = float(attr['size'])
    font = 'monospace'
    if 'font' in attr:
        font = attr['font']
    align = 'bottom-left'
    if 'align' in attr:
        align = attr['align']

    ratio = 0.2
    if 'ratio' in attr:
        ratio = float(attr['ratio'])/100.0
    linewidth = ratio*size/5.0
    txt = text.text

    rot = 'R0'
    if 'rot' in attr:
        rot = attr['rot']
    angle = float(re.findall('[0-9+?]', rot)[0])

    if (91 < angle) or (270 < angle):
        align = hflip_align(align)
        angle -= 180

    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    clearance = size*0.1
    w = 0.5*size
    full_width = w*len(txt) + clearance*(len(txt)-1)
    offset = offset_from_align(align, w, size, full_width)
    offset = rotate(offset[0], offset[1], math.radians(angle))
    dx = w+clearance
    dy = 0
    dx, dy = rotate(dx, dy, math.radians(angle))
    # logger.debug(f'align: {align}, offset: {offset}')
    # draw text origin
    c = CircleDataUnit(xy=(x, y), radius=0.01, ec=eagle_colors[color_id],
                       fill=False, linewidth=0.1, zorder=-layer_no)
    ax.add_patch(c)

    for s in txt:
        draw_letter(s, x+offset[0], y+offset[1],
                    ax=ax, size=size, angle=math.radians(angle), w=linewidth, color_id=color_id, layer_no=layer_no)
        x += dx
        y += dy


def draw_pin(pin: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = pin.attrib
    x0 = float(attr['x'])
    y0 = float(attr['y'])
    name = attr['name']
    length = attr['length']
    dx = 2.54
    if length == 'short':
        dx = 2.54
    if length == 'middle':
        dx = 2.54*2
    elif length == 'long':
        dx = 2.54*3

    rot = 'R0'
    if 'rot' in attr:
        rot = attr['rot']

    halign = 'center'
    text_x = x0
    text_y = y0

    if rot == 'R0':
        x = [x0, x0+dx]
        y = [y0, y0]
        halign = 'left'
        text_x = x0+2*dx
    elif rot == 'R90':
        x = [x0, x0]
        y = [y0, y0+dx]
    elif rot == 'R180':
        x = [x0, x0-dx]
        y = [y0, y0]
        halign = 'right'
        text_x = x0-2*dx
    elif rot == 'R270':
        x = [x0, x0]
        y = [y0, y0-dx]

    layer_no = 94  # pin layer may be fixed
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0
    w = 0.1
    l = LineDataUnits(x, y, linewidth=w,
                      color=eagle_colors[color_id], zorder=-layer_no)

    ax.add_line(l)

    # Name
    text_height = 2.0
    text_width = 0.5*text_height
    text_x += text_width  # default origin is left
    clearance = text_height*0.1
    full_width = text_width*len(name) + clearance*(len(name)-1)
    offset = offset_from_align(halign, w, text_height, full_width)
    linewidth = 0.2*text_height/5.0
    for s in name:
        draw_letter(s, text_x+offset[0], text_y + offset[1],
                    ax=ax, size=text_height, w=linewidth, color_id=0, layer_no=layer_no)
        text_x += text_width + clearance
    # ax.text(text_x, text_y, name, verticalalignment='center',
    #         horizontalalignment=halign, color=eagle_colors[color_id], zorder=-layer_no)


def draw_package(package: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):

    name = package.attrib['name']

    for pad in package.findall('pad'):
        draw_pad(pad, layers, ax)

    for smd in package.findall('smd'):
        draw_smd(smd, layers, ax)

    for circle in package.findall('circle'):
        draw_circle(circle, layers, ax)

    for wire in package.findall('wire'):
        draw_wire(wire, layers, ax)

    for text in package.findall('text'):
        draw_text(text, layers, ax)

    # ax.plot([0, 1], [0, 1])
    plt.axis('scaled')
    ax.set_aspect('equal')


def draw_symbol(symbol: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):

    name = symbol.attrib['name']

    for pin in symbol.findall('pin'):
        draw_pin(pin, layers, ax)

    for circle in symbol.findall('circle'):
        draw_circle(circle, layers, ax)

    for wire in symbol.findall('wire'):
        draw_wire(wire, layers, ax)

    for text in symbol.findall('text'):
        draw_text(text, layers, ax)

    # ax.plot([0, 1], [0, 1])
    plt.axis('scaled')
    ax.set_aspect('equal')


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
        plt.close()
        logger.debug(f'save {figpath}')

    os.makedirs(os.path.join(dirpath, f'symbols'), exist_ok=True)
    for symbol in symbols:
        fig = plt.figure()
        ax = plt.axes()
        draw_symbol(symbol, layers, ax=ax)
        name = symbol.attrib['name']
        ax.set_title(name)
        figpath = os.path.join(dirpath, f'symbols/{name}.svg')
        plt.savefig(figpath)
        plt.close()
        logger.debug(f'save {figpath}')
