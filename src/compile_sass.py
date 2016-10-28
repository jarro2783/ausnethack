#!/usr/bin/env python

import argparse
import hashlib
import os
import pathlib
import sys
import sass

def main():
    parser = argparse.ArgumentParser(description='Compile sass')
    parser.add_argument('--input')
    parser.add_argument('--outdir')
    parser.add_argument('--version')
    parser.add_argument('--minify',
        default=False, help='Minify the output', action='store_const',
        const=True)
    parser.add_argument('--deps', help='Write dependencies to file')

    args = parser.parse_args()

    if args.input is None:
        args_error('input')

    if args.outdir is None:
        args_error('outdir')

    if args.version is None:
        args_error('version')

    compile(args.input, args.outdir, args.version, args.minify, args.deps)

def args_error(arg):
    print('{} must be given on the command line'.format(arg),
        file=sys.stderr)
    sys.exit(1)

def gather_deps(deps, src):
    def add_dep(path):
        deps.append("css/_{}.scss".format(path))
        return None
    return add_dep

def make_path(name):
    path = pathlib.Path(name)
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True)

def build_destination(outdir, infile, version):
    parts = infile.split('.')

    path = pathlib.Path(outdir)
    path = path.joinpath("{}-{}.css".format(parts[0], version))
    return str(path)

def compile(source, outdir, version, minify, deps):

    kwargs = {}

    if minify:
        kwargs['output_style'] = 'compressed'

    if deps is not None:
        dependencies = []
        kwargs['importers'] = [(0, gather_deps(dependencies, source))]

    result = sass.compile(filename=source, **kwargs)

    make_path(version)

    version_file = open(version, 'w')
    sha256 = hashlib.sha256(result.encode('utf-8'))
    version_hash = sha256.hexdigest()[0:16]
    dest = build_destination(outdir, source, version_hash)
    version_file.write(dest)
    version_file.close()

    make_path(dest)

    output = open(dest, 'w')
    output.write(result)
    output.close()

    if deps is not None:
        output = open(deps, 'w')
        output.write("{}: {}\n".format(version, ' '.join(dependencies)))

if __name__ == '__main__':
    main()
