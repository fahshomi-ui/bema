#!/usr/bin/env python3
"""
Fix font to match original site exactly:
- Font: Tajawal Regular (loaded from Google Fonts CDN)
- Body: 16px
- Nav: Tajawal Regular, ~16px, font-weight 400
- Dropdown items: Tajawal Regular, ~14-15px

Also need to add Google Fonts link for Tajawal
"""
import glob

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

# Google Fonts link for Tajawal
tajawal_link = '<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">'

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add Tajawal Google Font if not already there
    if 'Tajawal' not in content.split('googleapis')[0] if 'googleapis' in content else True:
        if 'fonts.googleapis.com/css2?family=Tajawal' not in content:
            # Add before first <link or after <head>
            if '<head>' in content:
                content = content.replace('<head>', '<head>\n' + tajawal_link)
            elif '</title>' in content:
                content = content.replace('</title>', '</title>\n' + tajawal_link)
    
    # Update the nav font CSS to use Tajawal Regular exactly like original
    content = content.replace(
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
}""",
        """/* Nav items - match original font (Tajawal Regular) */
body, * {
  font-family: 'Tajawal', sans-serif !important;
}
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 400 !important;
  font-size: 16px !important;
  font-family: 'Tajawal', sans-serif !important;
  color: #333 !important;
}
.nav-submenu li a {
  font-weight: 400 !important;
  font-size: 15px !important;
  font-family: 'Tajawal', sans-serif !important;
  color: #333 !important;
  padding: 12px 20px !important;
  display: block !important;
}
.nav-submenu li a:hover {
  color: #6ab04c !important;
}"""
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ Font matched with original (Tajawal Regular)!")
