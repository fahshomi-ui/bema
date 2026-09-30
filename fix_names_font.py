#!/usr/bin/env python3
"""
Fix dropdown menu item names to match original exactly:
- تأمين للركبات → التأمين على المركبات
- تأمين السفر → تأمين السفر (same)
- تأمين العمالة المنزلية → العمالة المنزلية
- التأمين الصحي → التأمين الصحي (same)
- تأمين حياة القرض → تأمين القروض
- تأمين المنزل → تأمين المنازل
- تأمين الأخطاء الطبية → تأمين الاخطاء الطبية

Also fix the font to match original (thinner, lighter)
"""
import glob

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

# Name replacements - exact text in HTML
name_fixes = [
    (" تأمين للركبات ", " التأمين على المركبات "),
    (" تأمين العمالة المنزلية ", " العمالة المنزلية "),
    (" تأمين حياة القرض ", " تأمين القروض "),
    (" تأمين المنزل ", " تأمين المنازل "),
    (" تأمين الأخطاء الطبية ", " تأمين الاخطاء الطبية "),
]

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix names
    for old, new in name_fixes:
        content = content.replace(old, new)
    
    # Fix font for the nav section - make it match original (lighter weight)
    # The original uses a clean sans-serif font, normal weight
    # Replace our bold CSS with proper font matching
    content = content.replace(
        """/* Nav items - match original font */
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 400 !important;
  font-size: 1rem !important;
}""",
        """/* Nav items - match original font */
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 500 !important;
  font-size: 15px !important;
  font-family: 'Tajawal', 'Segoe UI', sans-serif !important;
}
.nav-submenu li a {
  font-weight: 400 !important;
  font-size: 14px !important;
  font-family: 'Tajawal', 'Segoe UI', sans-serif !important;
  color: #333 !important;
  padding: 10px 20px !important;
}
.nav-submenu li a:hover {
  color: #6ab04c !important;
}"""
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ Names and font fixed!")
