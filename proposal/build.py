"""Build proposal.md into proposal.html (two-column, CHI-style) and proposal.pdf.

Front matter (the title, author line and figure, i.e. everything before the
first "## " heading) is set full width; the body flows in two columns; the
references start on page 2, since the proposal allows unlimited reference space.

  pip install markdown && python3 build.py   (PDF needs node + playwright)
"""
import os
import re
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = """
@page { size: Letter; margin: 0.5in 0.55in 0.5in 0.55in; }
body { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 8.9pt; line-height: 1.22;
       color: #111; margin: 0; }
h1 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 14.5pt; margin: 0 0 3pt; line-height: 1.15; }
.authors { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.6pt; color: #333; margin-bottom: 6pt; }
figure { margin: 0 0 6pt; }
figure img { width: 100%; display: block; }
figcaption { font-family: "Liberation Sans", Arial, sans-serif; font-size: 7.4pt; line-height: 1.25; margin-top: 3pt; color: #222; }
.cols { column-count: 2; column-gap: 0.24in; text-align: justify; hyphens: auto; }
h2 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 9.4pt; margin: 5pt 0 1.5pt; break-after: avoid; }
p { margin: 0 0 3.2pt; }
ol { margin: 0 0 3pt; padding-left: 13pt; } li { margin-bottom: 1.5pt; }
.refs { break-before: page; font-size: 8.4pt; }
.refs h2 { margin-top: 0; }
.refs p { margin: 0 0 2.5pt; text-indent: -16pt; padding-left: 16pt; text-align: left; }
"""


def build():
    src = open(os.path.join(HERE, "proposal.md")).read()
    left = re.findall(r"\{\{[A-Z_]+\}\}", src)
    if left:
        print("warning: unfilled placeholders:", sorted(set(left)), file=sys.stderr)
    front, body = src.split("\n## ", 1)
    body = "## " + body
    body, refs = body.split("\n## References", 1)

    title = re.search(r"^# (.+)$", front, re.M).group(1)
    authors = re.search(r"^(?!#)(?!!\[)(\S.+)$", front, re.M).group(1)
    fig = re.search(r"!\[(.+?)\]\((.+?)\)", front, re.S)
    caption = markdown.markdown(fig.group(1))[3:-4]

    body_html = markdown.markdown(body, extensions=["sane_lists"])
    ref_lines = [l for l in refs.strip().splitlines() if l.strip()]
    refs_html = "".join(markdown.markdown(l) for l in ref_lines)

    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head>
<body><h1>{title}</h1><div class="authors">{markdown.markdown(authors)[3:-4]}</div>
<figure><img src="{fig.group(2)}" alt="Figure 1"><figcaption><b>Figure 1.</b> {caption.replace('Figure 1. ', '')}</figcaption></figure>
<div class="cols">{body_html}</div>
<div class="refs"><h2>References</h2>{refs_html}</div></body></html>"""
    out = os.path.join(HERE, "proposal.html")
    open(out, "w").write(html)
    print("wrote", out, f"({len(re.sub('<[^>]+>', ' ', body_html).split())} words in body)")

    js = os.path.join(HERE, "_pdf.js")
    open(js, "w").write("""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle' });
  await p.pdf({ path: process.argv[3], format: 'Letter', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();""")
    env = dict(os.environ)
    env.setdefault("NODE_PATH", subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", js, out, os.path.join(HERE, "proposal.pdf")], check=True, env=env)
    os.remove(js)
    print("wrote", os.path.join(HERE, "proposal.pdf"))


if __name__ == "__main__":
    build()
