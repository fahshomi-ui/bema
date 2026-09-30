import re

filepath = 'client/public/insurance/home-form.html'
with open(filepath, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the current arrow CSS rule
old_pattern = r'\.has-sub-menu>\.menu-title::after,\.has-sub-mnu>\.top-mnu::after,\.has-sub-menu>a:after,\.has-sub-menu>a:before\{[^}]+\}'
match = re.search(old_pattern, c)
if match:
    old_rule = match.group()
    print("Found old rule:", old_rule[:80], "...")
    
    # New CSS: 
    # 1. Hide ::before completely (that's the square box)
    # 2. Show arrow in ::after only
    new_rule = '.has-sub-menu>.menu-title::before,.has-sub-mnu>.top-mnu::before,.has-sub-menu>a:before{display:none!important;content:none!important}.has-sub-menu>.menu-title::after,.has-sub-mnu>.top-mnu::after,.has-sub-menu>a:after{content:"\\2304"!important;font-family:inherit!important;font-weight:normal!important;margin-right:5px;font-size:14px;position:static!important;padding:0!important;background:none!important;opacity:1!important;width:auto!important;top:unset!important;left:unset!important;right:unset!important;display:inline!important}'
    
    c = c[:match.start()] + new_rule + c[match.end():]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(c)
    
    print("Fixed! New rule applied.")
    print("Verifying...")
    with open(filepath, 'r', encoding='utf-8') as f:
        verify = f.read()
    print("has before:none:", 'content:none' in verify)
    print("has 2304:", '\\2304' in verify)
else:
    print("Pattern not found!")
    # Try to find what's there
    idx = c.find('has-sub-menu>a:after')
    if idx >= 0:
        print("Found at:", idx)
        print("Context:", c[max(0,idx-50):idx+200])
