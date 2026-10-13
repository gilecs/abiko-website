# Digital business cards

Live cards (not indexed by search engines):
- https://abikoagritech.com/abby
- https://abikoagritech.com/david

## Update a card
Details live in `build_cards.py`. Edit them there and rebuild (below): this updates the page
and the contact file that "Save contact" downloads (e.g. `david/dawit-makonnen.vcf`).
For a quick text fix you can also edit the **EDIT THIS CARD HERE** block in the page itself on
GitHub, but the .vcf file must be rebuilt to match. The QR code never changes.

Photos: put a square `photo.jpg` (about 400x400, under 60 KB) in the card's output folder and set
"photo": "photo.jpg"; the rebuild also embeds it in the contact file.

## Rebuild everything (pages, QR codes, print PDFs)
Edit the details in `build_cards.py`, then:
    python3 build_cards.py out && python3 build_print.py print && python3 build_phone_qr.py print

## Print files
`print/*-print.pdf`: 2 pages (front, back), 3.75 x 2.25 in = 3.5 x 2 in card + 0.125 in bleed.
Tell the printer: "full bleed, trim to 3.5 x 2 in". Re-export after the real details are filled in.
