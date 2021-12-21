"""draw for github actions
"""
import argparse
import os
import glob

import matplotlib.pyplot as plt
from actions_toolkit import core

from EagleDraw import parse_tree
from colorful_logger import get_colorful_logger

logger = get_colorful_logger(__name__)

# matplotlib config
plt.style.use('dark_background')
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.facecolor"] = '#2b2b2b'
plt.rcParams["axes.facecolor"] = '#2b2b2b'
plt.rcParams["savefig.facecolor"] = '#2b2b2b'
plt.rcParams["font.family"] = 'sans-serif'


if __name__ == '__main__':
    workdir = os.getenv('GITHUB_WORKSPACE', '.')
    logger.info(f'workdir : {workdir}')
    os.chdir(workdir)

    for filename in glob.glob('*.lbr'):
        parse_tree(filename, 'imgs')
