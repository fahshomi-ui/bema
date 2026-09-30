#!/usr/bin/env python3
"""
Fix all remaining issues on beimmai.com form pages:
1. Nav dropdown arrow: □ → proper chevron (˅) using Font Awesome
2. Translate nav dropdown English items to Arabic
3. Fix date of birth field: remove duplicate icon, hide mm/dd/yyyy
4. Add popup "من تريد التأمين عليه؟" on "احصل على العروض" button click
5. Fix "تأمين" in home-form nav link to "تأمين المنزل"
"""

import os
import glob

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(os.path.join(FORM_DIR, "*.html"))

print(f"Found {len(FORM_FILES)} form files:")
for f in FORM_FILES:
    print(f"  {f}")

# The translations for nav dropdown items
NAV_TRANSLATIONS = {
    "> Domestic Worker </a>": "> تأمين العمالة المنزلية </a>",
    "> Credit Life </a>": "> تأمين حياة القرض </a>",
    "> Medical Malpractice Ins. </a>": "> تأمين الأخطاء الطبية </a>",
    'href="/insurance/home-form"> تأمين </a>': 'href="/insurance/home-form"> تأمين المنزل </a>',
}

# CSS to fix the date field and add dropdown arrow
CUSTOM_CSS = """
<style>
/* Fix dropdown arrow - add chevron after تأمين nav link */
.dropdown.has-sub-menu > a.menu-title::after {
  content: '';
  display: inline-block;
  width: 0;
  height: 0;
  margin-right: 6px;
  vertical-align: middle;
  border-top: 5px solid;
  border-right: 5px solid transparent;
  border-left: 5px solid transparent;
}

/* Fix date input - hide browser default date picker icon */
input[type="date"]::-webkit-calendar-picker-indicator {
  display: none !important;
  -webkit-appearance: none !important;
}
input[type="date"]::-webkit-inner-spin-button {
  display: none !important;
}
input[type="date"]::-webkit-date-and-time-value {
  text-align: right;
}
input[type="date"] {
  -webkit-appearance: none !important;
  -moz-appearance: textfield !important;
}

/* Style the date field to look like the original */
.bootstrap-date-input-wrap .form-control[type="date"] {
  color: transparent;
}
.bootstrap-date-input-wrap .form-control[type="date"]:focus,
.bootstrap-date-input-wrap .form-control[type="date"]:valid {
  color: #212529;
}
.bootstrap-date-input-wrap .form-control[type="date"][value]:not([value=""]) {
  color: #212529;
}

/* Ensure the calendar trigger button is on the left (RTL) */
[dir=rtl] .bootstrap-date-input-trigger {
  right: auto !important;
  left: 10px !important;
}

/* Insurance popup modal */
.insurance-popup-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
  justify-content: center;
  align-items: center;
}
.insurance-popup-overlay.active {
  display: flex;
}
.insurance-popup {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  max-width: 550px;
  width: 90%;
  position: relative;
  text-align: center;
}
.insurance-popup .close-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.insurance-popup h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  font-weight: 600;
}
.insurance-popup p {
  color: #666;
  margin-bottom: 25px;
}
.insurance-popup .option-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 18px;
  margin-bottom: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.insurance-popup .option-btn:hover {
  border-color: #4caf50;
  box-shadow: 0 2px 8px rgba(76,175,80,0.1);
}
.insurance-popup .option-btn i {
  font-size: 1.3rem;
  color: #555;
}
</style>
"""

# The popup HTML
POPUP_HTML = """
<!-- Insurance Selection Popup -->
<div class="insurance-popup-overlay" id="insurancePopup">
  <div class="insurance-popup">
    <button class="close-btn" onclick="document.getElementById('insurancePopup').classList.remove('active')">X</button>
    <h3>من تريد التأمين عليه؟</h3>
    <p>اختر ما إذا كنت تريد التغطية لنفسك فقط أو تضمين أفراد عائلتك.</p>
    <button class="option-btn" onclick="document.getElementById('insurancePopup').classList.remove('active')">
      <i class="fa-solid fa-user"></i>
      أنا المؤمن عليه فقط
    </button>
    <button class="option-btn" onclick="document.getElementById('insurancePopup').classList.remove('active')">
      <i class="fa-solid fa-users"></i>
      إضافة أفراد الأسرة للتأمين
    </button>
  </div>
</div>
"""

# JavaScript to show popup on button click
POPUP_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Find the "احصل على العروض" button and attach popup
  var btns = document.querySelectorAll('button, .btn');
  btns.forEach(function(btn) {
    if (btn.textContent.trim().includes('احصل على العروض')) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('insurancePopup').classList.add('active');
      });
    }
  });
});
</script>
"""

def fix_file(filepath):
    print(f"\nProcessing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Fix nav dropdown translations
    for eng, ar in NAV_TRANSLATIONS.items():
        if eng in content:
            content = content.replace(eng, ar)
            print(f"  ✓ Translated: {eng.strip()[:40]}...")
    
    # 2. Fix the dropdown arrow - the original uses a chevron-down SVG or icon
    # The issue is that the CSS ::after pseudo-element needs Font Awesome or a proper character
    # Let's add a proper chevron icon after "تأمين" in the nav
    # Replace the plain text "تأمين </a>" in the has-sub-menu with one that includes an icon
    old_nav_link = 'class="nav-link menu-title"><!----><!----><!----> تأمين </a>'
    new_nav_link = 'class="nav-link menu-title"><!----><!----><!----> تأمين <i class="fa-solid fa-chevron-down" style="font-size:10px;margin-right:5px;"></i></a>'
    if old_nav_link in content:
        content = content.replace(old_nav_link, new_nav_link)
        print("  ✓ Added chevron-down icon to تأمين dropdown")
    
    # 3. Fix date field - change type="date" to type="text" to remove browser default
    # and keep the custom calendar button
    old_date_input = 'type="date" placeholder=" "'
    new_date_input = 'type="text" placeholder=" " readonly'
    if old_date_input in content:
        content = content.replace(old_date_input, new_date_input)
        print("  ✓ Changed date input to text type (removes mm/dd/yyyy)")
    
    # 4. Add custom CSS before </head>
    if CUSTOM_CSS.strip() not in content:
        content = content.replace('</head>', CUSTOM_CSS + '\n</head>')
        print("  ✓ Added custom CSS")
    
    # 5. Add popup HTML before </body> (only for medical-form which has the button)
    if 'medical-form' in filepath or 'domestic-form' in filepath or 'credit-life' in filepath or 'home-form' in filepath or 'malpractice' in filepath:
        if 'insurancePopup' not in content:
            content = content.replace('</body>', POPUP_HTML + POPUP_JS + '\n</body>')
            print("  ✓ Added insurance popup")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ File saved!")
    else:
        print(f"  - No changes needed")

# Also fix the homepage
HOMEPAGE = "client/public/bima-home.html"

for filepath in FORM_FILES:
    fix_file(filepath)

if os.path.exists(HOMEPAGE):
    fix_file(HOMEPAGE)

print("\n✅ All fixes applied!")
