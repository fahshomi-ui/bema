#!/usr/bin/env python3
"""
Fix nav links in all form pages:
1. "الرئيسية" -> points to our site root /
2. Dropdown items -> point to our site pages (/insurance/xxx-form)
3. "تتبع الطلب" -> disable (remove link functionality)
4. "تأمين للركبات" and "تأمين السفر" -> keep as external to bima.om (since we don't have those pages)
   Actually NO - user said ALL links go to our site. For pages we don't have, just use # or remove.
"""
import glob
import re

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix "الرئيسية" link - point to our site root
    content = content.replace(
        'href="https://bima.om/"><!----> الرئيسية',
        'href="/"><!----> الرئيسية'
    )
    
    # Fix "تتبع الطلب" - disable the link
    content = content.replace(
        'href="https://bima.om/Customer/SignIn"><!----> تتبع الطلب',
        'href="javascript:void(0)" style="pointer-events:none;opacity:0.5;cursor:default;"><!----> تتبع الطلب'
    )
    
    # Fix dropdown menu items - point to our pages
    # تأمين للركبات - we don't have this page, so disable or link to #
    content = content.replace(
        'href="https://bima.om/#MotorForm"> تأمين للركبات',
        'href="javascript:void(0)"> تأمين للركبات'
    )
    
    # تأمين السفر - we don't have this page
    content = content.replace(
        'href="https://bima.om/insurance/Travel"> تأمين السفر',
        'href="javascript:void(0)"> تأمين السفر'
    )
    
    # Fix footer links too
    content = content.replace(
        'href="https://bima.om/" target="_blank" rel="noopener"> الرئيسية',
        'href="/"> الرئيسية'
    )
    content = content.replace(
        'href="https://bima.om/Home/Terms" target="_blank" rel="noopener">الشروط',
        'href="javascript:void(0)">الشروط'
    )
    content = content.replace(
        'href="https://bima.om/Home/Terms" target="_blank" rel="noopener noreferrer"',
        'href="javascript:void(0)"'
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ All nav links fixed!")
