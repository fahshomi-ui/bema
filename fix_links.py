#!/usr/bin/env python3
"""
Fix dropdown menu links:
- التأمين على المركبات → javascript:void(0) - we don't have a vehicle form page (only VehicleShortPeriod.html)
  Actually we have VehicleShortPeriod.html! Let's link to it.
- تأمين السفر → javascript:void(0) - we have Travel.html! Let's link to it.

Also the issue might be that the links with target="_blank" and class="external-link" 
are preventing navigation. Let me fix those too.
"""
import glob

FORM_DIR = "client/public/insurance"
FORM_FILES = glob.glob(f"{FORM_DIR}/*-form.html")

for filepath in FORM_FILES:
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix التأمين على المركبات - link to VehicleShortPeriod.html
    content = content.replace(
        '<a target="_blank" rel="noopener noreferrer" class="external-link" href="javascript:void(0)"> التأمين على المركبات </a>',
        '<a href="/insurance/VehicleShortPeriod.html"> التأمين على المركبات </a>'
    )
    
    # Fix تأمين السفر - link to Travel.html
    content = content.replace(
        '<a target="_blank" rel="noopener noreferrer" class="external-link" href="javascript:void(0)"> تأمين السفر </a>',
        '<a href="/insurance/Travel.html"> تأمين السفر </a>'
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Done!")

print("\n✅ All dropdown links fixed!")
