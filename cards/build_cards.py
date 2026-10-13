"""Builds the digital business card pages from card-template.html.
Each page keeps its details in an editable JSON block near the top of the <body>."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, 'card-template.html')).read()

THEMES = {
    'abiko': {
        'vars': '--bg: #f8f5ef; --ink: #0f1f1a; --muted: rgba(15, 31, 26, 0.62); --accent: #1f3a30; --on-accent: #ffffff; '
                '--soft: #e4efe6; --line: rgba(15, 31, 26, 0.12); --logo-bg: #ffffff; --logo-pad: 6px 12px; '
                "--font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; --wordmark-font: var(--font);",
        'theme_color': '#1f3a30',
        'font_face': "@font-face { font-family: 'Inter'; font-weight: 400 600; font-display: swap; src: url('/fonts/inter-latin-400-600.woff2') format('woff2'); }",
        'head': '<link rel="preload" href="/fonts/inter-latin-400-600.woff2" as="font" type="font/woff2" crossorigin>\n    <link rel="icon" href="/favicon.ico" sizes="any">\n    <link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        'mark': '<picture><source type="image/webp" srcset="/images/opt/logo-96.webp"><img class="brand-logo" src="/images/opt/logo-96.png" width="125" height="48" alt="Abiko Agritech"></picture>',
    },
    'colab': {
        'vars': '--bg: #F6F3EC; --ink: #2b211b; --muted: rgba(43, 33, 27, 0.62); --accent: #5a3a26; --on-accent: #F6F3EC; '
                '--soft: #ebe2d4; --line: rgba(43, 33, 27, 0.12); '
                "--font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; --wordmark-font: Georgia, 'Times New Roman', serif;",
        'theme_color': '#5a3a26',
        'font_face': '',
        'head': '',
        'mark': '<div class="wordmark" aria-label="Cōlab Yard, Hawassa">Cōlab Yard<small>Hawassa</small></div>',
    },
}

CARDS = {
    # path (relative to output root) : (theme, data)
    'abiko/abby/index.html': ('abiko', {
        "name": "Abby",
        "title": "Title goes here",
        "company": "Abiko Agritech",
        "phone": "+251 900 000 000",
        "whatsapp": True,
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
        "name": "David",
        "title": "Title goes here",
        "company": "Abiko Agritech",
        "phone": "+251 900 000 000",
        "whatsapp": True,
        "email": "name@abikoagritech.com",
        "website": "https://abikoagritech.com",
        "linkedin": "",
        "instagram": "",
        "facebook": "https://www.facebook.com/abikoagritech",
        "tiktok": "https://www.tiktok.com/@abikoagritech",
        "location": "Hawassa, Ethiopia",
        "photo": ""
    }),
    'colab/abby/index.html': ('colab', {
        "name": "Abby",
        "title": "Title goes here",
        "company": "Cōlab Yard",
        "phone": "+251 900 000 000",
        "whatsapp": True,
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

def build(out_root):
    for path, (theme, data) in CARDS.items():
      t = THEMES[theme]
      html = (tpl.replace('__THEME_VARS__', t['vars']).replace('__THEME_COLOR__', t['theme_color'])
                 .replace('__FONT_FACE__', t['font_face']).replace('__HEAD_EXTRA__', t['head'])
                 .replace('__BRAND_MARK__', t['mark']).replace('__TITLE__', f"{data['name']} | {data['company']}")
                 .replace('__CARD_JSON__', json.dumps(data, indent=8, ensure_ascii=False)))
      assert '__' not in html.replace('__agentproxy', ''), 'unreplaced placeholder'
      dest = os.path.join(out_root, path); os.makedirs(os.path.dirname(dest), exist_ok=True)
      open(dest, 'w').write(html); print('wrote', dest, len(html)//1024, 'KB')


if __name__ == '__main__':
    build(sys.argv[1])
