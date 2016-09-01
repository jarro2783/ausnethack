#!/usr/bin/env python

import argparse
import os
import sys
import sass

def main():
    parser = argparse.ArgumentParser(description='Compile sass')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--minify',
        default=False, help='Minify the output', action='store_const',
        const=True)
    parser.add_argument('--deps', help='Write dependencies to file')

    args = parser.parse_args()

    if args.input is None:
        args_error('input')

    if args.output is None:
        args_error('output')

    compile(args.input, args.output, args.minify, args.deps)

def args_error(arg):
    print('{} must be given on the command line'.format(arg),
        file=sys.stderr)
    sys.exit(1)

def gather_deps(deps, src):
    def add_dep(path):
        deps.append("css/_{}.scss".format(path))
        return None
    return add_dep

def compile(source, dest, minify, deps):

    kwargs = {}

    if minify:
        kwargs['output_style'] = 'compressed'

    if deps is not None:
        dependencies = []
        kwargs['importers'] = [(0, gather_deps(dependencies, source))]

    result = sass.compile(filename=source,
        **kwargs)

    output = open(dest, 'w')
    output.write(result)

    if deps is not None:
        output = open(deps, 'w')
        output.write("{}: {}\n".format(dest, ' '.join(dependencies)))

if __name__ == '__main__':
    main()
