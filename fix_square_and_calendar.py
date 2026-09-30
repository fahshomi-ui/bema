#!/usr/bin/env python3
"""
DEFINITIVE FIX for:
1. Square □ next to "تأمين" - The external CSS from bima.om adds ::after content.
   Solution: Add a <style> tag RIGHT BEFORE </body> with maximum specificity to override.
2. Calendar icon - make it open a custom datepicker popup when clicked.
   Solution: Add JS that shows a proper datepicker on click.
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

# This CSS+JS block goes right before </body> to ensure it loads LAST and overrides everything
FINAL_OVERRIDE_BLOCK = '''
<!-- FINAL OVERRIDES - loads last to override external CSS -->
<style>
/* Kill the square □ from external CSS - maximum specificity */
.dropdown.has-sub-menu > a.menu-title::after,
.dropdown.has-sub-menu > a.menu-title::before,
li.dropdown.has-sub-menu > a::after,
li.dropdown.has-sub-menu > a::before,
.nav-menu .dropdown.has-sub-menu > a.menu-title::after,
.nav-menu .dropdown.has-sub-menu > a.menu-title::before,
.nav-menu > li.dropdown.has-sub-menu > a::after,
.nav-menu > li.dropdown.has-sub-menu > a::before,
.main-navbar .nav-menu > li.dropdown.has-sub-menu > a.nav-link.menu-title::after,
.main-navbar .nav-menu > li.dropdown.has-sub-menu > a.nav-link.menu-title::before {
  display: none !important;
  content: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  font-size: 0 !important;
  opacity: 0 !important;
}

/* Custom datepicker popup styles */
.custom-datepicker-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 10000;
  justify-content: center;
  align-items: center;
}
.custom-datepicker-overlay.active {
  display: flex;
}
.custom-datepicker {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  min-width: 300px;
  direction: rtl;
  text-align: center;
}
.custom-datepicker .dp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}
.custom-datepicker .dp-header button {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.custom-datepicker .dp-header button:hover {
  background: #f5f5f5;
}
.custom-datepicker .dp-header .dp-month-year {
  font-weight: 600;
  font-size: 1rem;
}
.custom-datepicker .dp-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 5px;
}
.custom-datepicker .dp-weekdays span {
  font-size: 0.75rem;
  color: #999;
  text-align: center;
  padding: 5px 0;
}
.custom-datepicker .dp-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}
.custom-datepicker .dp-day {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.9rem;
  margin: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.custom-datepicker .dp-day:hover {
  background: #e8f5e9;
}
.custom-datepicker .dp-day.selected {
  background: #4caf50;
  color: #fff;
}
.custom-datepicker .dp-day.today {
  border: 1px solid #4caf50;
}
.custom-datepicker .dp-day.other-month {
  color: #ccc;
}
</style>

<!-- Custom Datepicker HTML -->
<div class="custom-datepicker-overlay" id="datepickerOverlay">
  <div class="custom-datepicker" id="datepickerWidget">
    <div class="dp-header">
      <button onclick="dpNextMonth()">&#x276E;</button>
      <span class="dp-month-year" id="dpMonthYear"></span>
      <button onclick="dpPrevMonth()">&#x276F;</button>
    </div>
    <div class="dp-weekdays">
      <span>أحد</span><span>اثن</span><span>ثلا</span><span>أرب</span><span>خمي</span><span>جمع</span><span>سبت</span>
    </div>
    <div class="dp-days" id="dpDays"></div>
  </div>
</div>

<script>
// ===== FIX SQUARE: Remove any ::after content via JS as backup =====
(function() {
  var links = document.querySelectorAll('.has-sub-menu > a.menu-title, li.has-sub-menu > a');
  links.forEach(function(a) {
    // Force remove any pseudo-element by adding inline style override
    var style = document.createElement('style');
    style.textContent = '[class*="has-sub-menu"] > a.menu-title::after, [class*="has-sub-menu"] > a.menu-title::before { display:none!important; content:none!important; }';
    document.head.appendChild(style);
  });
})();

// ===== CUSTOM DATEPICKER =====
var dpCurrentDate = new Date();
var dpSelectedDate = null;
var dpTargetInput = null;

var arabicMonths = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];

function openDatepicker(inputEl) {
  dpTargetInput = inputEl;
  dpCurrentDate = new Date();
  renderDatepicker();
  document.getElementById('datepickerOverlay').classList.add('active');
}

function closeDatepicker() {
  document.getElementById('datepickerOverlay').classList.remove('active');
}

function dpPrevMonth() {
  dpCurrentDate.setMonth(dpCurrentDate.getMonth() - 1);
  renderDatepicker();
}

function dpNextMonth() {
  dpCurrentDate.setMonth(dpCurrentDate.getMonth() + 1);
  renderDatepicker();
}

function renderDatepicker() {
  var year = dpCurrentDate.getFullYear();
  var month = dpCurrentDate.getMonth();
  document.getElementById('dpMonthYear').textContent = arabicMonths[month] + ' ' + year;
  
  var firstDay = new Date(year, month, 1).getDay();
  var daysInMonth = new Date(year, month + 1, 0).getDate();
  var daysInPrevMonth = new Date(year, month, 0).getDate();
  
  var html = '';
  // Previous month days
  for (var i = firstDay - 1; i >= 0; i--) {
    html += '<button class="dp-day other-month" onclick="selectDpDay(this,' + (daysInPrevMonth - i) + ',-1)">' + (daysInPrevMonth - i) + '</button>';
  }
  // Current month days
  var today = new Date();
  for (var d = 1; d <= daysInMonth; d++) {
    var cls = 'dp-day';
    if (d === today.getDate() && month === today.getMonth() && year === today.getFullYear()) cls += ' today';
    html += '<button class="' + cls + '" onclick="selectDpDay(this,' + d + ',0)">' + d + '</button>';
  }
  // Next month days
  var totalCells = firstDay + daysInMonth;
  var remaining = (7 - (totalCells % 7)) % 7;
  for (var n = 1; n <= remaining; n++) {
    html += '<button class="dp-day other-month" onclick="selectDpDay(this,' + n + ',1)">' + n + '</button>';
  }
  
  document.getElementById('dpDays').innerHTML = html;
}

function selectDpDay(el, day, monthOffset) {
  var year = dpCurrentDate.getFullYear();
  var month = dpCurrentDate.getMonth() + monthOffset;
  var selected = new Date(year, month, day);
  
  // Format as dd/mm/yyyy
  var dd = String(selected.getDate()).padStart(2, '0');
  var mm = String(selected.getMonth() + 1).padStart(2, '0');
  var yyyy = selected.getFullYear();
  var formatted = dd + '/' + mm + '/' + yyyy;
  
  if (dpTargetInput) {
    dpTargetInput.value = formatted;
    dpTargetInput.setAttribute('type', 'text');
  }
  closeDatepicker();
}

// Close datepicker on overlay click
document.getElementById('datepickerOverlay').addEventListener('click', function(e) {
  if (e.target === this) closeDatepicker();
});

// Attach calendar trigger click handlers
document.addEventListener('DOMContentLoaded', function() {
  var triggers = document.querySelectorAll('.bootstrap-date-input-trigger, [class*="date-input-trigger"]');
  triggers.forEach(function(trigger) {
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var wrap = trigger.closest('[class*="date-input-wrap"]');
      var input = null;
      if (wrap) {
        input = wrap.querySelector('input');
      }
      if (!input) {
        input = trigger.parentElement.querySelector('input');
      }
      openDatepicker(input);
    });
  });
});
</script>
'''

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any existing FINAL OVERRIDES block
    content = re.sub(r'\n<!-- FINAL OVERRIDES.*?</script>\s*', '', content, flags=re.DOTALL)
    
    # Insert the override block right before </body>
    content = content.replace('</body>', FINAL_OVERRIDE_BLOCK + '\n</body>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ All fixes applied - square removed, datepicker added!")
