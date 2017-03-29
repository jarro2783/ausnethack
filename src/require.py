#!/usr/bin/env python

'''Builds the js require functionality.

Takes an output bundle and the inputs.
'''

import argparse
from pathlib import PurePath
import sys

def main():
    '''The main entry point.'''

    parser = argparse.ArgumentParser(description='Compile bundles')
    parser.add_argument('--output')
    parser.add_argument('inputs', nargs='+')

    args = parser.parse_args()

    compile_bundle(args.output, args.inputs)

def compile_bundle(output, inputs):
    '''Compiles the bundle given by output from input files.'''

    if not isinstance(output, str):
        print("Output must be a file name")
        sys.exit(1)

    if len(inputs) == 0:
        print("You must specify the module to build", file=sys.stderr)
        sys.exit(1)

    result = open(output, 'w')
    require = open('src/require.js')

    result.write('var modules = {')
    for module in inputs:
        write_module(result, module)
    result.write('}')

    result.write(require.read())

def write_module(result, module):
    '''Write the modules out.'''
    module_file = open(module)
    contents = module_file.read()

    module_path = PurePath(module)
    module_name = module_path.parts[-1].split('.')[0]

    result.write(
        '''"{}": function(require, exports) {{
  {}
}},
'''.format(module_name, contents))

if __name__ == '__main__':
    main()
