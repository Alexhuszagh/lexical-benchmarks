#!/usr/bin/env python
'''
    metadata
    ========

    Gets and exports the current benchmark metadata.

    This includes the CPU info, including detailed information,
    the OS including revision number, and the full Rust toolchain
    information.
'''

import argparse
import json
import platform
from pathlib import Path

import cpuinfo  # pyright: ignore[reportMissingImports]
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
    help='the file name to save the criterion files to. defaults `/results/{{commit}}`.',
)
parser.add_argument(
    '--toolchain',
    help='an optional toolchain to get the rust information from',
)
parser.add_argument(
    '--rustc',
    help='the name or path to the rustc executable',
    default='rustc'
)
args = parser.parse_args()
commit = shared.get_commit(str(args.target.parent))
if args.output is None:
    args.output = Path(f'{home}/results/{commit}/metadata.json')
args.output.parent.mkdir(exist_ok=True, parents=True)

metadata = {}
metadata['commit'] = commit

# get our platform data
uname = platform.uname()
metadata['platform'] = plat = {}
plat['processor'] = platform.processor()
plat['machine'] = platform.machine()
plat['version'] = platform.version()
plat['release'] = platform.release()
plat['system'] = platform.system()

# get more comprehensive CPU information
metadata['cpuinfo'] = cpuinfo.get_cpu_info()
metadata['cpuinfo'].pop('python_version', None)

# get our full rsust info
metadata['rust'] = shared.get_rustc(args.rustc, args.toolchain)

with args.output.open('w', encoding='utf-8') as file:
    json.dump(metadata, file, indent=2)
