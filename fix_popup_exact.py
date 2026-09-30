#!/usr/bin/env python3
"""
Update the popup in all form pages to match the original EXACTLY:
- Same styling, same layout
- When "أخرى" is selected, show a number input field "أدخل عدد الأفراد"
- Green gradient button "متابعة" with rounded corners
- Exact same font sizes, spacing, colors
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

# New popup CSS that matches the original exactly
NEW_POPUP_CSS = '''/* Insurance popup modal - exact match to original */
.insurance-popup-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 9999;
  justify-content: center;
  align-items: center;
}
.insurance-popup-overlay.active {
  display: flex;
}
.insurance-popup {
  background: #fff;
  border-radius: 20px;
  padding: 45px 40px 35px;
  max-width: 560px;
  width: 92%;
  position: relative;
  text-align: center;
  max-height: 90vh;
  overflow-y: auto;
  direction: rtl;
}
.insurance-popup .close-btn {
  position: absolute;
  top: 18px;
  left: 18px;
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  width: 34px;
  height: 34px;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-weight: 300;
  line-height: 1;
}
.insurance-popup .close-btn:hover {
  background: #f5f5f5;
}
.insurance-popup h3 {
  font-size: 1.7rem;
  margin-bottom: 12px;
  font-weight: 700;
  color: #1a1a1a;
  margin-top: 0;
}
.insurance-popup .popup-desc {
  color: #666;
  margin-bottom: 28px;
  font-size: 0.92rem;
  line-height: 1.5;
}
.insurance-popup .option-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 22px 20px;
  margin-bottom: 14px;
  border: 1.5px solid #e8e8e8;
  border-radius: 14px;
  background: #fff;
  font-size: 1.05rem;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  color: #333;
}
.insurance-popup .option-btn:hover {
  border-color: #7bc333;
}
.insurance-popup .option-btn.selected {
  border-color: #7bc333;
  box-shadow: 0 0 0 2px rgba(123,195,51,0.15);
}
.insurance-popup .option-btn svg {
  width: 22px;
  height: 22px;
  fill: none;
  stroke: #555;
  stroke-width: 1.5;
}
.family-count-section {
  display: none;
  margin-top: 22px;
  text-align: right;
}
.family-count-section.show {
  display: block;
}
.family-count-section .count-label {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 16px;
  color: #333;
}
.family-count-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-bottom: 18px;
  direction: rtl;
}
.count-btn {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  border: 1.5px solid #e0e0e0;
  background: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  color: #333;
}
.count-btn:hover {
  border-color: #7bc333;
}
.count-btn.active {
  background: #7bc333;
  color: #fff;
  border-color: #7bc333;
}
.other-input-wrap {
  display: none;
  margin-bottom: 18px;
}
.other-input-wrap.show {
  display: block;
}
.other-input-wrap input {
  width: 100%;
  height: 54px;
  border: 1.5px solid #e0e0e0;
  border-radius: 14px;
  padding: 0 16px;
  font-size: 1rem;
  font-family: inherit;
  text-align: right;
  direction: rtl;
  outline: none;
}
.other-input-wrap input:focus {
  border-color: #7bc333;
}
.other-input-wrap input::placeholder {
  color: #999;
}
.continue-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(to bottom, #a8e063, #56ab2f);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 8px;
  font-family: inherit;
  transition: opacity 0.2s;
  box-shadow: 0 4px 15px rgba(86,171,47,0.3);
}
.continue-btn:hover {
  opacity: 0.9;
}
'''

# New popup HTML that matches the original exactly
NEW_POPUP_HTML = '''
<!-- Insurance Selection Popup -->
<div class="insurance-popup-overlay" id="insurancePopup">
  <div class="insurance-popup">
    <button class="close-btn" onclick="closePopup()">X</button>
    <h3>من تريد التأمين عليه؟</h3>
    <p class="popup-desc">اختر ما إذا كنت تريد التغطية لنفسك فقط أو تضمين أفراد عائلتك.</p>
    
    <button class="option-btn" id="selfOnlyBtn" onclick="handleSelfOnly()">
      <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
      أنا المؤمن عليه فقط
    </button>
    
    <button class="option-btn" id="addFamilyBtn" onclick="handleAddFamily()">
      <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
      إضافة أفراد الأسرة للتأمين
    </button>
    
    <div class="family-count-section" id="familyCountSection">
      <p class="count-label">كم عدد أفراد العائلة الذين تريد إضافتهم؟</p>
      <div class="family-count-grid">
        <button class="count-btn" onclick="selectCount(this,1)">1</button>
        <button class="count-btn" onclick="selectCount(this,2)">2</button>
        <button class="count-btn" onclick="selectCount(this,3)">3</button>
        <button class="count-btn" onclick="selectCount(this,4)">4</button>
        <button class="count-btn" onclick="selectCount(this,5)">5</button>
        <button class="count-btn" onclick="selectCount(this,6)">6</button>
        <button class="count-btn" onclick="selectCount(this,7)">7</button>
        <button class="count-btn" onclick="selectCount(this,8)">8</button>
        <button class="count-btn" onclick="selectCount(this,9)">9</button>
        <button class="count-btn" onclick="selectOther(this)">أخرى</button>
      </div>
      <div class="other-input-wrap" id="otherInputWrap">
        <input type="number" id="otherCountInput" placeholder="أدخل عدد الأفراد" min="1" max="50">
      </div>
      <button class="continue-btn" onclick="handleContinue()">متابعة</button>
    </div>
  </div>
</div>
'''

# New popup JS
NEW_POPUP_JS = '''<script>
var selectedFamilyCount = null;

function closePopup() {
  document.getElementById('insurancePopup').classList.remove('active');
}

function handleSelfOnly() {
  document.getElementById('insurancePopup').classList.remove('active');
  var currentPage = window.location.pathname;
  var offersPage = currentPage.replace('-form', '-offers');
  window.location.href = offersPage;
}

function handleAddFamily() {
  document.getElementById('familyCountSection').classList.add('show');
  document.getElementById('addFamilyBtn').classList.add('selected');
  document.getElementById('selfOnlyBtn').classList.remove('selected');
}

function selectCount(el, num) {
  selectedFamilyCount = num;
  var btns = document.querySelectorAll('.count-btn');
  btns.forEach(function(b) { b.classList.remove('active'); });
  el.classList.add('active');
  document.getElementById('otherInputWrap').classList.remove('show');
}

function selectOther(el) {
  selectedFamilyCount = 'other';
  var btns = document.querySelectorAll('.count-btn');
  btns.forEach(function(b) { b.classList.remove('active'); });
  el.classList.add('active');
  document.getElementById('otherInputWrap').classList.add('show');
  document.getElementById('otherCountInput').focus();
}

function handleContinue() {
  var count = selectedFamilyCount;
  if (count === 'other') {
    count = document.getElementById('otherCountInput').value;
    if (!count || count < 1) return;
  }
  if (!count) return;
  document.getElementById('insurancePopup').classList.remove('active');
  var currentPage = window.location.pathname;
  var offersPage = currentPage.replace('-form', '-offers');
  window.location.href = offersPage + '?family=' + count;
}

// Calendar icon click handler
function initCalendarTrigger() {
  var triggers = document.querySelectorAll('.bootstrap-date-input-trigger');
  triggers.forEach(function(trigger) {
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      var wrap = trigger.closest('.bootstrap-date-input-wrap');
      if (wrap) {
        var dateInput = wrap.querySelector('input[type="date"]');
        if (dateInput) {
          dateInput.showPicker ? dateInput.showPicker() : dateInput.click();
        }
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  // Intercept clicks on "احصل على العروض" button using capture phase
  document.addEventListener('click', function(e) {
    var target = e.target;
    var el = target;
    for (var i = 0; i < 5; i++) {
      if (!el) break;
      if (el.textContent && el.textContent.trim() === 'احصل على العروض') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        // Show popup and reset state
        document.getElementById('insurancePopup').classList.add('active');
        document.getElementById('familyCountSection').classList.remove('show');
        document.getElementById('otherInputWrap').classList.remove('show');
        document.getElementById('addFamilyBtn').classList.remove('selected');
        document.getElementById('selfOnlyBtn').classList.remove('selected');
        var btns = document.querySelectorAll('.count-btn');
        btns.forEach(function(b) { b.classList.remove('active'); });
        selectedFamilyCount = null;
        return false;
      }
      el = el.parentElement;
    }
  }, true);

  // Also intercept form submission
  var forms = document.querySelectorAll('form');
  forms.forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      e.stopPropagation();
      document.getElementById('insurancePopup').classList.add('active');
      document.getElementById('familyCountSection').classList.remove('show');
      document.getElementById('otherInputWrap').classList.remove('show');
      document.getElementById('addFamilyBtn').classList.remove('selected');
      document.getElementById('selfOnlyBtn').classList.remove('selected');
      var btns = document.querySelectorAll('.count-btn');
      btns.forEach(function(b) { b.classList.remove('active'); });
      selectedFamilyCount = null;
      return false;
    });
  });

  initCalendarTrigger();
});
</script>'''

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove old popup CSS
    content = re.sub(
        r'/\* Insurance popup modal.*?</style>\s*\n\s*</head>',
        NEW_POPUP_CSS + '</style>\n\n</head>',
        content,
        flags=re.DOTALL
    )
    
    # Remove old popup HTML and JS
    content = re.sub(
        r'\n<!-- Insurance Selection Popup -->.*?</script>',
        NEW_POPUP_HTML + '\n' + NEW_POPUP_JS,
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ All popups updated to match original exactly!")
