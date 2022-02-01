import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from DiagramDataUnit import CircleDataUnit, TextDataUnit, Text, LineDataUnits
from enum import Enum
import os
import math
from colorful_logger import get_colorful_logger
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


def get_arc(x1, y1, x2, y2, phi, u: float = 1.0):
    n = [-(y2-y1), (x2-x1)]
    m = [0.5*(x1+x2), 0.5*(y1+y2)]
    x3 = m[0] - u*n[0]
    y3 = m[1] - u*n[1]

    x0 = (x1**2*y2 - x1**2*y3 - x2**2*y1 + x2**2*y3 + x3**2*y1 - x3**2*y2 + y1**2*y2 - y1**2*y3 -
          y1*y2**2 + y1*y3**2 + y2**2*y3 - y2*y3**2)/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)
    y0 = -(x1**2*x2 - x1**2*x3 - x1*x2**2 + x1*x3**2 - x1*y2**2 + x1*y3**2 + x2**2*x3 - x2*x3**2 +
           x2*y1**2 - x2*y3**2 - x3*y1**2 + x3*y2**2)/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)
    r = -math.sqrt((x1**2 - 2*x1*x2 + x2**2 + y1**2 - 2*y1*y2 + y2**2)*(x1**2 - 2*x1*x3 + x3**2 + y1**2 - 2*y1*y3 + y3**2)
                   * (x2**2 - 2*x2*x3 + x3**2 + y2**2 - 2*y2*y3 + y3**2))/(2*(x1*y2 - x1*y3 - x2*y1 + x2*y3 + x3*y1 - x3*y2)+1e-6)

    theta1 = math.atan2((y1-y0), (x1-x0))
    theta2 = math.atan2((y2-y0), (x2-x0))

    return x0, y0, r, theta1, theta2, x3, y3


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
        # lower left corner location
        w = dx
        h = dy
    else:
        w = dy
        h = dx

    x = x0-0.5*w
    y = y0-0.5*h

    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])

    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    rect = patches.FancyBboxPatch(
        xy=(x, y), width=w, height=h, fc=eagle_colors[color_id], ec=None, lw=None, zorder=-layer_no)
    ax.add_patch(rect)


def draw_wire(wire: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = wire.attrib
    x = [float(attr['x1']), float(attr['x2'])]
    y = [float(attr['y1']), float(attr['y2'])]
    w = float(attr['width'])
    curve = None
    if 'curve' in attr:
        curve = float(attr['curve'])

    layer_no = int(attr['layer'])
    layer = search_layer(layers, layer_no)
    color_id = int(layer.attrib['color'])
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0

    if curve is None:
        # straight line
        l = LineDataUnits(x, y, linewidth=w,
                          color=eagle_colors[color_id], zorder=-layer_no)

        ax.add_line(l)
    else:
        # draw arc
        u = curve/360.0
        x0, y0, r, t1, t2, x3, y3 = get_arc(
            x[0], y[0], x[1], y[1], math.radians(curve), u=u)

        arc = patches.Arc((x0, y0), r*2, r*2,
                          theta1=math.degrees(t1),
                          theta2=math.degrees(t2),
                          linewidth=w,
                          color=eagle_colors[color_id],  zorder=-layer_no)
        ax.add_patch(arc)

        # debug
        # reference point
        c = CircleDataUnit(xy=(x3, y3), radius=0.1, ec=eagle_colors[color_id],
                           fill=False, linewidth=w, zorder=-layer_no)
        ax.add_patch(c)

        # mid point
        m = [0.5*(x[0]+x[1]), 0.5*(y[0]+y[1])]

        c = CircleDataUnit(xy=m, radius=0.01, ec=eagle_colors[color_id],
                           fill=False, linewidth=w, zorder=-layer_no)
        ax.add_patch(c)


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
    if not color_id in eagle_colors:
        logger.warning(f'color id {color_id} is undefined')
        color_id = 0
    t = ax.text(x, y, txt, fontfamily='sans-serif',
                fontsize=size, zorder=-layer_no)
    # ppd = 72.0/ax.figure.dpi
    # tf = ax.transData.transform
    # fontsize = ((tf((1, size))-tf((0, 0)))*ppd)[1]
    # t.set_fontsize(fontsize)

    # print(f'text type: {type(t)}')
    # t = TextDataUnit(x, y, txt, fontfamily='monospace',
    #                  fontsize=size, zorder=-layer_no, transform=ax.transAxes)

    # ax.add_artist(t)


def draw_pin(pin: ET.ElementTree, layers: ET.ElementTree, ax: plt.Axes):
    attr = pin.attrib
    x0 = float(attr['x'])
    y0 = float(attr['y'])
    name = attr['name']
    length = attr['length']
    dx = 2.54
    if length == 'short':
        dx = 2.54
    elif length == 'long':
        dx = 2.54

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

    ax.text(text_x, text_y, name, verticalalignment='center',
            horizontalalignment=halign, color=eagle_colors[color_id], zorder=-layer_no)


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
