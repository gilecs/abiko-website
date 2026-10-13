"""Builds the digital business card pages from card-template.html.
Each page keeps its details in an editable JSON block near the top of the <body>."""
import base64, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, 'card-template.html')).read()

THEMES = {
    'abiko': {
        'vars': '--bg: #f8f5ef; --ink: #0f1f1a; --muted: rgba(15, 31, 26, 0.62); --accent: #1f3a30; --on-accent: #ffffff; '
                '--soft: #e4efe6; --line: rgba(15, 31, 26, 0.12); --logo-bg: #ffffff; --logo-pad: 6px 12px; '
                "--font: 'Inter', 'Noto Sans Ethiopic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; --wordmark-font: var(--font);",
        'theme_color': '#1f3a30',
        'font_face': "@font-face { font-family: 'Inter'; font-weight: 400 600; font-display: swap; src: url('/fonts/inter-latin-400-600.woff2') format('woff2'); } @font-face { font-family: 'Noto Sans Ethiopic'; font-weight: 400 600; font-display: swap; src: url('/fonts/noto-ethiopic-400-600.woff2') format('woff2'); unicode-range: U+1200-137F; }",
        'head': '<link rel="preload" href="/fonts/inter-latin-400-600.woff2" as="font" type="font/woff2" crossorigin>\n    <link rel="icon" href="/favicon.ico" sizes="any">\n    <link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        'mark': '<picture><source type="image/webp" srcset="/images/opt/logo-96.webp"><img class="brand-logo" src="/images/opt/logo-96.png" width="125" height="48" alt="Abiko Agritech"></picture>',
    },
    'colab': {
        'vars': '--bg: #F6F3EC; --ink: #2b211b; --muted: rgba(43, 33, 27, 0.62); --accent: #5a3a26; --on-accent: #F6F3EC; '
                '--soft: #ebe2d4; --line: rgba(43, 33, 27, 0.12); '
                "--font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans Ethiopic', sans-serif; --wordmark-font: Georgia, 'Times New Roman', serif;",
        'theme_color': '#5a3a26',
        'font_face': "@font-face { font-family: 'Noto Sans Ethiopic'; font-weight: 400 600; font-display: swap; src: url('/abby/noto-ethiopic-400-600.woff2') format('woff2'); unicode-range: U+1200-137F; }",
        'head': '',
        'mark': '<div class="wordmark" aria-label="Cōlab Yard, Hawassa">Cōlab Yard<small>Hawassa</small></div>',
    },
}

CARDS = {
    # path (relative to output root) : (theme, data)
    'abiko/abby/index.html': ('abiko', {
        "name": "Abby",
        "name_am": "",
        "title": "Title goes here",
        "title_am": "",
        "company": "Abiko Agritech",
        "phone": "+251 900 000 000",
        "whatsapp": True,
        "telegram": "",
        "email": "name@abikoagritech.com",
        "website": "https://abikoagritech.com",
        "linkedin": "https://www.linkedin.com/in/your-profile",
        "instagram": "",
        "facebook": "https://www.facebook.com/abikoagritech",
        "tiktok": "https://www.tiktok.com/@abikoagritech",
        "location": "Hawassa, Ethiopia",
        "photo": ""
    }),
    'abiko/david/index.html': ('abiko', {
        "name": "Dawit Makonnen",
        "name_am": "ዳዊት መኮንን",
        "title": "Founder & Managing Director",
        "title_am": "መሥራች እና ዋና ሥራ አስኪያጅ",
        "company": "Abiko Agritech",
        "phone": "+251 944 297 033",
        "whatsapp": True,
        "telegram": "@dmakonnen",
        "email": "dmakonn1@gmail.com",
        "website": "https://www.abikoagritech.com",
        "linkedin": "",
        "instagram": "",
        "facebook": "https://www.facebook.com/abikoagritech",
        "tiktok": "https://www.tiktok.com/@abikoagritech",
        "location": "Hawassa, Ethiopia",
        "photo": ""
    }),
    'colab/abby/index.html': ('colab', {
        "name": "Abby",
        "name_am": "",
        "title": "Title goes here",
        "title_am": "",
        "company": "Cōlab Yard",
        "phone": "+251 900 000 000",
        "whatsapp": True,
        "telegram": "",
        "email": "contact@colabyard.com",
        "website": "https://colabyard.com",
        "linkedin": "https://www.linkedin.com/in/your-profile",
        "instagram": "https://www.instagram.com/colab.yard/",
        "facebook": "https://www.facebook.com/colab.yard",
        "tiktok": "https://www.tiktok.com/@colab.yard",
        "location": "Hawassa, Ethiopia",
        "photo": ""
    }),
}

