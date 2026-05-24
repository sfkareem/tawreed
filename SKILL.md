# XLSX Skill Definition

This document outlines standard requirements for creating, editing, and formatting spreadsheet files.

## Requirements for Outputs

### All Excel files

#### Professional Font
- Use a consistent, professional font (e.g., Arial, Segoe UI, Calibri) for all deliverables unless otherwise instructed by the user.

#### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`).

#### Gridlines
- Always ensure gridlines are visible: `ws.views.sheetView[0].showGridLines = True` (or equivalent).

### Financial and Takeoff Models

#### Color Coding Standards
Unless otherwise stated by the user or existing template:
- **Blue text (RGB: 0,0,255 / Hex: 0000FF)**: Hardcoded inputs, and numbers users will change (e.g., supplier unit rates, brands, models, remarks).
- **Black text (RGB: 0,0,0 / Hex: 000000)**: All formulas, calculations, and static system-populated description columns.
- **Green text (RGB: 0,128,0 / Hex: 008000)**: Links pulling from other worksheets within the same workbook.
- **Red text (RGB: 255,0,0 / Hex: FF0000)**: External links to other files.
- **Yellow background (RGB: 255,255,0 / Hex: FFFF00)**: Key assumptions needing attention or cells that need to be updated.

#### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024").
- **Currency**: Use local or specified currency format (e.g. `#,##0.00` or `$#,##0.00`).
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., `_($* -_);_($* (#,##0);_($* "-"_);_(@_)` or custom number format).
- **Percentages**: Default to `0.0%` format (one decimal).
- **Multiples**: Format as `0.0x` for valuation multiples.
- **Negative numbers**: Use parentheses `(123)` not minus `-123`.

#### Formula Construction Rules
- **Assumptions Placement**: Place all assumptions in separate cells, and reference them. Never hardcode numbers in formulas.
- **Formula Error Prevention**: Verify all cell references are correct. Test with edge cases (zero values, negative numbers).
- **Use Formulas, Not Hardcoded Values**: Always use Excel formulas instead of calculating values in Python and hardcoding them. This ensures the spreadsheet remains dynamic and updateable.
- **Dynamic Links**: Link sheets together dynamically using standard formulas (e.g. `=SUM(...)`, `=COUNTA(...)`).
