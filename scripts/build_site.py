"""Stage only the standalone report as the GitHub Pages entry point."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT):
    report = (root / 'reports/decision-report.html').read_text()
    if '{{' in report or 'synthetic' not in report.lower():
        raise ValueError('Generate a complete, disclosed report before publishing')
    destination = root / '_site'
    if destination.is_symlink():
        raise ValueError('Refusing to replace a symlinked build directory')
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()
    # Keep deployment independent of the repository name / Pages base path.
    report = report.replace('</footer>', ' · <a href="https://github.com/RichaShiny/challenge-lab">View source and case study</a></footer>')
    (destination / 'index.html').write_text(report)
    print('Built _site/index.html; no database, logs or source files included.')


if __name__ == '__main__':
    build()
