import argparse
from ast import parse
from typing import Tuple

import xml.etree.ElementTree as ET
import numpy as np
import re
import copy


def parse_tf(s):
    # matrix(a,b,c,d,tx,ty)
    t = re.findall(
        r'matrix\(([\S]+?),([\S]+?),([\S]+?),([\S]+?),([\S]+?),([\S]+?)\)', s)
    # mat = [ [a,c,tx],
    # [b,d,ty],
    # [0,0,1]
    # ]
    # print(t)
    a, b, c, d, tx, ty = t[0]
    mat = np.matrix([[float(a), float(c), float(tx)],
                     [float(b), float(d), float(ty)],
                     [0, 0, 1]
                     ])
    return mat


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


def seek_tree(tree: ET.ElementTree, tf=[]):
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
            seek_tree(child, tf_c)
        elif tag == '{http://www.w3.org/2000/svg}path':
            d = attr['d']
            print(d)
        else:
            print(f'{tag}')
            # print(f'tf: {tf_c}')


def show_text(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    print(f'{root.tag}')
    seek_tree(root, [])

    print('---')
    print(parse_tf('matrix(1,0,0,1,210,30)'))
    print(parse_tf("matrix(0.0889855,0,0,-0.0889855,-388.103,185.482)"))

    print(parse_node('M7483,1883L7496,1883L7533,1993'))
    print(parse_node('M7456.92,1809.5L7534.08,1809.5'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()
    show_text(args.filename)
