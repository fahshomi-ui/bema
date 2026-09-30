#!/usr/bin/env python3
"""
Final fix:
1. Arrow ▾ on LEFT of تأمين (after the ن character)
   - In RTL, text flows right-to-left
   - The screenshot shows: "الصفحة الرئيسية    تأمين ˅    تتبع الطلب"
   - Arrow is AFTER تأمين visually (to its left in RTL)
   - In RTL HTML: span AFTER text appears on LEFT visually
   - Current: تأمين <span>▾</span> - this should already be on the left
   - BUT the issue is margin-right pushes it away. In RTL margin-right = margin toward the text
   - Let me use direction:ltr on the span to force it, or just use margin-left
   
2. Accordion FAQ - add JS to toggle open/close
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Arrow position
    # Current: تأمين <span style="font-size:10px;margin-right:4px;">&#x25BE;</span>
    # In RTL, margin-right on the span pushes it AWAY from the text (to the left)
    # But the user says it's on the WRONG side. Let me put it BEFORE the text instead.
    # In RTL: element BEFORE text in HTML = appears on RIGHT visually
    # Element AFTER text in HTML = appears on LEFT visually
    # 
    # From the user's screenshot, the arrow appears on the RIGHT of تأمين (before it)
    # They want it on the LEFT (after it)
    # Current code has it AFTER the text, which in RTL should be on LEFT...
    # 
    # WAIT - looking at the screenshot again: "˅ تأمين" - the arrow is to the LEFT of the word
    # and the user is saying "اخرها على يسارها بعد حرف ن" = put it on the left after letter ن
    # That means: تأمين˅  (arrow right after the ن, on its left side)
    # 
    # The current code already has it after تأمين. The issue might be that margin-right
    # in RTL actually pushes it to the RIGHT (toward the text). Let me remove margin and 
    # just put it directly after with a tiny gap.
    
    content = content.replace(
        '<!----> تأمين <span style="font-size:10px;margin-right:4px;">&#x25BE;</span>',
        '<!----> <span style="font-size:10px;margin-left:4px;display:inline;">&#x25BE;</span>تأمين '
    )
    
    # FIX 2: Add accordion toggle JS (Bootstrap 5 accordion without Bootstrap JS)
    accordion_js = """
<script>
// Accordion toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  var buttons = document.querySelectorAll('.accordion-button');
  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = this.closest('.accordion-item').querySelector('.accordion-collapse');
      var isOpen = target.classList.contains('show');
      
      // Close all
      document.querySelectorAll('.accordion-collapse').forEach(function(el) {
        el.classList.remove('show');
        el.style.display = 'none';
      });
      document.querySelectorAll('.accordion-button').forEach(function(el) {
        el.classList.add('collapsed');
        el.setAttribute('aria-expanded', 'false');
      });
      
      // Toggle current
      if (!isOpen) {
        target.classList.add('show');
        target.style.display = 'block';
        this.classList.remove('collapsed');
        this.setAttribute('aria-expanded', 'true');
      }
    });
  });
  
  // Initialize - hide all collapsed items
  document.querySelectorAll('.accordion-collapse').forEach(function(el) {
    if (!el.classList.contains('show')) {
      el.style.display = 'none';
    }
  });
});
</script>
"""
    # Add before closing </body> or at end
    if '</body>' in content:
        content = content.replace('</body>', accordion_js + '</body>')
    else:
        content += accordion_js
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ All fixes applied!")
