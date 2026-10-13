"""Builds QR codes and print-ready business cards (3.5 x 2 in, 0.125 in bleed) from the same card data."""
import asyncio, base64, os, sys
import segno
from playwright.async_api import async_playwright
from build_cards import CARDS

OUT = sys.argv[1]
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
URLS = {
    'abiko/abby/index.html': ('abiko', 'abby', 'https://abikoagritech.com/abby'),
    'abiko/david/index.html': ('abiko', 'david', 'https://abikoagritech.com/david'),
    'colab/abby/index.html': ('colab', 'abby', 'https://colabyard.com/abby'),
}
os.makedirs(OUT, exist_ok=True)
font_b64 = base64.b64encode(open(f'{SITE}/fonts/inter-latin-400-600.woff2', 'rb').read()).decode()
eth_b64 = base64.b64encode(open(f'{SITE}/fonts/noto-ethiopic-400-600.woff2', 'rb').read()).decode()
logo_b64 = base64.b64encode(open(f'{SITE}/images/opt/logo-96.png', 'rb').read()).decode()

STYLE = {
    'abiko': dict(front_bg='#f8f5ef', ink='#0f1f1a', muted='#56625c', accent='#1f3a30', back_bg='#1f3a30', back_ink='#ffffff',
                  mark=f'<img src="data:image/png;base64,{logo_b64}" style="height:0.34in">', serif=False),
    'colab': dict(front_bg='#F6F3EC', ink='#2b211b', muted='#6b5f57', accent='#5a3a26', back_bg='#5a3a26', back_ink='#F6F3EC',
                  mark='<div style="font-family:Georgia,serif;font-size:15pt;letter-spacing:.02em;color:#5a3a26">Cōlab Yard'
                       '<div style="font-family:Inter;font-size:5.5pt;letter-spacing:.28em;text-transform:uppercase;opacity:.75">Hawassa</div></div>', serif=True),
}

def card_html(theme, data, qr_svg, url):
    s = STYLE[theme]
    pretty = lambda u: u.replace('https://', '').replace('www.', '').rstrip('/')
    rows = [r for r in [data['phone'], data['email'], pretty(data['website'])] if r]
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Inter; font-weight: 400 600; src: url(data:font/woff2;base64,{font_b64}) format('woff2'); }}
@font-face {{ font-family: 'Noto Sans Ethiopic'; font-weight: 400 600; src: url(data:font/woff2;base64,{eth_b64}) format('woff2'); unicode-range: U+1200-137F; }}
@page {{ size: 3.75in 2.25in; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: Inter, 'Noto Sans Ethiopic', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.side {{ width: 3.75in; height: 2.25in; position: relative; overflow: hidden; page-break-after: always; }}
/* safe area: 0.125in bleed + 0.125in margin inside trim */
.front {{ background: {s["front_bg"]}; color: {s["ink"]}; }}
.front .inner {{ position: absolute; inset: 0.3in 0.32in; display: flex; flex-direction: column; }}
.front .bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 0.27in; background: {s["accent"]}; }}
.inner > * {{ flex-shrink: 0; }}
.name {{ font-size: 14pt; font-weight: 600; letter-spacing: -0.01em; margin-top: auto; line-height: 1.1; }}
.am {{ font-size: 8.5pt; font-weight: 500; margin-top: 1pt; }}
.am-t {{ margin-top: 1pt; }}
.title {{ font-size: 7.5pt; color: {s["muted"]}; margin-top: 2pt; }}
.rule {{ width: 0.45in; height: 1.5pt; background: {s["accent"]}; margin: 5pt 0 4pt; }}
.rows {{ font-size: 7pt; line-height: 1.55; margin-bottom: 0.1in; }}
.back {{ background: {s["back_bg"]}; color: {s["back_ink"]}; display: flex; align-items: center; justify-content: center; gap: 0.2in; }}
.qr {{ width: 1.22in; height: 1.22in; background: #fff; border-radius: 6pt; padding: 0.11in; }}
.qr svg {{ width: 100%; height: 100%; display: block; }}
.cta {{ max-width: 1.35in; }}
.cta b {{ display: block; font-size: 10pt; font-weight: 600; line-height: 1.2; }}
.cta span {{ display: block; font-size: 6.5pt; opacity: .8; margin-top: 5pt; }}
</style></head><body>
<div class="side front"><div class="inner">
  <div>{s["mark"]}</div>
  <div class="name">{data["name"]}</div>
  {f'<div class="am">{data["name_am"]}</div>' if data.get("name_am") else ''}
  <div class="title">{data["title"]}</div>
  {f'<div class="title am-t">{data["title_am"]}</div>' if data.get("title_am") else ''}
  <div class="rule"></div>
  <div class="rows">{"<br>".join(rows)}</div>
</div><div class="bar"></div></div>
<div class="side back">
  <div class="qr">{qr_svg}</div>
  <div class="cta"><b>Scan to save my contact</b><span>{pretty(url)}</span></div>
</div>
</body></html>'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for key, (theme, slug, url) in URLS.items():
            data = CARDS[key][1]
            base = f'{OUT}/{theme}-{slug}'
            qr = segno.make(url, error='m')
            qr.save(f'{base}-qr.svg', scale=10, border=4)
            qr.save(f'{base}-qr.png', scale=20, border=4)
            svg_inline = qr.svg_inline(border=0, dark='#000000', omitsize=True)
            html = card_html(theme, data, svg_inline, url)
            open(f'{base}-print.html', 'w').write(html)
            pg = await b.new_page()
            await pg.set_content(html, wait_until='networkidle')
            await pg.pdf(path=f'{base}-print.pdf', width='3.75in', height='2.25in', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
            # preview image of both sides with trim line
            await pg.set_viewport_size({'width': 720, 'height': 432 * 2})
            await pg.add_style_tag(content='.side{transform-origin:0 0} body{zoom:2}')
            await pg.screenshot(path=f'{base}-preview.png', full_page=True)
            print('built', base)
        await b.close()

asyncio.run(main())
