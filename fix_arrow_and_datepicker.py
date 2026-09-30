#!/usr/bin/env python3
"""
Fix:
1. Move arrow from RIGHT of تأمين to LEFT (matching original: ˅ تأمين)
2. Replace datepicker with one that matches original exactly:
   - Appears BELOW the field (not centered popup)
   - Has month dropdown + year dropdown with arrows
   - Blue navigation arrows < >
   - Weekday headers: إث ثل أر خم جم سب أح
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Move arrow to LEFT of تأمين
    # Current: تأمين <span...>▾</span>
    # Should be: <span...>˅</span> تأمين
    # In RTL, "left visually" means BEFORE the text in HTML
    # Original shows: ˅ تأمين (arrow on left side visually)
    # In RTL layout, what appears on LEFT is actually at the END of the text
    # So we need: تأمين <span>˅</span> but the span should have margin-left instead of margin-right
    # Actually looking at original screenshot: "تأمين  ˅" - arrow is to the LEFT of تأمين
    # In RTL, LEFT side = end of line = after the text in HTML
    # Current code already has it after: تأمين <span>▾</span>
    # But margin-right pushes it away from text to the right (which in RTL is toward text start)
    # Need: margin-left instead of margin-right to push it to the left (away from text in RTL)
    
    content = content.replace(
        '<!----> تأمين <span style="font-size:11px;margin-right:4px;display:inline-block;">&#x25BE;</span>',
        '<!----> تأمين <span style="font-size:12px;margin-left:6px;display:inline-block;vertical-align:middle;">&#x25BE;</span>'
    )
    
    # FIX 2: Replace the datepicker overlay with a dropdown-style one that appears below the field
    # Remove old datepicker overlay
    old_datepicker = re.search(r'<!-- Custom Datepicker HTML -->.*?</div>\s*</div>', content, re.DOTALL)
    if old_datepicker:
        content = content.replace(old_datepicker.group(), '')
    
    # Remove old datepicker CSS
    content = re.sub(
        r'/\* Custom datepicker popup styles \*/.*?\.custom-datepicker \.dp-day\.other-month \{[^}]+\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove old datepicker overlay HTML and JS
    content = re.sub(
        r'<div class="custom-datepicker-overlay".*?</div>\s*</div>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # New datepicker CSS + JS that matches original
    NEW_DATEPICKER = '''/* Datepicker - matches original bima.om exactly */
.bima-datepicker {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1050;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  padding: 10px;
  min-width: 280px;
  direction: rtl;
}
.bima-datepicker.open {
  display: block;
}
.bima-dp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 4px 0;
}
.bima-dp-header .dp-nav-btn {
  background: none;
  border: none;
  color: #2196F3;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
}
.bima-dp-header .dp-nav-btn:hover {
  color: #1565C0;
}
.bima-dp-header .dp-selects {
  display: flex;
  align-items: center;
  gap: 6px;
}
.bima-dp-header .dp-selects select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 3px 6px;
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
  background: #fff;
  appearance: auto;
}
.bima-dp-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 4px;
}
.bima-dp-weekdays span {
  font-size: 0.78rem;
  color: #666;
  padding: 4px 0;
  font-weight: 500;
}
.bima-dp-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
}
.bima-dp-day {
  width: 34px;
  height: 34px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.88rem;
  margin: auto;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}
.bima-dp-day:hover {
  background: #e3f2fd;
}
.bima-dp-day.today {
  border: 1px solid #2196F3;
}
.bima-dp-day.selected {
  background: #2196F3;
  color: #fff;
}
.bima-dp-day.other {
  color: #ccc;
}'''

    # Insert new datepicker CSS before the closing </style> that's before </head>
    # Find the FINAL OVERRIDES style section and add to it
    content = content.replace(
        '/* Kill the square',
        NEW_DATEPICKER + '\n\n/* Kill the square'
    )
    
    # Replace the old datepicker JS section
    old_js_pattern = r'// ===== CUSTOM DATEPICKER =====.*?(?=// Close datepicker on overlay click|</script>)'
    
    NEW_DATEPICKER_JS = '''// ===== CUSTOM DATEPICKER - matches original bima.om =====
var dpYear, dpMonth, dpSelectedDate = null, dpTargetInput = null;

var arMonths = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];

function openBimaDP(trigger) {
  // Close any open datepicker first
  document.querySelectorAll('.bima-datepicker').forEach(function(d) { d.remove(); });
  
  var wrap = trigger.closest('[class*="date-input-wrap"]') || trigger.parentElement;
  dpTargetInput = wrap.querySelector('input');
  
  var now = new Date();
  dpYear = now.getFullYear();
  dpMonth = now.getMonth();
  
  var dp = document.createElement('div');
  dp.className = 'bima-datepicker open';
  dp.id = 'bimaDP';
  dp.innerHTML = buildDPHTML();
  
  wrap.style.position = 'relative';
  wrap.appendChild(dp);
  
  // Close on outside click
  setTimeout(function() {
    document.addEventListener('click', closeDPOutside);
  }, 10);
}

function closeDPOutside(e) {
  var dp = document.getElementById('bimaDP');
  if (dp && !dp.contains(e.target) && !e.target.closest('[class*="date-input-trigger"]')) {
    dp.remove();
    document.removeEventListener('click', closeDPOutside);
  }
}

function buildDPHTML() {
  var monthOpts = '';
  for (var i = 0; i < 12; i++) {
    monthOpts += '<option value="' + i + '"' + (i === dpMonth ? ' selected' : '') + '>' + arMonths[i] + '</option>';
  }
  var yearOpts = '';
  for (var y = 2030; y >= 1940; y--) {
    yearOpts += '<option value="' + y + '"' + (y === dpYear ? ' selected' : '') + '>' + y + '</option>';
  }
  
  var html = '<div class="bima-dp-header">';
  html += '<button class="dp-nav-btn" onclick="dpNav(1)">&#x276E;</button>';
  html += '<div class="dp-selects">';
  html += '<select onchange="dpChangeYear(this.value)">' + yearOpts + '</select>';
  html += '<select onchange="dpChangeMonth(this.value)">' + monthOpts + '</select>';
  html += '</div>';
  html += '<button class="dp-nav-btn" onclick="dpNav(-1)">&#x276F;</button>';
  html += '</div>';
  html += '<div class="bima-dp-weekdays"><span>إث</span><span>ثل</span><span>أر</span><span>خم</span><span>جم</span><span>سب</span><span>أح</span></div>';
  html += '<div class="bima-dp-days">' + buildDays() + '</div>';
  return html;
}

function buildDays() {
  var firstDay = new Date(dpYear, dpMonth, 1).getDay();
  // Adjust for Monday start (original uses Monday as first day)
  var startDay = (firstDay === 0) ? 6 : firstDay - 1;
  var daysInMonth = new Date(dpYear, dpMonth + 1, 0).getDate();
  var prevDays = new Date(dpYear, dpMonth, 0).getDate();
  var today = new Date();
  
  var html = '';
  // Previous month
  for (var p = startDay - 1; p >= 0; p--) {
    html += '<button class="bima-dp-day other" onclick="pickDay(' + (prevDays - p) + ',-1)">' + (prevDays - p) + '</button>';
  }
  // Current month
  for (var d = 1; d <= daysInMonth; d++) {
    var cls = 'bima-dp-day';
    if (d === today.getDate() && dpMonth === today.getMonth() && dpYear === today.getFullYear()) cls += ' today';
    html += '<button class="' + cls + '" onclick="pickDay(' + d + ',0)">' + d + '</button>';
  }
  // Next month
  var total = startDay + daysInMonth;
  var rem = (7 - (total % 7)) % 7;
  for (var n = 1; n <= rem; n++) {
    html += '<button class="bima-dp-day other" onclick="pickDay(' + n + ',1)">' + n + '</button>';
  }
  return html;
}

function dpNav(dir) {
  dpMonth += dir;
  if (dpMonth > 11) { dpMonth = 0; dpYear++; }
  if (dpMonth < 0) { dpMonth = 11; dpYear--; }
  refreshDP();
}

function dpChangeMonth(m) { dpMonth = parseInt(m); refreshDP(); }
function dpChangeYear(y) { dpYear = parseInt(y); refreshDP(); }

function refreshDP() {
  var dp = document.getElementById('bimaDP');
  if (dp) dp.innerHTML = buildDPHTML();
}

function pickDay(day, offset) {
  var m = dpMonth + offset;
  var y = dpYear;
  if (m > 11) { m = 0; y++; }
  if (m < 0) { m = 11; y--; }
  var dd = String(day).padStart(2,'0');
  var mm = String(m + 1).padStart(2,'0');
  var formatted = dd + '/' + mm + '/' + y;
  if (dpTargetInput) {
    dpTargetInput.value = formatted;
    dpTargetInput.setAttribute('type','text');
  }
  var dp = document.getElementById('bimaDP');
  if (dp) dp.remove();
  document.removeEventListener('click', closeDPOutside);
}

'''

    # Replace old datepicker JS
    content = re.sub(
        r'// ===== CUSTOM DATEPICKER =====.*?// Close datepicker on overlay click',
        NEW_DATEPICKER_JS + '// Close datepicker on overlay click',
        content,
        flags=re.DOTALL
    )
    
    # Also fix the calendar trigger to use new function
    content = re.sub(
        r"// Attach calendar trigger click handlers.*?(?=</script>)",
        """// Attach calendar trigger click handlers
document.addEventListener('DOMContentLoaded', function() {
  var triggers = document.querySelectorAll('[class*="date-input-trigger"]');
  triggers.forEach(function(trigger) {
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      openBimaDP(trigger);
    });
  });
});
""",
        content,
        flags=re.DOTALL
    )
    
    # Remove the old overlay-based datepicker HTML if still present
    content = re.sub(
        r'<div class="custom-datepicker-overlay"[^>]*>.*?</div>\s*</div>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove old overlay close handler
    content = re.sub(
        r"// Close datepicker on overlay click.*?}\);",
        '',
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ Arrow moved to left + datepicker matches original!")
