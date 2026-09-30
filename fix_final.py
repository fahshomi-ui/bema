#!/usr/bin/env python3
"""
Fix 3 issues across all form pages:
1. Replace fa-chevron-down icon (shows as square □) with pure CSS arrow
2. Make calendar icon trigger the date picker when clicked
3. Fix popup so it doesn't auto-redirect - only navigates after user selects option
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ===== FIX 1: Replace fa-chevron-down icon with Unicode arrow =====
    # The icon font isn't loading so it shows as a square box
    # Replace: <i class="fa-solid fa-chevron-down" style="font-size:10px;margin-right:5px;"></i>
    # With: a simple Unicode down arrow ˅
    content = re.sub(
        r'<i class="fa-solid fa-chevron-down"[^>]*></i>',
        '<span style="font-size:11px;margin-right:4px;display:inline-block;">&#x25BE;</span>',
        content
    )
    
    # Also remove the CSS ::after rule that adds another arrow (double arrow issue)
    content = re.sub(
        r'/\* Fix dropdown arrow - add chevron after.*?\*/\s*\.dropdown\.has-sub-menu > a\.menu-title::after \{[^}]+\}',
        '/* Dropdown arrow handled inline */\n.dropdown.has-sub-menu > a.menu-title::after { display: none !important; }',
        content,
        flags=re.DOTALL
    )
    
    # ===== FIX 2: Make calendar icon clickable to open date picker =====
    # Find the bootstrap-date-input-trigger button and make it actually trigger the date input
    # The current trigger button has class "bootstrap-date-input-trigger"
    # We need to add JS that makes clicking it open the native date picker
    
    # ===== FIX 3: Fix popup - prevent auto-redirect =====
    # The issue is the form's submit action or the button's default behavior
    # We need to make sure clicking "احصل على العروض" ONLY shows the popup
    # and navigation only happens when user clicks option inside popup
    
    # Replace the old popup JS with a fixed version
    old_popup_js_pattern = r'<script>\s*var selectedFamilyCount.*?</script>'
    
    new_popup_js = '''<script>
var selectedFamilyCount = 5;

function handleSelfOnly() {
  document.getElementById('insurancePopup').classList.remove('active');
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
  // Intercept ALL clicks on "احصل على العروض" button
  // Use event delegation to catch it regardless of how the button is structured
  document.addEventListener('click', function(e) {
    var target = e.target;
    // Check if clicked element or its parent contains the text
    var el = target;
    for (var i = 0; i < 5; i++) {
      if (!el) break;
      if (el.textContent && el.textContent.trim() === 'احصل على العروض') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        document.getElementById('insurancePopup').classList.add('active');
        // Reset state
        document.getElementById('familyCountSection').style.display = 'none';
        var addBtn = document.getElementById('addFamilyBtn');
        if (addBtn) {
          addBtn.style.borderColor = '';
          addBtn.style.boxShadow = '';
        }
        return false;
      }
      el = el.parentElement;
    }
  }, true); // Use capture phase to intercept before other handlers

  // Also intercept form submission
  var forms = document.querySelectorAll('form');
  forms.forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      e.stopPropagation();
      document.getElementById('insurancePopup').classList.add('active');
      // Reset state
      document.getElementById('familyCountSection').style.display = 'none';
      var addBtn = document.getElementById('addFamilyBtn');
      if (addBtn) {
        addBtn.style.borderColor = '';
        addBtn.style.boxShadow = '';
      }
      return false;
    });
  });

  // Init calendar trigger
  initCalendarTrigger();
});
</script>'''
    
    content = re.sub(old_popup_js_pattern, new_popup_js, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Fixed!")

print("\n✅ All fixes applied!")
