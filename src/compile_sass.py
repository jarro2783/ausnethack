#!/usr/bin/env python

import argparse
import os
import sys
import sass

def main():
    parser = argparse.ArgumentParser(description='Compile sass')
    parser.add_argument('--sourcedir')
    parser.add_argument('--destdir')
    parser.add_argument('--minify',
        default=False, help='Minify the output', action='store_const',
        const=True)

    args = parser.parse_args()

    if args.sourcedir is None:
        args_error('sourcedir')

    if args.destdir is None:
        args_error('destdir')

    compile(args.sourcedir, args.destdir, args.minify)

def args_error(arg):
    print('{} must be given on the command line'.format(arg),
        file=sys.stderr)
    sys.exit(1)

def compile(source, dest, minify):

    kwargs = {}

    if minify:
        kwargs['output_style'] = 'compressed'

    sass.compile(dirname=(source, dest), **kwargs)

if __name__ == '__main__':
    main()
