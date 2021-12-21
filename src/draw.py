import argparse
import matplotlib.pyplot as plt

from colorful_logger import get_colorful_logger
from EagleDraw import parse_tree

logger = get_colorful_logger(__name__)

# matplotlib config
plt.style.use('dark_background')
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = '#2b2b2b'
plt.rcParams["axes.facecolor"] = '#2b2b2b'
plt.rcParams["savefig.facecolor"] = '#2b2b2b'
plt.rcParams["font.family"] = 'sans-serif'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    parser.add_argument(
        '--output', '-o', default='imgs', help='output path')
    args = parser.parse_args()
    print(args.filenames)
    for filename in args.filenames:
        parse_tree(filename, args.output)
