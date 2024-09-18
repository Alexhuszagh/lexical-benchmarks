'''
    plot
    ====

    Plot the changes between either different parsers/formatters or versions.

    This plots either the difference between specific commits as profiled by
    criterion or the difference between different libraries.

    If a single commit or no commits are provided, it

    TODO: Add examples
    TODO: Ensure we group the results by the kind of benchmark it is
        - Type (so, u8, u16, f32, etc.)
        - Benchmark
'''

import typing
import argparse
import json
import os
import subprocess
from collections import defaultdict
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

home = Path(__file__).absolute().parent

parser = argparse.ArgumentParser(
    prog='plot',
    description='plot the performance between libraries or commits.'
)
parser.add_argument(
    '-i',
    '--input',
    '--input-directory',
    dest='input',
    type=Path,
    help='the directory containing the results to plot. defaults to results/.',
    default=Path(__file__).parent / 'results',
)
parser.add_argument(
    '-o',
    '--output',
    '--output-directory',
    dest='output',
    type=Path,
    help='the path to save the plots to. defaults to results/',
    default=Path(__file__).parent / 'results',
)
parser.add_argument(
    '-s',
    '--style',
    help='the plotting style to use.',
    default='seaborn-v0_8-pastel'
)
parser.add_argument(
    '-r',
    '--repository',
    help='the path to the lexical repository.',
    required=True,
    type=Path,
)
parser.add_argument(
    '-c',
    '--commits',
    help='the list of commits to compare to. defaults to the latest commit.',
    nargs='*',
)
parser.add_argument(
    '-l',
    '--library',
    help='the llibrary to compare over multiple commits.',
)
parser.add_argument(
    '--show',
    help='if to show the plots in addition to saving them.',
    action='store_true',
)
args = parser.parse_args()
plt.style.use(args.style)

Flattened: typing.TypeAlias = tuple[Sequence[str], Sequence[str], MutableMapping[str, Sequence[float]]]


def sort_order(num_type: str) -> tuple[int, int]:
    '''Creates a custom sort order based on the numeric type.'''

    # NOTE: We want unsigned, then signed types, as ordered, then
    # go from smaller to larger types.
    num_type = num_type.strip()
    match num_type[0]:
        case 'u':
            kind = 0
        case 'i':
            kind = 1
        case 'f':
            kind = 2
        case _:
            raise ValueError(f'Got an invalid numeric type of "{num_type}".')

    return (kind, int(num_type[1:]))


def kind(num_type: str) -> str:
    '''Convert the numeric type to a given kind.'''
    num_type = num_type.strip()
    match num_type[0]:
        case 'u':
            return 'int'
        case 'i':
            return 'int'
        case 'f':
            return 'float'
        case _:
            raise ValueError(f'Got an invalid numeric type of "{num_type}".')


def get_commit_history(directory: Path | str, count: int = 5000) -> dict[str, int]:
    '''
    Get the entire commit history from a repo to determine commit order.

    Under the hood, this uses `git log -1 --pretty=format:%h`.
    '''

    command = ['git', 'log', f'-{count}', '--pretty=format:%h']
    process = subprocess.run(
        command,
        cwd=str(directory),
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )
    process.check_returncode()
    commits = process.stdout.decode('ascii').splitlines()

    return {j: i for i, j in enumerate(reversed(commits))}


def commit_key(commits: dict[str, int], value: str) -> int:
    '''Grabs the commit key by the largest, if it exists.'''
    if value in all_commits:
        return commits[value]
    return -1


# the naming convention follows:
#   {','.join(commits)}-{','.join(libraries)}
# then we have each bench group to bench separated in 4 categories:
#   to_float
#   to_integer
#   from_float
#   from_integer
# and the naming follows:
#   {group}-{name}.png
all_commits = set(os.listdir(args.input))
commits = get_commit_history(args.repository)
if not args.commits:
    args.commits = [max(commits, key=lambda k: commit_key(commits, k))]
if args.output is None:
    args.output = Path(f'{home}/results')


def scale_values(values: Mapping[str, Sequence[float]]) -> tuple[str, float]:
    '''Scale values to the proper magnitude, such as s or ns.'''
    # All criterion values are reported in ns, this isn't human friendly
    flattened = [i for j in values.values() for i in j]
    lower = min(flattened)
    # it's fine if we have like 5000, it's better than 0.5 for everything
    min_value = 5
    if lower >= min_value * 10**9:
        return ('s', 10**9)
    elif lower >= min_value * 10**6:
        return ('ms', 10**6)
    elif lower >= min_value * 10**3:
        return ('μs', 10**3)
    return ('ns', 1)


