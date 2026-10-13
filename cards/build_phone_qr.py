"""Phone-screen QR images (1170x2532, iPhone/Android friendly) for showing at meetings."""
import asyncio, base64, os, sys
import segno
from playwright.async_api import async_playwright
from build_cards import CARDS
OUT=sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SITE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
font=base64.b64encode(open(f'{SITE}/fonts/inter-latin-400-600.woff2','rb').read()).decode()
eth_b64=base64.b64encode(open(f'{SITE}/fonts/noto-ethiopic-400-600.woff2','rb').read()).decode()
logo=base64.b64encode(open(f'{SITE}/images/opt/logo-96.png','rb').read()).decode()
ITEMS=[('abiko','abby','abiko/abby/index.html','https://abikoagritech.com/abby'),
       ('abiko','david','abiko/david/index.html','https://abikoagritech.com/david'),
       ('colab','abby','colab/abby/index.html','https://colabyard.com/abby')]
TH={'abiko':dict(bg='#1f3a30',fg='#ffffff',sub='#d7f0df',mark=f'<div style="background:#fff;border-radius:28px;padding:22px 34px;display:inline-block"><img src="data:image/png;base64,{logo}" style="height:110px;display:block"></div>'),
    'colab':dict(bg='#5a3a26',fg='#F6F3EC',sub='#ebe2d4',mark='<div style="font-family:Georgia,serif;font-size:96px;letter-spacing:.02em">Cōlab Yard<div style="font-family:Inter;font-size:30px;letter-spacing:.3em;opacity:.8;margin-top:6px">HAWASSA</div></div>')}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1170,'height':2532})
        for theme,slug,key,url in ITEMS:
            d=CARDS[key][1]; t=TH[theme]
            qr=segno.make(url,error='m').svg_inline(border=0,omitsize=True)
            html=f'''<html><head><meta charset="utf-8"><style>
@font-face{{font-family:Inter;font-weight:400 600;src:url(data:font/woff2;base64,{font}) format('woff2')}}
@font-face{{font-family:'Noto Sans Ethiopic';font-weight:400 600;src:url(data:font/woff2;base64,{eth_b64}) format('woff2');unicode-range:U+1200-137F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1170px;height:2532px;background:{t["bg"]};color:{t["fg"]};font-family:Inter,'Noto Sans Ethiopic',sans-serif;text-align:center;
 display:flex;flex-direction:column;align-items:center;padding:330px 110px 0}}
.qr{{margin-top:120px;width:860px;height:860px;background:#fff;border-radius:56px;padding:70px}}
.qr svg{{width:100%;height:100%;display:block}}
h1{{font-size:96px;font-weight:600;margin-top:110px;letter-spacing:-.01em}}
.am{{font-size:54px;font-weight:500;margin-top:10px}}
.role{{font-size:44px;color:{t["sub"]};margin-top:14px}}
.cta{{font-size:46px;margin-top:80px;font-weight:600}}
.url{{font-size:38px;color:{t["sub"]};margin-top:12px}}
</style></head><body>{t["mark"]}<div class="qr">{qr}</div>
<h1>{d["name"]}</h1>{f'<div class="am">{d["name_am"]}</div>' if d.get("name_am") else ""}<div class="role">{" · ".join(x for x in [d["title"],d["company"]] if x)}</div>{f'<div class="role">{d["title_am"]}</div>' if d.get("title_am") else ""}
<div class="cta">Scan to save my contact</div><div class="url">{url.replace("https://","")}</div></body></html>'''
            await pg.set_content(html,wait_until='networkidle')
            f=f'{OUT}/{theme}-{slug}-phone-qr.png'; await pg.screenshot(path=f); print(f)
        await b.close()
asyncio.run(main())
