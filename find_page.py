import sys
import logging
from pypdf import PdfReader

import config

logging.getLogger("pypdf").setLevel(logging.ERROR)   # hide the 'wrong pointing object' noise

term = " ".join(sys.argv[1:]).lower()
for pdf in config.POLICY_DIR.glob("*.pdf"):
    for page_number, page in enumerate(PdfReader(pdf).pages, start=1):
        text = " ".join((page.extract_text() or "").split())
        idx = text.lower().find(term)
        if idx >= 0:
            print(f"\npage {page_number}: ...{text[max(0, idx - 120):idx + 180]}...")
