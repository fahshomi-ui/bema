#!/usr/bin/env python3
"""
Fix nav:
1. Make nav items bold
2. Move arrow to LEFT of تأمين visually
   In RTL, LEFT side visually = the arrow needs to come BEFORE the text in HTML
   Current: تأمين <span>▾</span>  (arrow appears on left in RTL - wait no)
   
   Actually in RTL:
   - HTML order: text first, then span
   - Visual: span appears on LEFT, text on RIGHT
   - So current should already show arrow on left...
   
   But from the screenshot, the arrow ˅ is between "تأمين" and the small ▾
   There are TWO arrows showing! One is our ▾ span and one is the CSS ::after
   
   Looking at screenshot more carefully:
   - "تأمين" then "˅" then "▾" 
   - The ˅ is from somewhere else, the ▾ is our span
   
   Actually the user is saying: put the arrow on the LEFT side of the word تأمين
   In the original (app.bima.om): "تأمين  ˅" with arrow on LEFT
   
   In RTL display:
   - What's written FIRST in HTML appears on the RIGHT
   - What's written LAST in HTML appears on the LEFT
   
   So to show: [arrow] [تأمين] visually (arrow on left)
   In HTML RTL we need: تأمين [arrow] (arrow after text = appears on left in RTL)
   
   That's what we already have! The issue might be that there's STILL a second character.
   Let me just make sure there's only ONE arrow and it's positioned correctly.
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Make nav links bold
    # Add CSS for nav menu items to be bold
    bold_css = """
/* Make nav items bold */
.nav-menu > li > a.menu-title,
.nav-menu > li > a.nav-link {
  font-weight: 700 !important;
  font-size: 1rem !important;
}
"""
    # Insert before the "Kill the square" comment
    content = content.replace('/* Kill the square', bold_css + '/* Kill the square')
    
    # FIX 2: The arrow - in RTL, to appear on LEFT of text, it should be AFTER text in HTML
    # Current: تأمين <span style="...margin-left:6px...">▾</span>
    # This should already appear on the left in RTL. But let's make sure the span is correct.
    # The issue from screenshot: there seem to be TWO characters (˅ and ▾)
    # One is our span, the other might be from ::after CSS that's not fully hidden
    
    # Let's replace with a cleaner approach - use a proper SVG chevron inline
    content = content.replace(
        '<!----> تأمين <span style="font-size:12px;margin-left:6px;display:inline-block;vertical-align:middle;">&#x25BE;</span>',
        '<!----> تأمين <svg style="width:12px;height:12px;margin-right:2px;vertical-align:middle;display:inline-block;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>'
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ Nav bold + arrow fixed!")
