import argparse
from ast import parse
from typing import Tuple
import re
import copy
import os
import sys

import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt


def parse_tf(s):
    # matrix(a,b,c,d,tx,ty)
    t = re.findall(
        r'matrix\(([\S]+?),([\S]+?),([\S]+?),([\S]+?),([\S]+?),([\S]+?)\)', s)
    a, b, c, d, tx, ty = t[0]
    mat = np.matrix([[float(a), float(c), float(tx)],
                     [float(b), float(d), float(ty)],
                     [0, 0, 1]
                     ])
    return mat


def transform(pos, transforms=[]):

    print(f'transforms:\n{transforms}')
    p = np.matrix([pos[0], pos[1], 1]).T
    for tf in reversed(transforms):
        p = tf @ p
    return np.ravel(p)[0:2]


def parse_node(s: str) -> Tuple:
    """parse nodes in a path

    Args:
        s (str): body of the path's d attribute

    Returns:
        Tuple: (symbol, positions)
    """
    # https://developer.mozilla.org/ja/docs/Web/SVG/Tutorial/Paths
    sy = re.findall(r'[a-zA-Z]', s)
    l = re.split('[a-zA-Z]', s)  # sprit with alphabet
    pos = [p.split(',') for p in l[1:]]

    # convert str to float
    for p in pos:
        for i, x in enumerate(p):
            p[i] = float(x)

    return sy, pos


def seek_tree(tree: ET.ElementTree, tf=[], paths=[]):
    for child in tree:
        tf_c = copy.deepcopy(tf)
        tag = child.tag
        attr = child.attrib
        # print(tag)
        # print(attr)

        if 'transform' in attr:
            if len(tf_c) == 0:
                tf_c = [parse_tf(attr['transform'])]
            else:
                tf_c.append(parse_tf(attr['transform']))

        if tag == '{http://www.w3.org/2000/svg}g':
            seek_tree(child, tf_c, paths)
        elif tag == '{http://www.w3.org/2000/svg}path':
            d = attr['d']
            sy, positions = parse_node(d)
            transformed_pos = [
                transform(p, tf_c) for p in positions
            ]
            # print(f'#tf: {len(tf_c)}')
            # print(f'transformed_pos: {transformed_pos}')
            paths.append(transformed_pos)

        else:
            print(f'{tag}')
            # print(f'tf: {tf_c}')
    return paths


def show_text(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    print(f'{root.tag}')
    pathes = []
    pathes = seek_tree(root, [], pathes)
    print(f'#pathes: {len(pathes)}')
    print('---')

    fig, ax = plt.subplots()
    for p in pathes:
        x = [xx[0] for xx in p]
        y = [yy[1] for yy in p]
        ax.plot(x, y)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim([0, 20])
    ax.set_ylim([20, 0])
    b = os.path.basename(filename).split('.')[0]
    img_path = os.path.join(os.path.dirname(__file__), f'../tmp/{b}.png')
    plt.savefig(img_path)
    print(f'save {img_path}')
    # tf = parse_tf('matrix(1,0,0,1,210,30)')
    # pp = transform([0, 0], [tf])
    # print(f'pp: {pp}')

    # print(parse_node('M7483,1883L7496,1883L7533,1993'))
    # print(parse_node('M7456.92,1809.5L7534.08,1809.5'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()
    show_text(args.filename)
