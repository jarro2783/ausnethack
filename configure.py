#!/usr/bin/env python3

'''
Configures the wwwnethack build.
'''

import os
import pathlib
import sys
import source_files as source
import yaml

SOURCEDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SOURCEDIR, 'src'))
import ninja_syntax

def main():
    #pylint:disable=too-many-locals
    '''The main entry point.'''
    ninja = ninja_syntax.Writer(open('build.ninja', 'w'))

    ninja.include('rules.ninja')
    ninja.newline()

    build_files = []
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

    for bundle, modules in source.js.items():
        basepath = pathlib.Path('static', 'js')
        built = pathlib.Path('.build').joinpath(basepath, bundle)
        sources = [
            str(pathlib.Path('static', 'js').joinpath(name))
            for name in modules
        ]
        ninja.build(str(built), 'require_js', sources)
        build_files.append(str(built))
        default_rules.append(str(built))

    ausnethack = '.build/static/js/ausnethack.js'
    build_files.append(ausnethack)
    ninja.build(
        ausnethack,
        'copy',
        'static/js/ausnethack.js')
    default_rules.append(ausnethack)

    assetpath = 'site/assets.map.yaml'
    ninja.build(assetpath, 'asset_map', build_files)
    default_rules.append(assetpath)

    assetmap = pathlib.Path('site/assets.map.yaml')
    if assetmap.exists():
        assets = open(str(assetmap))
        versions = yaml.load(assets)

        for asset in versions:
            version = versions[asset]
            outpath = pathlib.Path('.'+version)
            ninja.build(str(outpath),
                        'copy', ".build/static/{}".format(asset))
            default_rules.append(str(outpath))

    ninja.build('build.ninja', 'rebuild_ninja', 'site/assets.map.yaml')

    # favicon.ico
    ninja.build('assets/favicon.ico', 'copy', 'static/favicon.ico')
    default_rules.append('assets/favicon.ico')

    # tests
    ninja.newline()
    ninja.build('test', 'phony', 'do_tests')
    ninja.build('do_tests', 'runtests')

    # linter
    ninja.newline()
    ninja.build(
        'lint',
        'phony',
        [
            'lint_main',
            'lint_lib',
            'lint_configure',
            'lint_require',
        ])
    ninja.build('lint_main', 'linter', variables={'SOURCE':'site/main.py'})
    ninja.build('lint_lib', 'linter', variables={'SOURCE':'site/wwwnethack'})
    ninja.build(
        'lint_configure',
        'linter',
        variables={'SOURCE': 'configure.py', 'PPATH': 'src'})
    ninja.build(
        'lint_require',
        'linter',
        variables={'SOURCE': 'src/require.py'})

    ninja.newline()
    ninja.default(default_rules)

if __name__ == '__main__':
    main()