def plot(
    values: Mapping[str, Sequence[float]],
    # these are each individual labels in the legend
    labels: Sequence[str],
    # these are the x ticks
    ticks: Sequence[str],
    title: str,
    path: str | Path,
) -> None:
    '''Plot the values on a constrained histogram and save to file.'''

    # built the plot parameters
    x = np.arange(len(ticks))
    width = min(0.2, 0.8 / len(values))
    spacing = min(0.05, 0.2 / len(values)) + 1
    units, scale = scale_values(values)

    fig, ax = plt.subplots(layout='constrained')
    max_value = 1
    for multiplier, label in enumerate(labels):
        offset = width * multiplier * spacing
        adjusted = np.array(values[label]) / scale
        max_value = max(max_value, max(adjusted))
        ax.bar(x + offset, adjusted, width, label=label)

    # update our plot settings
    ax.set_title(title)
    ax.set_ylabel(f'Mean Time ({units})')
    ax.set_xticks(x + width / 4 * len(ticks), ticks)
    ax.set_xlim(-0.5, max(1, max(x) + 1))
    ax.set_ylim(0, 1.2 * max_value)
    ncols = max(int(len(values) // 4), 1)
    ax.legend(loc='upper right', ncols=ncols)

    plt.savefig(path, bbox_inches='tight')
    if args.show:
        plt.show()
    else:
        plt.close('all')


def flatten_values(nested: Sequence[tuple[str, float, str]]) -> Flattened:
    '''Flatten our groups values for plotting.'''

    # NOTE: We want this to be the labels, ticks, then values
    nested.sort(key=lambda x: (sort_order(x[0]), x[2]))
    ticks = sorted({i[0] for i in nested}, key=sort_order)
    labels = sorted({i[2] for i in nested})
    values = defaultdict(list)
    for num_type, value, label in nested:
        values[label].append(value)

    return (labels, ticks, values)


def flatten_by_mean(mean: Mapping[str, int]) -> Mapping[str, Mapping[str, Flattened]]:
    '''Flatten the outputs from a single mean set of values to a flat structure.'''

    result = defaultdict(dict)
    for group, benches in mean.items():
        # group our benches by type, then we can plot the values
        # this group items by types, into something like the following format:
        #   {'parse':
        #       {'float': [
        #           ('f32', 9.979, 'core'),
        #           ('f32', 8.7968, 'lexical'),
        #       ]
        #   }}
        by_types = defaultdict(lambda: defaultdict(list))
        for key in benches:
            split = key.split('_')
            if len(split) != 3:
                continue
            type, num_type, library = key.split('_')
            by_type = by_types[type][kind(num_type)]
            by_type.append((num_type, benches[key], library))

        # now we want to iterate over everything and then group it appropriately
        # for example, within a group we want:
        #   labels: ['f32', 'f64']
        for type, type_values in by_types.items():
            for num_type, nested in type_values.items():
                result[group][type] = (num_type, flatten_values(nested))

    return result


def plot_libraries(commit: str) -> None:
    '''Plot a comparison between different libraries for the given benchmarks.'''

    # NOTE: The format for these is always `{type}_{type}_{library}`, however, type can be odd
    #   We want to plot it by type, increasing in size, for each category, with each library
    #   in the same group. So for example, pairing `std`
    input = args.input / commit / 'flatbench.json'
    with input.open() as file:
        benches = json.load(file)
    mean = benches['mean']
    flattened = flatten_by_mean(mean)
    for group, values in flattened.items():
        for type, (num_type, data) in values.items():
            labels, ticks, values = data
            title = group.title().replace('_', ' ')
            title = f'{title} — {type.title()} {num_type.title()}'
            filename = f'{group} - {type} {num_type} - {",".join(labels)}.png'
            path = args.output / commit / 'plot' / filename
            path.parent.mkdir(exist_ok=True, parents=True)
            plot(values, labels, ticks, title, path)


def plot_commits(library: str, commits: Sequence[str]) -> None:
    '''Plot a comparison between commits for the given benchmarks for each library.'''

    # NOTE: If all libraries are provided, then it will grab the all relevant libraries and
    # iterate over each.
    inputs = [args.input / i / 'flatbench.json' for i in commits]
    benches = []
    for input in inputs:
        with input.open() as file:
            benches.append(json.load(file))
    means = [i['mean'] for i in benches]
    # FIXME: Need to implement this
    grouped = [flatten_by_mean(i) for i in means]
    raise NotImplementedError('TODO: Plot comparisons between commits.')


# if we have only a single commit, we compare by commit, otherwise we compare by library
if len(args.commits) == 1 and args.library:
    raise ValueError('Cannot provide both a commit and a single library.')
elif len(args.commits) == 1:
    plot_libraries(args.commits[0])
elif args.library:
    plot_commits(args.library, args.commits)
else:
    raise ValueError('Must provide either a single commit or a single library.')
