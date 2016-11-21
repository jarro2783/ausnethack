#!/usr/bin/env python3

import argparse
import os
import sys
import source_files as source
import yaml

sourcedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(sourcedir, 'src'))
import ninja_syntax

def main(assetmap=None):
    ninja = ninja_syntax.Writer(open('build.ninja', 'w'))

    ninja.include('rules.ninja')
    ninja.newline()

    build_files = []
    version_files = []

    default_rules = []

    for sass in source.css:
        parts = sass.split('.')
        css = "{}.css".format(parts[0])
        built = ".build/css/{}".format(css)
        ninja.build(built,
                    'build_sass',
                    "css/{}".format(sass),
                    'src/compile_sass.py')

        build_files.append(built)
        default_rules.append(built)

    assetpath = 'site/assets.map.yaml'
    ninja.build(assetpath, 'asset_map', build_files)
    default_rules.append(assetpath)

    if assetmap is not None:
        assets = open(assetmap)
        versions = yaml.load(assets)

        for asset in versions:
            version = versions[asset]
            target = '.'+version
            ninja.build(target, 'copy', ".build/{}".format(asset))
            default_rules.append(target)

    ninja.build('build.ninja', 'rebuild_ninja', 'site/assets.map.yaml')

    # tests
    ninja.newline()
    ninja.build('test', 'phony', 'do_tests')
    ninja.build('do_tests', 'runtests')
    ninja.newline()

    ninja.default(default_rules);

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='configure build')
    parser.add_argument(
        '--assetmap',
        help='generate versioned rules from an asset map')
    args = parser.parse_args()
    main(args.assetmap)
