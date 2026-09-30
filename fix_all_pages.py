#!/usr/bin/env python3
"""
Comprehensive fix for ALL form pages to match the original bima.om site.
Uses medical-form.html as the template (it's the most complete) and adapts each page.

Pages to fix:
1. domestic-form.html - تأمين العمالة المنزلية
2. credit-life-form.html - تأمين حياة القرض  
3. home-form.html - تأمين المنازل
4. malpractice-form.html - تأمين الأخطاء الطبية

For each page we need to:
- Fix the heading to Arabic
- Fix the description to Arabic
- Fix form fields to match original
- Fix any English text
- Make malpractice page work (currently blank)
"""
import re

# Read the medical-form as our working template reference
with open('client/public/insurance/medical-form.html', 'r', encoding='utf-8') as f:
    medical_content = f.read()

# ============================================================
# PAGE CONFIGURATIONS - matching the original bima.om exactly
# ============================================================

pages = {
    'domestic-form.html': {
        'heading': 'تأمين العمالة المنزلية',
        'description': 'تأمين يحمي العمالة المنزلية (مثل الخادمات والسائقين) من الإصابات والأمراض المرتبطة بالعمل والمسؤولية. يغطي المصاريف الطبية والتعويضات والمسؤولية القانونية لصاحب العمل وفقاً للقانون.',
        'offers_page': '/insurance/domestic-offers',
        'form_type': 'domestic', # phone + dob + tabs (تأمين على الحياة / Health Insurance)
        'why_title': 'ليش تختار بيمة لتأمين العمالة المنزلية',
        'old_heading_pattern': r'domestic\s*<span[^>]*>\s*insurance\s*</span>',
        'old_description': 'Insurance that protects household employees (e.g., maids, drivers) against work-related injuries, illness, and liability. Covers medical expenses, compensation, and employer legal liability as required by law.',
    },
    'credit-life-form.html': {
        'heading': 'تأمين حياة القرض',
        'description': 'يغطي أرصدة القروض المستحقة في حالة وفاة المقترض أو إعاقته الدائمة. يضمن الحماية المالية للعائلة والمؤسسة المقرضة.',
        'offers_page': '/insurance/credit-life-offers',
        'form_type': 'credit-life', # phone + dob + gender + loan amount + loan duration + tabs (شخصي / سكني)
        'why_title': 'ليش تختار بيمة لتأمين حياة القرض',
        'old_heading_pattern': r'credit life\s*<span[^>]*>\s*insurance\s*</span>',
        'old_description': 'Covers outstanding loan balances in case of death or permanent disability of the borrower. Ensures financial protection for the family and the lending institution.',
    },
    'home-form.html': {
        'heading': 'تأمين المنازل',
        'description': 'تأمين شامل يحمي منزلك ومحتوياته من الأضرار الناتجة عن الحريق والسرقة والكوارث الطبيعية وغيرها من المخاطر.',
        'offers_page': '/insurance/home-offers',
        'form_type': 'home', # phone + dob + gender + marital status (same as medical)
        'why_title': 'ليش تختار بيمة لتأمين المنازل',
        'old_heading_pattern': r'الرئيسية\s*<span[^>]*>\s*insurance\s*</span>',
        'old_description': '',
    },
    'malpractice-form.html': {
        'heading': 'تأمين الأخطاء الطبية',
        'description': 'تأمين يحمي الأطباء والممارسين الصحيين من المطالبات القانونية الناتجة عن الأخطاء الطبية أو الإهمال المهني.',
        'offers_page': '/insurance/malpractice-offers',
        'form_type': 'malpractice', # needs to be built from scratch
        'why_title': 'ليش تختار بيمة لتأمين الأخطاء الطبية',
        'old_heading_pattern': '',
        'old_description': '',
    },
}

# For malpractice, we'll use medical-form as a complete template
# For others, we'll do targeted replacements

