#!/usr/bin/env python3
"""
Match nav exactly with original:
- Original nav items: "الصفحة الرئيسية" (not just "الرئيسية"), "تأمين ˅", "تتبع الطلب"
- Font: normal weight (not bold) - same as original
- Arrow: small ▾ on left of تأمين
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Change "الرئيسية" to "الصفحة الرئيسية" in nav
    content = content.replace(
        'href="/"><!----> الرئيسية </a>',
        'href="/"><!----> الصفحة الرئيسية </a>'
    )
    
    # FIX 2: Remove the bold CSS we added earlier - make it normal weight like original
    content = content.replace(
        """
/* Make nav items bold */
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 700 !important;
  font-size: 1rem !important;
}
""",
        """
/* Nav items - match original font */
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 400 !important;
  font-size: 1rem !important;
}
"""
    )
    
    # FIX 3: Arrow - replace SVG with simple text arrow ˅ matching original exactly
    # Original uses a simple small chevron character
    content = re.sub(
        r'<!----> تأمين <svg[^>]*>.*?</svg>',
        '<!----> تأمين <span style="font-size:10px;margin-right:4px;">&#x25BE;</span>',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ Nav text and font matched with original!")
