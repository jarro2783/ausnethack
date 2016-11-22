#!/usr/bin/env python3

import argparse
import os
import pathlib
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
        basepath = pathlib.Path('static', 'css')
        built = pathlib.Path('.build').joinpath(basepath, css)
        map_path = pathlib.Path('.build', 'static', 'css', css+'.map')
        ninja.build([str(built), str(map_path)],
                    'build_sass',
                    "static/css/{}".format(sass),
                    'src/compile_sass.py')

        build_files.append(str(built))
        default_rules.append(str(built))

    assetpath = 'site/assets.map.yaml'
    ninja.build(assetpath, 'asset_map', build_files)
    default_rules.append(assetpath)

    if assetmap is not None:
        assets = open(assetmap)
        versions = yaml.load(assets)

        for asset in versions:
            version = versions[asset]
            outpath = pathlib.Path('.'+version)
            ninja.build(str(outpath),
                        'copy', ".build/static/{}".format(asset))
            default_rules.append(str(outpath))

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