def _esc(v):
    return str(v).replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')

def _fold(line):
    # RFC 6350: lines over 75 octets are folded with CRLF + space (never splitting a UTF-8 character)
    out, cur = [], b''
    for ch in line:
        enc = ch.encode('utf-8')
        if len(cur) + len(enc) > (75 if not out else 74):
            out.append(cur); cur = b''
        cur += enc
    out.append(cur)
    return '\r\n '.join(x.decode('utf-8') for x in out)

def vcard(d, card_url, photo_path=None):
    parts = d['name'].split()
    last = parts[-1] if len(parts) > 1 else ''
    first = ' '.join(parts[:-1]) if len(parts) > 1 else d['name']
    phone = re.sub(r'[^\d+]', '', d.get('phone', ''))
    loc = [x.strip() for x in d.get('location', '').split(',') if x.strip()]
    country = loc.pop() if len(loc) > 1 else ''
    city = loc.pop() if loc else ''
    L = ['BEGIN:VCARD', 'VERSION:3.0',
         f'N:{_esc(last)};{_esc(first)};;;', f'FN:{_esc(d["name"])}']
    if d.get('name_am'): L.append(f'NICKNAME:{_esc(d["name_am"])}')
    if d.get('company'): L.append(f'ORG:{_esc(d["company"])}')
    if d.get('title'): L.append(f'TITLE:{_esc(d["title"])}')
    if phone: L.append(f'TEL;TYPE=CELL,VOICE:{phone}')
    if d.get('email'): L.append(f'EMAIL;TYPE=INTERNET,WORK:{d["email"]}')
    if d.get('website'): L.append(f'URL:{d["website"]}')
    if d.get('location'): L.append(f'ADR;TYPE=WORK:;;{_esc(", ".join(loc))};{_esc(city)};;;{_esc(country)}')
    for key, label in (('linkedin', 'linkedin'), ('facebook', 'facebook'), ('tiktok', 'tiktok'), ('instagram', 'instagram')):
        if d.get(key): L.append(f'X-SOCIALPROFILE;TYPE={label}:{d[key]}')
    if d.get('telegram'): L.append(f'X-SOCIALPROFILE;TYPE=telegram:https://t.me/{d["telegram"].lstrip("@")}')
    note = f'{d.get("company", "")}. Digital card: {card_url}'
    if d.get('title_am'): note = f'{d["title_am"]}. ' + note
    L.append(f'NOTE:{_esc(note)}')
    if photo_path and os.path.exists(photo_path):
        L.append('PHOTO;ENCODING=b;TYPE=JPEG:' + base64.b64encode(open(photo_path, 'rb').read()).decode())
    L.append('END:VCARD')
    return '\r\n'.join(_fold(l) for l in L) + '\r\n'

def vcf_name(d):
    slug = unicodedata.normalize('NFKD', d['name']).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', slug).strip('-') + '.vcf'

CARD_URLS = {
    'abiko/abby/index.html': 'https://abikoagritech.com/abby',
    'abiko/david/index.html': 'https://abikoagritech.com/david',
    'colab/abby/index.html': 'https://colabyard.com/abby',
}

def build(out_root):
    for path, (theme, data) in CARDS.items():
      t = THEMES[theme]
      html = (tpl.replace('__THEME_VARS__', t['vars']).replace('__THEME_COLOR__', t['theme_color'])
                 .replace('__FONT_FACE__', t['font_face']).replace('__HEAD_EXTRA__', t['head'])
                 .replace('__BRAND_MARK__', t['mark']).replace('__TITLE__', f"{data['name']} | {data['company']}")
                 .replace('__CARD_JSON__', json.dumps(data, indent=8, ensure_ascii=False))
                 .replace('__VCF_FILE__', vcf_name(data)))
      assert '__' not in html.replace('__agentproxy', ''), 'unreplaced placeholder'
      dest = os.path.join(out_root, path); os.makedirs(os.path.dirname(dest), exist_ok=True)
      open(dest, 'w').write(html); print('wrote', dest, len(html)//1024, 'KB')
      vdest = os.path.join(os.path.dirname(dest), vcf_name(data))
      photo = os.path.join(os.path.dirname(dest), 'photo.jpg')
      open(vdest, 'w', newline='').write(vcard(data, CARD_URLS[path], photo)); print('wrote', vdest)


if __name__ == '__main__':
    build(sys.argv[1])
