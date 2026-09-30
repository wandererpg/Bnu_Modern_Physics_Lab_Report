#!/usr/bin/env python3
"""Expand all five registered templates into separately named local examples.

Does not touch experimental reports. Existing source files are preserved.
"""
import argparse
import json
import shutil
from pathlib import Path


def create(output: Path):
    assets = Path(__file__).resolve().parent.parent / 'assets'
    root = assets / 'report_templates'
    registry = json.loads((root / 'registry.json').read_text(encoding='utf-8'))
    planned = [(entry, output / ('MVP_' + entry['source'].removeprefix('template_'))) for entry in registry['templates']]
    existing = [str(path) for _, path in planned if path.exists()]
    if existing:
        raise FileExistsError('Choose a new output folder; existing MVPs are preserved: ' + ', '.join(existing))
    output.mkdir(parents=True, exist_ok=True)
    (output / 'build').mkdir(exist_ok=True)
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(assets / 'branding' / 'bnu_logo.png', output / 'assets' / 'bnu_logo.png')
    shutil.copyfile(assets / 'thu_template' / 'thuemp.cls', output / 'thuemp.cls')
    parts = {
        'common': root / 'common.tex',
        'layout_v2': root / 'layout_v2.tex',
        'metadata': root / 'examples' / 'mvp_metadata.tex',
        'body': root / 'examples' / 'mvp_body.tex',
    }
    for entry, target in planned:
        source = (root / entry['source']).read_text(encoding='utf-8')
        for key, path in parts.items():
            source = source.replace(r'\input{report_template/' + key + '}', path.read_text(encoding='utf-8').rstrip())
        target.write_text('% !TEX encoding = UTF-8\n' + source, encoding='utf-8')
        print(target.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    create(parser.parse_args().output.resolve())
