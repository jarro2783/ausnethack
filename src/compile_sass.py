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
    parser.add_argument('--minify',
        default=False, help='Minify the output', action='store_const',
        const=True)
    parser.add_argument('--deps', help='Write dependencies to file')

    args = parser.parse_args()

    if args.input is None:
        args_error('input')

    if args.outdir is None:
        args_error('outdir')

    compile(args.input, args.outdir, args.minify, args.deps)

def args_error(arg):
    print('{} must be given on the command line'.format(arg),
        file=sys.stderr)
    sys.exit(1)

def gather_deps(deps, src):
    def add_dep(path):
        deps.append("static/css/_{}.scss".format(path))
        return None
    return add_dep

def make_path(name):
    path = pathlib.Path(name)
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True)

def build_destination(outdir, infile):
    parts = infile.split('.')

    css = "{}.css".format(parts[0])
    build = pathlib.Path('.build', css)
    map_path = pathlib.Path(css+'.map')
    return (str(build), str(map_path))

def compile(source, outdir, minify, deps):

    kwargs = {}

    if minify:
        kwargs['output_style'] = 'compressed'

    if deps is not None:
        dependencies = []
        kwargs['importers'] = [(0, gather_deps(dependencies, source))]

    dest,destmap = build_destination(outdir, source)

    result = sass.compile(
        filename=source,
        source_map_filename='maps/'+destmap,
        **kwargs)

    make_path(dest)

    output = open(dest, 'w')
    output.write(result[0])
    output.close()

    map_out = pathlib.Path('.build', destmap)
    make_path(map_out)

    output = open(str(map_out), 'w')
    output.write(result[1])
    output.close()

    if deps is not None:
        output = open(deps, 'w')
        output.write("{}: {}\n".format(dest, ' '.join(dependencies)))

if __name__ == '__main__':
    main()
