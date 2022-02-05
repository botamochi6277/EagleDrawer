import argparse

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

    return t


def seek_tree(tree: ET.ElementTree, tf=[]):
    for child in tree:
        tf_c = copy.deepcopy(tf)
        tag = child.tag
        attr = child.attrib
        # print(tag)
        # print(attr)

        if 'transform' in attr:
            if len(tf_c) == 0:
                tf_c = parse_tf(attr['transform'])
            else:
                tf_c.append(parse_tf(attr['transform']))

        if tag == '{http://www.w3.org/2000/svg}g':
            seek_tree(child, tf_c)
        else:
            # print(f'{tag}')
            print(f'tf: {tf_c}')


def show_text(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    print(f'{root.tag}')
    print('---')
    seek_tree(root, [])

    print(parse_tf('matrix(1,0,0,1,210,30)'))
    print(parse_tf("matrix(0.0889855,0,0,-0.0889855,-388.103,185.482)"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()
    show_text(args.filename)
