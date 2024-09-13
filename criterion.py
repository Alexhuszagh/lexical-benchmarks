'''
    criterion
    =========

    Copies the criterion bench results to the target directory.

    Due to the large size of criterion data, it's generally not
    recommended to use this.
'''

import argparse
import os
import shutil
from pathlib import Path

import shared

home = Path(__file__).absolute().parent

parser = argparse.ArgumentParser(
    prog='flatbench',
    description='generate flate profiling results to compare between runs.'
)
parser.add_argument(
    '-t',
    '--target',
    '--target-directory',
    dest='target',
    type=Path,
    help='the base directory containing the build info. defaults to `target/`',
    default=Path(__file__).parent / 'target',
)
parser.add_argument(
    '-o',
    '--output',
    '--output-directory',
    dest='output',
    type=Path,
    help='the path to save the criterion benchmark files to.',
)
parser.add_argument(
    '-p',
    '--profile',
    help='the name of the profile to load the results from.',
    default='base',
)
args = parser.parse_args()
if args.output is None:
    commit = shared.get_commit(str(args.target.parent))
    args.output = Path(f'{home}/results/{commit}')
args.output.mkdir(exist_ok=True, parents=True)

# the structure is:
#   criterion -> group -> bench -> profile
# load all our files, and collate them by group and the like
criterion = (args.target / 'criterion').absolute()
estimates = criterion.rglob(f'*/*/{args.profile}/estimates.json')
for estimate in estimates:
    directory = estimate.parent
    group = directory.parent.parent.name
    name = directory.parent.name
    files = os.listdir(directory)
    output = args.output / group / name
    output.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.copy2(directory / file, output)
