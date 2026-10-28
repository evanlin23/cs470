"""Bundle the current report as a standalone Overleaf project; optionally compile it."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
README = """# BridgeFinder midterm — editable Overleaf project

In Overleaf select New Project → Upload Project, then upload this ZIP.
Set the main document to main.tex and the compiler to pdfLaTeX (the defaults
should work). Recompile; references may require a second pass.

Edit main.tex. Its % Rewrite purpose: comments explain what each paragraph
needs to accomplish; they do not appear in the PDF. The section-to-rubric map
is in review/rewrite-guide.md. The bibliography is embedded at the end, so no BibTeX or Biber
step is required. Figures are included at their existing relative paths under
midterm/review/screenshots/. Keep that structure unless you update main.tex.

review/rubric-review.md contains the strict editorial assessment.
review/rewrite-guide.md gives Evan and Eric the final rewrite priorities and
facts that must remain synchronized. These Markdown files do not appear in
the compiled paper. The supplied rubric does not state a page limit.
Check the layout after manual edits.

This archive excludes prototype data, code and private study keys. It was
compiled locally after clean extraction using pdfLaTeX. No claim is made
that it has already been uploaded to, or compiled on, the Overleaf service.
"""


def package(destination, verify=False):
    source = ROOT / 'midterm/latex/main.tex'
    figures = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', source.read_text())
    files = {'main.tex': source}
    files.update({name: ROOT / name for name in figures})
    for name in ['rubric-review.md', 'rewrite-guide.md', 'analysis-notes.md', 'style-review.md']:
        files['review/' + name] = ROOT / 'midterm/review' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in files.items():
            archive.write(path, name)
        archive.writestr('README.md', README)
    if verify:
        with tempfile.TemporaryDirectory(prefix='bridgefinder-overleaf-') as directory:
            folder = Path(directory)
            with zipfile.ZipFile(destination) as archive:
                archive.extractall(folder)
            for name, original in files.items():
                if (folder / name).read_bytes() != original.read_bytes():
                    raise RuntimeError(f'Archive differs from current source: {name}')
            if shutil.which('pdflatex'):
                for _ in range(2):
                    run = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
                                         cwd=folder, capture_output=True, text=True)
                    if run.returncode:
                        raise RuntimeError(run.stdout[-5000:])
                log = (folder / 'main.log').read_text()
                if re.search(r'LaTeX Warning|Overfull|Underfull|undefined references|undefined citations', log):
                    raise RuntimeError('Extracted project has compilation warnings; inspect the source.')
            elif shutil.which('tectonic'):
                run = subprocess.run(['tectonic', 'main.tex'], cwd=folder, capture_output=True, text=True)
                if run.returncode:
                    raise RuntimeError(run.stderr or run.stdout)
            else:
                raise RuntimeError('Neither pdflatex nor tectonic found for verification.')
            def pdf_text(path):
                return subprocess.check_output(['pdftotext', str(path), '-'], text=True)
            if pdf_text(folder / 'main.pdf') != pdf_text(ROOT / 'midterm/midterm.pdf'):
                raise RuntimeError('Extracted project PDF text differs from the current report PDF.')
            print('Verified: clean extraction, matching source/assets, two pdfLaTeX passes, no warnings, matching report text.')
    print(f'Created {destination} ({destination.stat().st_size:,} bytes)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'midterm/bridgefinder-midterm-overleaf.zip')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    package(args.out.resolve(), args.verify)
