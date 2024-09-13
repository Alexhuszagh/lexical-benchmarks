'''
    shared
    ======

    Shared functionality between processed.
'''

import typing
import os
import subprocess


def readlines(cmd: list[str], cwd: str = os.getcwd()) -> typing.Generator[str, None, None]:
    '''An iterable that iterates over lines in a file..'''
    process = subprocess.Popen(
        args=cmd,
        stdout=subprocess.PIPE,
        cwd=cwd,
    )
    for line in process.stdout:
        yield line.decode('ascii').strip()


def get_commit(cwd: str = os.getcwd()) -> str:
    '''Get the short commit for the current repo.'''
    line = next(readlines(['git', 'log', '--oneline'], cwd=cwd))
    return line.split(maxsplit=1)[0]


def get_rustc(
    rustc: str = 'rustc',
    toolchain: str | None = None,
    cwd: str = os.getcwd(),
) -> dict:
    '''Get the diagnostic rustc information.'''
    # The output will look something like this:
    #   rustc 1.81.0 (eeb90cda1 2024-09-04)
    #   binary: rustc
    #   commit-hash: eeb90cda1969383f56a2637cbd3037bdf598841c
    #   commit-date: 2024-09-04
    #   host: x86_64-pc-windows-msvc
    #   release: 1.81.0
    #   LLVM version: 18.1.7

    cmd = [rustc]
    if toolchain is not None:
        cmd.append(f'+{toolchain}')
    cmd += ['--version', '--verbose']
    lines = list(readlines(cmd, cwd=cwd))
    version, *rest = lines

    info = {}
    info['version'] = version.split(maxsplit=1)[1]
    for line in rest:
        key, value = line.split(':', maxsplit=1)
        info[key] = value

    return info
