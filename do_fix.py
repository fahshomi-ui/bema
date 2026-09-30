#!/usr/bin/env python3
"""Apply FA override CSS and custom datepicker to home-form.html"""
import sys

filepath = 'client/public/insurance/home-form.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Read {len(lines)} lines')

# Find the CDN link line
cdn_line_idx = None
for i, line in enumerate(lines):
    if 'cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1' in line:
        cdn_line_idx = i
        break

if cdn_line_idx is None:
    print('ERROR: CDN link not found')
    sys.exit(1)

# Insert FA fix and datepicker CSS after CDN line
fa_fix_line = '<style id="fa-fix">.fa-solid,.fas,.fa{font-family:"Font Awesome 6 Free"!important;font-weight:900!important}.fa-brands,.fab{font-family:"Font Awesome 6 Brands"!important;font-weight:400!important}.fa-3x{font-size:3em!important}.feature-card i.fa-solid{color:#4CAF50;margin-bottom:10px}.bootstrap-date-input-trigger{right:auto!important;left:10px!important}.bootstrap-date-input-wrap .form-control{padding-right:0.75rem!important;padding-left:2.4rem!important}</style>\n'

dp_css_line = '<style id="bima-datepicker-css">.bima-datepicker{display:none;position:absolute;top:100%;left:0;right:0;z-index:1050;background:#fff;border:1px solid #e0e0e0;border-radius:4px;box-shadow:0 4px 12px rgba(0,0,0,0.1);padding:10px;min-width:280px;direction:rtl}.bima-datepicker.open{display:block}.bima-dp-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;padding:4px 0}.bima-dp-header .dp-nav-btn{background:none;border:none;color:#2196F3;font-size:18px;font-weight:bold;cursor:pointer;padding:4px 8px;line-height:1}.bima-dp-header .dp-nav-btn:hover{color:#1565C0}.bima-dp-header .dp-selects{display:flex;align-items:center;gap:6px}.bima-dp-header .dp-selects select{border:1px solid #ddd;border-radius:4px;padding:3px 6px;font-size:0.9rem;cursor:pointer;background:#fff;appearance:auto}.bima-dp-weekdays{display:grid;grid-template-columns:repeat(7,1fr);text-align:center;margin-bottom:4px}.bima-dp-weekdays span{font-size:0.78rem;color:#666;padding:4px 0;font-weight:500}.bima-dp-days{display:grid;grid-template-columns:repeat(7,1fr);text-align:center}.bima-dp-day{width:34px;height:34px;border:none;background:none;cursor:pointer;font-size:0.88rem;margin:auto;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#333}.bima-dp-day:hover{background:#e3f2fd}.bima-dp-day.today{border:1px solid #2196F3}.bima-dp-day.selected{background:#2196F3;color:#fff}.bima-dp-day.other{color:#ccc}</style>\n'

lines.insert(cdn_line_idx + 1, fa_fix_line)
lines.insert(cdn_line_idx + 2, dp_css_line)
print('FIX 1 OK: FA override + datepicker CSS inserted')

# Now find DATE PICKER and FORM VALIDATION markers (line numbers shifted by 2)
dp_start = None
dp_end = None
for i, line in enumerate(lines):
    if '// ============ DATE PICKER ============' in line:
        dp_start = i
    if '// ============ FORM VALIDATION ============' in line:
        dp_end = i

if dp_start is None or dp_end is None:
    print(f'ERROR: DATE PICKER={dp_start}, FORM VALIDATION={dp_end}')
    sys.exit(1)

