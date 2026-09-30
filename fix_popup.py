#!/usr/bin/env python3
"""
Update the insurance popup in all form pages to match the original app.bima.om exactly:
- "أنا المؤمن عليه فقط" → goes to offers page
- "إضافة أفراد الأسرة للتأمين" → shows family count selector (1-9 + أخرى)
- "متابعة" button → goes to offers page with family count
"""

import glob
import os

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(os.path.join(FORM_DIR, "*-form.html"))

# The new popup HTML that matches the original exactly
NEW_POPUP_HTML = '''
<!-- Insurance Selection Popup -->
<div class="insurance-popup-overlay" id="insurancePopup">
  <div class="insurance-popup">
    <button class="close-btn" onclick="document.getElementById('insurancePopup').classList.remove('active')">X</button>
    <h3>من تريد التأمين عليه؟</h3>
    <p>اختر ما إذا كنت تريد التغطية لنفسك فقط أو تضمين أفراد عائلتك.</p>
    
    <!-- Option 1: Self only -->
    <button class="option-btn" id="selfOnlyBtn" onclick="handleSelfOnly()">
      <i class="fa-solid fa-user"></i>
      أنا المؤمن عليه فقط
    </button>
    
    <!-- Option 2: Add family members -->
    <button class="option-btn" id="addFamilyBtn" onclick="handleAddFamily()">
      <i class="fa-solid fa-users"></i>
      إضافة أفراد الأسرة للتأمين
    </button>
    
    <!-- Family count section (hidden initially) -->
    <div id="familyCountSection" style="display:none; margin-top: 20px;">
      <p style="font-weight: 600; font-size: 1rem; margin-bottom: 15px;">كم عدد أفراد العائلة الذين تريد إضافتهم؟</p>
      <div class="family-count-grid">
        <button class="count-btn" onclick="selectCount(1)">1</button>
        <button class="count-btn" onclick="selectCount(2)">2</button>
        <button class="count-btn" onclick="selectCount(3)">3</button>
        <button class="count-btn" onclick="selectCount(4)">4</button>
        <button class="count-btn active" onclick="selectCount(5)">5</button>
        <button class="count-btn" onclick="selectCount(6)">6</button>
        <button class="count-btn" onclick="selectCount(7)">7</button>
        <button class="count-btn" onclick="selectCount(8)">8</button>
        <button class="count-btn" onclick="selectCount(9)">9</button>
        <button class="count-btn" onclick="selectCount('other')">أخرى</button>
      </div>
      <button class="continue-btn" onclick="handleContinue()">متابعة</button>
    </div>
  </div>
</div>
'''

# The new popup JS
NEW_POPUP_JS = '''
<script>
var selectedFamilyCount = 5;

function handleSelfOnly() {
  document.getElementById('insurancePopup').classList.remove('active');
  // Navigate to offers page
  var currentPage = window.location.pathname;
  var offersPage = currentPage.replace('-form', '-offers');
  window.location.href = offersPage;
}

function handleAddFamily() {
  document.getElementById('familyCountSection').style.display = 'block';
  document.getElementById('addFamilyBtn').style.borderColor = '#4caf50';
  document.getElementById('addFamilyBtn').style.boxShadow = '0 0 0 2px rgba(76,175,80,0.2)';
}

function selectCount(num) {
  selectedFamilyCount = num;
  var btns = document.querySelectorAll('.count-btn');
  btns.forEach(function(b) { b.classList.remove('active'); });
  event.target.classList.add('active');
}

function handleContinue() {
  document.getElementById('insurancePopup').classList.remove('active');
  var currentPage = window.location.pathname;
  var offersPage = currentPage.replace('-form', '-offers');
  window.location.href = offersPage + '?family=' + selectedFamilyCount;
}

document.addEventListener('DOMContentLoaded', function() {
  var btns = document.querySelectorAll('button, .btn, a');
  btns.forEach(function(btn) {
    if (btn.textContent.trim().includes('احصل على العروض')) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('insurancePopup').classList.add('active');
        // Reset state
        document.getElementById('familyCountSection').style.display = 'none';
        document.getElementById('addFamilyBtn').style.borderColor = '';
        document.getElementById('addFamilyBtn').style.boxShadow = '';
      });
    }
  });
});
</script>
'''

# Updated CSS for the popup (including family count grid)
NEW_POPUP_CSS = '''
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
  border-radius: 16px;
  padding: 40px 35px;
  max-width: 600px;
  width: 90%;
  position: relative;
  text-align: center;
  max-height: 90vh;
  overflow-y: auto;
}
.insurance-popup .close-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}
.insurance-popup .close-btn:hover {
  background: #f5f5f5;
}
.insurance-popup h3 {
  font-size: 1.6rem;
  margin-bottom: 10px;
  font-weight: 700;
  color: #222;
}
.insurance-popup > p {
  color: #666;
  margin-bottom: 25px;
  font-size: 0.95rem;
}
.insurance-popup .option-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 20px;
  margin-bottom: 15px;
  border: 1.5px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}
.insurance-popup .option-btn:hover {
  border-color: #4caf50;
  box-shadow: 0 2px 8px rgba(76,175,80,0.1);
}
.insurance-popup .option-btn i {
  font-size: 1.2rem;
  color: #555;
}
.family-count-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
  direction: rtl;
}
.count-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 1.5px solid #e0e0e0;
  background: #fff;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
}
.count-btn:hover {
  border-color: #4caf50;
}
.count-btn.active {
  background: #4caf50;
  color: #fff;
  border-color: #4caf50;
}
.continue-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #66bb6a, #43a047);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  font-family: inherit;
  transition: background 0.2s;
}
.continue-btn:hover {
  background: linear-gradient(135deg, #43a047, #2e7d32);
}
'''

# Old popup content markers to find and replace
OLD_POPUP_START = '<!-- Insurance Selection Popup -->'
OLD_POPUP_END_MARKER = '</script>\n'  # End of the popup JS

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if old popup exists
    if OLD_POPUP_START in content:
        # Find the popup section and replace it
        popup_start = content.find(OLD_POPUP_START)
        # Find the closing </script> after the popup
        # The popup ends with </script>\n</body>
        after_popup = content.find('</script>', popup_start + len(OLD_POPUP_START))
        if after_popup != -1:
            # Find the next </script> which is the popup JS end
            popup_end = after_popup + len('</script>')
            
            # Replace old popup with new one
            old_popup_section = content[popup_start:popup_end]
            content = content[:popup_start] + NEW_POPUP_HTML + NEW_POPUP_JS + content[popup_end:]
            print(f"  ✓ Replaced popup with updated version")
    else:
        # Add popup before </body>
        if '</body>' in content:
            content = content.replace('</body>', NEW_POPUP_HTML + NEW_POPUP_JS + '\n</body>')
            print(f"  ✓ Added new popup")
    
    # Update the CSS - replace old popup CSS with new one
    old_css_marker = '/* Insurance popup modal */'
    if old_css_marker in content:
        # Find and replace the old CSS section
        css_start = content.find(old_css_marker)
        # Find the end of the CSS block (next </style> after this marker)
        css_end = content.find('</style>', css_start)
        if css_end != -1:
            old_css = content[css_start:css_end]
            content = content[:css_start] + NEW_POPUP_CSS + content[css_end:]
            print(f"  ✓ Updated popup CSS")
    else:
        # Add CSS before </head>
        content = content.replace('</head>', '<style>' + NEW_POPUP_CSS + '</style>\n</head>')
        print(f"  ✓ Added popup CSS")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Saved!")

print("\n✅ All popup updates complete!")
