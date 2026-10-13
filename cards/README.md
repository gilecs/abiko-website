# Digital business cards

Live cards (not indexed by search engines):
- https://abikoagritech.com/abby
- https://abikoagritech.com/david

## Update a card (no tools needed)
Open `abby/index.html` or `david/index.html` on GitHub, click the pencil, and edit the values
in the block marked **EDIT THIS CARD HERE** near the top of the body. Leave a value empty ("")
to hide it. Commit, and Netlify publishes it in about a minute. The QR code never changes.

Photos: add a square photo (about 400x400, under 60 KB) to `images/cards/`, then set
"photo": "/images/cards/abby.jpg".

## Rebuild everything (pages, QR codes, print PDFs)
Edit the details in `build_cards.py`, then:
    python3 build_cards.py out && python3 build_print.py print

## Print files
`print/*-print.pdf`: 2 pages (front, back), 3.75 x 2.25 in = 3.5 x 2 in card + 0.125 in bleed.
Tell the printer: "full bleed, trim to 3.5 x 2 in". Re-export after the real details are filled in.