# Custom datepicker JS lines
custom_dp_lines = [
    '    // ============ CUSTOM DATEPICKER ============\n',
    '    var dpYear, dpMonth, dpSelectedDate = null, dpTargetInput = null;\n',
    "    var arMonths = ['\u064a\u0646\u0627\u064a\u0631','\u0641\u0628\u0631\u0627\u064a\u0631','\u0645\u0627\u0631\u0633','\u0623\u0628\u0631\u064a\u0644','\u0645\u0627\u064a\u0648','\u064a\u0648\u0646\u064a\u0648','\u064a\u0648\u0644\u064a\u0648','\u0623\u063a\u0633\u0637\u0633','\u0633\u0628\u062a\u0645\u0628\u0631','\u0623\u0643\u062a\u0648\u0628\u0631','\u0646\u0648\u0641\u0645\u0628\u0631','\u062f\u064a\u0633\u0645\u0628\u0631'];\n",
    '    function openBimaDP(trigger){\n',
    "      document.querySelectorAll('.bima-datepicker').forEach(function(d){d.remove();});\n",
    "      var wrap=trigger.closest('.bootstrap-date-input-wrap')||trigger.parentElement;\n",
    "      dpTargetInput=wrap.querySelector('input[type=\"text\"]')||wrap.querySelector('input');\n",
    '      var now=new Date();dpYear=now.getFullYear();dpMonth=now.getMonth();\n',
    "      var dp=document.createElement('div');dp.className='bima-datepicker open';dp.id='bimaDP';\n",
    "      dp.innerHTML=buildDPHTML();wrap.style.position='relative';wrap.appendChild(dp);\n",
    "      setTimeout(function(){document.addEventListener('click',closeDPOutside);},10);\n",
    '    }\n',
    '    function closeDPOutside(e){\n',
    "      var dp=document.getElementById('bimaDP');\n",
    "      if(dp&&!dp.contains(e.target)&&!e.target.closest('.bootstrap-date-input-trigger')&&!e.target.closest('#policyStartDate')){\n",
    "        dp.remove();document.removeEventListener('click',closeDPOutside);\n",
    '      }\n',
    '    }\n',
    '    function buildDPHTML(){\n',
    "      var mo='';for(var i=0;i<12;i++)mo+='<option value=\"'+i+'\"'+(i===dpMonth?' selected':'')+'>'+arMonths[i]+'</option>';\n",
    "      var yo='';for(var y=2030;y>=1940;y--)yo+='<option value=\"'+y+'\"'+(y===dpYear?' selected':'')+'>'+y+'</option>';\n",
    "      var h='<div class=\"bima-dp-header\">';\n",
    '      h+=\'<button type="button" class="dp-nav-btn" onclick="dpNav(1)">\\u276e</button>\';\n',
    '      h+=\'<div class="dp-selects"><select onchange="dpChangeYear(this.value)">\'+yo+\'</select>\';\n',
    '      h+=\'<select onchange="dpChangeMonth(this.value)">\'+mo+\'</select></div>\';\n',
    '      h+=\'<button type="button" class="dp-nav-btn" onclick="dpNav(-1)">\\u276f</button></div>\';\n',
    "      h+='<div class=\"bima-dp-weekdays\"><span>\u0625\u062b</span><span>\u062b\u0644</span><span>\u0623\u0631</span><span>\u062e\u0645</span><span>\u062c\u0645</span><span>\u0633\u0628</span><span>\u0623\u062d</span></div>';\n",
    "      h+='<div class=\"bima-dp-days\">'+buildDays()+'</div>';return h;\n",
    '    }\n',
    '    function buildDays(){\n',
    '      var fd=new Date(dpYear,dpMonth,1).getDay();var sd=(fd===0)?6:fd-1;\n',
    '      var dim=new Date(dpYear,dpMonth+1,0).getDate();var pd=new Date(dpYear,dpMonth,0).getDate();\n',
    "      var today=new Date();var h='';\n",
    '      for(var p=sd-1;p>=0;p--)h+=\'<button type="button" class="bima-dp-day other" onclick="pickDay(\'+(pd-p)+\',-1)">\'+(pd-p)+\'</button>\';\n',
    "      for(var d=1;d<=dim;d++){var c='bima-dp-day';if(d===today.getDate()&&dpMonth===today.getMonth()&&dpYear===today.getFullYear())c+=' today';h+='<button type=\"button\" class=\"'+c+'\" onclick=\"pickDay('+d+',0)\">'+d+'</button>';}\n",
    "      var t=sd+dim;var r=(7-(t%7))%7;\n",
    '      for(var n=1;n<=r;n++)h+=\'<button type="button" class="bima-dp-day other" onclick="pickDay(\'+n+\',1)">\'+ n+\'</button>\';return h;\n',
    '    }\n',
    '    function dpNav(dir){dpMonth+=dir;if(dpMonth>11){dpMonth=0;dpYear++;}if(dpMonth<0){dpMonth=11;dpYear--;}refreshDP();}\n',
    '    function dpChangeMonth(m){dpMonth=parseInt(m);refreshDP();}\n',
    '    function dpChangeYear(y){dpYear=parseInt(y);refreshDP();}\n',
    "    function refreshDP(){var dp=document.getElementById('bimaDP');if(dp)dp.innerHTML=buildDPHTML();}\n",
    '    function pickDay(day,offset){\n',
    '      var m=dpMonth+offset,y=dpYear;if(m>11){m=0;y++;}if(m<0){m=11;y--;}\n',
    "      var dd=String(day).padStart(2,'0'),mm=String(m+1).padStart(2,'0');\n",
    "      if(dpTargetInput)dpTargetInput.value=dd+'/'+mm+'/'+y;\n",
    "      var dp=document.getElementById('bimaDP');if(dp)dp.remove();\n",
    "      document.removeEventListener('click',closeDPOutside);\n",
    '    }\n',
    "    document.querySelectorAll('.bootstrap-date-input-trigger').forEach(function(trigger){\n",
    "      trigger.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();openBimaDP(trigger);});\n",
    '    });\n',
    "    var pdi=document.getElementById('policyStartDate');\n",
    "    if(pdi){pdi.addEventListener('click',function(){var t=this.closest('.bootstrap-date-input-wrap');if(t){var btn=t.querySelector('.bootstrap-date-input-trigger');if(btn)openBimaDP(btn);}});}\n",
    '\n',
]

# Replace lines from dp_start to dp_end (exclusive)
lines = lines[:dp_start] + custom_dp_lines + lines[dp_end:]
print('FIX 2 OK: Custom datepicker JS replaced native date picker')

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
content = ''.join(lines)
print(f'Final: {len(lines)} lines, {len(content)} chars')
print(f'fa-fix: {content.count("fa-fix")}')
print(f'openBimaDP: {content.count("openBimaDP")}')
print(f'buildingCardCol.*none: {"buildingCardCol" in content}')