def fix_domestic(content):
    """Fix domestic-form.html"""
    info = pages['domestic-form.html']
    
    # Fix heading
    content = re.sub(
        r'page-heading-1">.*?</h1>',
        f'page-heading-1">{info["heading"]}</h1>',
        content,
        flags=re.DOTALL
    )
    
    # Fix description
    content = content.replace(
        'Insurance that protects household employees (e.g., maids, drivers) against work-related injuries, illness, and liability. Covers medical expenses, compensation, and employer legal liability as required by law.',
        info['description']
    )
    
    # Fix "Worker" text in date field
    content = content.replace('Worker تاريخ الميلاد', 'تاريخ الميلاد')
    content = content.replace('Worker', '')
    
    # Fix "Health Insurance" tab text
    content = content.replace('Health Insurance', 'تأمين صحي')
    
    # Fix why section title
    content = re.sub(r'ليش تختار بيمة[^<]*', info['why_title'], content, count=1)
    
    # Fix offers redirect
    content = content.replace("/insurance/domestic-offers", info['offers_page'])
    
    return content

def fix_credit_life(content):
    """Fix credit-life-form.html"""
    info = pages['credit-life-form.html']
    
    # Fix heading
    content = re.sub(
        r'page-heading-1">.*?</h1>',
        f'page-heading-1">{info["heading"]}</h1>',
        content,
        flags=re.DOTALL
    )
    
    # Fix description
    content = content.replace(
        'Covers outstanding loan balances in case of death or permanent disability of the borrower. Ensures financial protection for the family and the lending institution.',
        info['description']
    )
    
    # Fix why section title
    content = re.sub(r'ليش تختار بيمة[^<]*', info['why_title'], content, count=1)
    
    return content

def fix_home(content):
    """Fix home-form.html"""
    info = pages['home-form.html']
    
    # Fix heading - "الرئيسية insurance" → "تأمين المنازل"
    content = re.sub(
        r'page-heading-1">.*?</h1>',
        f'page-heading-1">{info["heading"]}</h1>',
        content,
        flags=re.DOTALL
    )
    
    # Fix why section title
    content = re.sub(r'ليش تختار بيمة[^<]*', info['why_title'], content, count=1)
    
    return content

def fix_malpractice(content, medical_template):
    """Fix malpractice-form.html - rebuild from medical template"""
    info = pages['malpractice-form.html']
    
    # Use medical-form as base
    new_content = medical_template
    
    # Change heading
    new_content = re.sub(
        r'page-heading-1">.*?</h1>',
        f'page-heading-1">{info["heading"]}</h1>',
        new_content,
        flags=re.DOTALL
    )
    
    # Change description
    new_content = new_content.replace(
        'خطة التأمين الصحي التي تساعدك على التعامل مع أية مشاكل صحية مفاجئة وأعباء التكاليف الطبية العالية، من خلال توفير تغطية شاملة للعلاج، والفحوصات، والاستشارات الطبية، مما يمنحك راحة البال والأمان لك ولعائلتك',
        info['description']
    )
    
    # Change offers redirect
    new_content = new_content.replace('/insurance/medical-offers', info['offers_page'])
    
    # Change why section title
    new_content = re.sub(r'ليش تختار بيمة للتأمين الطبي', info['why_title'], new_content)
    new_content = re.sub(r'ليش تختار بيمة[^<]*', info['why_title'], new_content, count=1)
    
    # Change the active nav item highlighting
    # In medical form, "التأمين الصحي" is the current page
    # We need malpractice to show as current
    
    return new_content

# ============================================================
# APPLY FIXES
# ============================================================

# Fix domestic-form.html
print("Fixing domestic-form.html...")
with open('client/public/insurance/domestic-form.html', 'r', encoding='utf-8') as f:
    content = f.read()
content = fix_domestic(content)
with open('client/public/insurance/domestic-form.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("  ✓ Done!")

# Fix credit-life-form.html
print("Fixing credit-life-form.html...")
with open('client/public/insurance/credit-life-form.html', 'r', encoding='utf-8') as f:
    content = f.read()
content = fix_credit_life(content)
with open('client/public/insurance/credit-life-form.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("  ✓ Done!")

# Fix home-form.html
print("Fixing home-form.html...")
with open('client/public/insurance/home-form.html', 'r', encoding='utf-8') as f:
    content = f.read()
content = fix_home(content)
with open('client/public/insurance/home-form.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("  ✓ Done!")

# Fix malpractice-form.html - rebuild from medical template
print("Fixing malpractice-form.html (rebuilding from medical template)...")
content = fix_malpractice(None, medical_content)
with open('client/public/insurance/malpractice-form.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("  ✓ Done!")

print("\n✅ All pages fixed!")
