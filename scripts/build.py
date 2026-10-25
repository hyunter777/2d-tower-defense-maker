"""Build the English manual and generated API; validate the combined static site."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parents[1] / '.work/docs-site' if ROOT.name == 'site' and ROOT.parent.name == 'docs' else ROOT / 'site'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise ValueError('Build output must not contain the documentation source.')
    env = dict(os.environ, NO_MKDOCS_2_WARNING='1')
    subprocess.run([sys.executable, '-m', 'mkdocs', 'build', '--strict', '--site-dir', str(output)], cwd=ROOT, env=env, check=True)
    docfx = shutil.which('docfx')
    if not docfx:
        raise RuntimeError('Install DocFX 2.81.0 before building the API reference.')
    subprocess.run([docfx, 'build', 'docfx/docfx.json', '--output', str(output / 'api'), '--warningsAsErrors', '--disableGitFeatures'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'scripts/check_content.py', '--site', str(output)], cwd=ROOT, check=True)
    print(f'Documentation site: {output}')

if __name__ == '__main__':
    main()
