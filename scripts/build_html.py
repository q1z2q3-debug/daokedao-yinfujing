# -*- coding: utf-8 -*-
"""把《润泽说 道可道之坛经·通释》编译成单文件 HTML。
用法：python3 scripts/build_html.py （需 pandoc）
"""
import pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
MD = BOOK / "润泽说 道可道之黄帝阴符经·通释.md"
OUT = BOOK / "阴符经·阅读版.html"
TMP = pathlib.Path("/tmp/yinfu_src.md")
BODY = pathlib.Path("/tmp/yinfu_body.html")

src = MD.read_text(encoding="utf-8")
src = re.sub(r"^---\n.*?\n---\n", "", src, count=1, flags=re.S)
src = src.replace("# 润泽说 道可道之黄帝阴符经\n## 黄帝阴符经 · 通释\n", "")
TMP.write_text(src, encoding="utf-8")

subprocess.run(["pandoc", str(TMP), "-f", "markdown+hard_line_breaks",
                "-t", "html5", "--no-highlight", "-o", str(BODY)], check=True)
body = BODY.read_text(encoding="utf-8")
body = re.sub(r"<h([234])\s*\n\s*", r"<h\1 ", body)
body = body.replace("<blockquote>", '<blockquote class="sutra">')
body = body.replace("<table>", '<table class="t">')

import base64
FIG = BOOK / "figures"
def fig_wuzei():
    svg = (FIG / "图1-五贼制化循环.svg").read_text(encoding="utf-8")
    return ('<figure class="fig">%s<figcaption>图一　五贼制化循环<br><span>实线相生为德，虚线相克为贼；害中含恩，裁而后成。</span></figcaption></figure>' % svg)

def _unused_cup():
    png = (FIG / "x.png").read_bytes()
    b64 = base64.b64encode(png).decode()
    return ('<figure class="fig"><img alt="三才五蕴太极空杯" src="data:image/png;base64,%s">'
            '<figcaption>图一　三才五蕴太极空杯（《心经通释》原版模型，图二原型照录）<br>'
            '<span>色为杯底，受想行识为四壁；空性超越器相边界，芥子纳须弥。</span></figcaption></figure>' % b64)

def fig_sandao():
    svg = (FIG / "图2-三盗三才循环.svg").read_text(encoding="utf-8")
    return ('<figure class="fig">%s<figcaption>图二　三盗三才循环<br>'
            '<span>天地、万物、人互为盗；取用有度，三才乃安。</span></figcaption></figure>' % svg)

m = re.search(r"<!-- FRONTIS -->(.*?)<!-- /FRONTIS -->", body, re.S)
frontis = m.group(1).strip() if m else ""
if m:
    body = body.replace(m.group(0), "")
body = body.replace("<!-- FIG:wuzei -->", fig_wuzei()).replace("<!-- FIG:sandao -->", fig_sandao())

parts = re.findall(r'<h1 id="([^"]+)"[^>]*>(.*?)</h1>', body, flags=re.S)
nav = "\n".join('<li><a href="#%s"><i>·</i><span>%s</span></a></li>'
                % (hid, re.sub(r"<[^>]+>", "", raw).strip())
                for hid, raw in parts)

body = re.sub(r"<h1 ", '<h2 class="ch" ', body)
body = body.replace("</h1>", "</h2>")

FAVICON = ("<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' fill='%23994433'/%3E"
           "%3Ctext x='32' y='46' font-size='30' text-anchor='middle' "
           "fill='%23F7F4EE' font-family='serif'%3E%E9%99%B8%3C/text%3E%3C/svg%3E\">")

SHELL = pathlib.Path(__file__).parent.joinpath("_shell.html").read_text(encoding="utf-8")
out = SHELL.replace("__NAV__", nav).replace("__FRONTIS__", frontis).replace("__BODY__", body).replace("__FAVICON__", FAVICON)
OUT.write_text(out, encoding="utf-8")
print("ok", len(out), "chars |", len(parts), "toc items |", OUT)
