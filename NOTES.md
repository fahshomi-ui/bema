# Fix Notes

## Issues to fix:
1. Square □ next to "تأمين" in nav - caused by external CSS `styles-NZVCYVCJ.css` from app.bima.om adding ::after content
2. Calendar icon not opening date picker when clicked
3. Popup should not auto-redirect to offers page

## Solution for square □:
- The external CSS at line 2 `https://app.bima.om/styles-NZVCYVCJ.css` adds a ::after pseudo-element with content that shows as □
- Our CSS at line 159 says `display: none !important` but it's at line 159 while the external CSS loads at line 2
- The external CSS likely has higher specificity or the content is from a different selector
- REAL FIX: Remove the external CSS link OR add the override CSS AFTER the external link with higher specificity
- Alternative: Use JS to remove the ::after content after page load

## File structure:
- External CSS: line 2 - `href="https://app.bima.om/styles-NZVCYVCJ.css"` (loaded TWICE)
- Our override CSS: line 158-159
- Nav HTML: line 330 area - `<li class="dropdown has-sub-menu">...<a>... تأمين <span>▾</span></a>`

## Calendar fix:
- The date input trigger button has class `bootstrap-date-input-trigger`
- Need to make it call showPicker() on the hidden date input
- The date input is `input[type="date"]` inside `.bootstrap-date-input-wrap`

## Original site reference:
- https://app.bima.om/insurance/medical - the original working site
- Arrow next to تأمين is a proper SVG/CSS chevron ˅
- Calendar opens ngb-datepicker (Angular Bootstrap datepicker)
