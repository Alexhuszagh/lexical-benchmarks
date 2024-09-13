#!/usr/bin/env python
'''
    flatbench
    =========

    Create a baseline for metrics between various tools.

    This finds all the results from criterion in the target directories,
    and then concatenates them and joins various tooling into a single
    file.

    The file will be output to `/target/profiling.json` (by default).
'''

import argparse
import json
from collections import defaultdict
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
    default=Path(__file__).absolute().parent / 'target',
)
parser.add_argument(
    '-o',
    '--output',
    '--output-file',
    dest='output',
    type=Path,
    help='the path file name to save the report to. defaults to `results/{{commit}}/flatbench.json`.',
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
    args.output = Path(f'{home}/results/{commit}/flatbench.json')
args.output.parent.mkdir(exist_ok=True, parents=True)

# the structure is:
#   criterion -> group -> bench -> profile
# load all our files, and collate them by group and the like
criterion = (args.target / 'criterion').absolute()
files = criterion.rglob(f'*/*/{args.profile}/estimates.json')
results = defaultdict(lambda: defaultdict(dict))
for file in files:
    group = file.parent.parent.parent.name
    name = file.parent.parent.name
    with (criterion / file).open(encoding='utf-8') as fp:
        results[group][name] = json.load(fp)

# now we need to collate everything by groups, etc.
profiling = defaultdict(lambda: defaultdict(dict))
for group, items in results.items():
    for name, item in items.items():
        # extract our useful info
        mean = item['mean']
        mean_ci = mean['confidence_interval']
        std_dev = item['std_dev']

        # update our info
        profiling['mean'][group][name] = mean['point_estimate']
        profiling['lower'][group][name] = mean_ci['lower_bound']
        profiling['upper'][group][name] = mean_ci['upper_bound']
        profiling['confidence'][group][name] = mean_ci['confidence_level']
        profiling['std_dev'][group][name] = std_dev['point_estimate']

with open(args.target / args.output, 'w', encoding='utf-8') as fp:
    json.dump(profiling, fp, indent=2)
