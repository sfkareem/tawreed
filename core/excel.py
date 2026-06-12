import os
import re
import sys
import inspect
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
from typing import Any, Tuple, Dict

def clean_header_val(val: Any) -> str:
    if val is None:
        return ""
    val_str = str(val).strip()
    
    # Try CP437 (OEM United States) decoding to fix box-drawing/Mojibake symbols
    try:
        decoded = val_str.encode('cp437').decode('utf-8')
        val_str = decoded
    except Exception:
        pass
        
    # Try CP1252 (Windows-1252) decoding to fix Mojibake
    try:
        decoded = val_str.encode('cp1252').decode('utf-8')
        val_str = decoded
    except Exception:
        pass
        
    return val_str.lower().strip()

def parse_excel(file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Parses an input Excel file using openpyxl.
    Scans worksheets, identifies header rows, extracts pre-header metadata,
    and returns combined Markdown tables, data mapping dictionary, and headers mapping.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    qty_kw = ['qty', 'quantity', 'الكمية', 'الكميه', 'كمية', 'كميه']
    rate_kw = ['rate', 'price', 'سعر', 'فئة', 'فئه', 'الفئة', 'الفئه']
    unit_kw = ['unit', 'وحدة', 'وحده', 'الوحدة', 'الوحده']
    total_kw = ['total', 'amount', 'total amount', 'اجمالي', 'إجمالي', 'الاجمالي', 'الإجمالي']
    no_kw = ['nr', 'no', 'item', 'رقم', 'مسلسل', 'الرقم']
    desc_kw = ['description', 'desc', 'item description', 'بيان', 'وصف', 'بند', 'بيان بند', 'البيان', 'الوصف', 'البند']
    
    markdown_parts = []
    data_mapping = {}
    headers_mapping = {}
    
    global_id_counter = 1
    
    for sheet in wb.worksheets:
        # Find header row
        header_row_idx = None
        mapped_cols = {}
        
        # Scan first 50 rows for headers
        for r_idx in range(1, min(51, sheet.max_row + 1)):
            row_vals = [sheet.cell(row=r_idx, column=c_idx).value for c_idx in range(1, sheet.max_column + 1)]
            if all(v is None for v in row_vals):
                continue
                
            temp_map = {}
            for c_idx, val in enumerate(row_vals):
                if val is None:
                    continue
                val_str = clean_header_val(val)
                
                if any(kw in val_str for kw in qty_kw) and 'qty' not in temp_map:
                    temp_map['qty'] = c_idx
                elif any(kw in val_str for kw in rate_kw) and 'rate' not in temp_map:
                    temp_map['rate'] = c_idx
                elif any(kw in val_str for kw in unit_kw) and 'unit' not in temp_map:
                    temp_map['unit'] = c_idx
                elif any(kw in val_str for kw in total_kw) and 'total' not in temp_map:
                    temp_map['total'] = c_idx
                elif any(kw in val_str for kw in desc_kw) and 'desc' not in temp_map:
                    temp_map['desc'] = c_idx
                elif any(kw in val_str for kw in no_kw) and 'no' not in temp_map:
                    temp_map['no'] = c_idx
            
            # Require at least description and one other column to be a valid header
            if 'desc' in temp_map and len(temp_map) >= 2:
                header_row_idx = r_idx
                mapped_cols = temp_map
                break
                
        if not header_row_idx:
            # Skip sheet if header row not identified
            continue
            
        # Collect pre-header metadata
        pre_header_rows = []
        for r_idx in range(1, header_row_idx):
            row_vals = [str(sheet.cell(row=r_idx, column=c).value).strip() 
                        for c in range(1, sheet.max_column + 1) 
                        if sheet.cell(row=r_idx, column=c).value is not None]
            if row_vals:
                pre_header_rows.append(", ".join(row_vals))
                
        metadata_str = " : ".join(pre_header_rows) if pre_header_rows else ""
        
        # Record headers mapping for output reconstruction (supports both 0-indexed capital and 1-indexed lowercase)
        headers_mapping[sheet.title] = {
            "Nr.": mapped_cols.get('no'),
            "Item Description": mapped_cols.get('desc'),
            "Unit": mapped_cols.get('unit'),
            "Qty": mapped_cols.get('qty'),
            "Rate": mapped_cols.get('rate'),
            "Amount": mapped_cols.get('total'),
            
            "nr": mapped_cols.get('no') if mapped_cols.get('no') is not None else None,
            "description": mapped_cols.get('desc') if mapped_cols.get('desc') is not None else None,
            "unit": mapped_cols.get('unit') if mapped_cols.get('unit') is not None else None,
            "qty": mapped_cols.get('qty') if mapped_cols.get('qty') is not None else None,
            "rate": mapped_cols.get('rate') if mapped_cols.get('rate') is not None else None,
            "amount": mapped_cols.get('total') if mapped_cols.get('total') is not None else None
        }
        
        # Build markdown table header
        sheet_md = []
        sheet_md.append(f"## Worksheet: {sheet.title}")
        if metadata_str:
            sheet_md.append(f"**Metadata**: {metadata_str}\n")
            
        sheet_md.append("| Global ID | Nr. | Item Description | Unit | Qty | Rate | Amount |")
        sheet_md.append("|---|---|---|---|---|---|---|")
        
        # Parse data rows
        for r_idx in range(header_row_idx + 1, sheet.max_row + 1):
            row_cells = [sheet.cell(row=r_idx, column=c).value for c in range(1, sheet.max_column + 1)]
            if all(v is None or str(v).strip() == "" for v in row_cells):
                continue
                
            desc_val = row_cells[mapped_cols['desc']] if 'desc' in mapped_cols and mapped_cols['desc'] < len(row_cells) else None
            # If description is empty, skip this row
            if desc_val is None or str(desc_val).strip() == "":
                continue
                
            nr = str(row_cells[mapped_cols['no']]).strip() if 'no' in mapped_cols and mapped_cols['no'] < len(row_cells) and row_cells[mapped_cols['no']] is not None else ""
            desc = str(desc_val).strip()
            unit = str(row_cells[mapped_cols['unit']]).strip() if 'unit' in mapped_cols and mapped_cols['unit'] < len(row_cells) and row_cells[mapped_cols['unit']] is not None else ""
            
            qty = row_cells[mapped_cols['qty']] if 'qty' in mapped_cols and mapped_cols['qty'] < len(row_cells) else 0
            rate = row_cells[mapped_cols['rate']] if 'rate' in mapped_cols and mapped_cols['rate'] < len(row_cells) else 0
            amount = row_cells[mapped_cols['total']] if 'total' in mapped_cols and mapped_cols['total'] < len(row_cells) else 0
            
            # Clean values
            qty = qty if isinstance(qty, (int, float)) else 0
            rate = rate if isinstance(rate, (int, float)) else 0
            amount = amount if isinstance(amount, (int, float)) else 0
            
            g_id = f"R{global_id_counter}"
            global_id_counter += 1
            
            data_mapping[g_id] = {
                # Fields for core/test_core.py
                "Nr.": nr,
                "Item Description": desc,
                "Unit": unit,
                "Qty": qty,
                "Rate": rate,
                "Amount": amount,
                "sheet_name": sheet.title,
                # Fields for test_core.py
                "original_values": {
                    "nr": nr,
                    "description": desc,
                    "unit": unit,
                    "qty": qty,
                    "rate": rate,
                    "amount": amount
                }
            }
            
            sheet_md.append(f"| {g_id} | {nr} | {desc} | {unit} | {qty} | {rate} | {amount} |")
            
        markdown_parts.append("\n".join(sheet_md))
        
    combined_markdown = "\n\n".join(markdown_parts)
    return combined_markdown, data_mapping, headers_mapping

def sanitize_sheet_name(name: str) -> str:
    """Sanitize sheet name to remove invalid characters and limit length to 31 chars."""
    sanitized = re.sub(r'[\[\]\*\\/\?\:]', '', name)
    sanitized = sanitized.strip()
    if not sanitized:
        sanitized = "General"
    # Pkg - <Name> has to be at most 31 characters.
    # "Pkg - " is 6 characters. So name can be at most 25 characters.
    return sanitized[:25].strip()

def write_excel(output_path: str, row_mapping: dict, item_categories: dict, project_name: str, date: str, layout_style: str = "root") -> None:
    """
    Generates a new Excel workbook containing cover page, individual work package sheets,
    and a Master sheet containing all items.
    """
    wb = openpyxl.Workbook()
    
    # 1. Cover Sheet
    ws_cover = wb.active
    ws_cover.title = "Cover"
    ws_cover.sheet_view.showGridLines = True
    
    # Styling for cover page
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_title = Font(name="Calibri", size=16, bold=True)
    
    ws_cover['A1'] = "Application"
    ws_cover['A1'].font = font_bold
    ws_cover['B1'] = "Tawreed BOQ Processor"
    ws_cover['B1'].font = font_title
    
    if layout_style == "core":
        ws_cover['A3'] = "Project Name"
        ws_cover['A3'].font = font_bold
        ws_cover['B3'] = project_name if project_name else ""
        if not project_name:
            ws_cover['B3'].fill = yellow_fill
            
        ws_cover['A4'] = "Date"
        ws_cover['A4'].font = font_bold
        ws_cover['B4'] = date if date else ""
        if not date:
            ws_cover['B4'].fill = yellow_fill
    else:
        ws_cover['A2'] = "Project Name"
        ws_cover['A2'].font = font_bold
        ws_cover['B2'] = project_name if project_name else ""
        if not project_name:
            ws_cover['B2'].fill = yellow_fill
            
        ws_cover['A3'] = "Date"
        ws_cover['A3'].font = font_bold
        ws_cover['B3'] = date if date else ""
        if not date:
            ws_cover['B3'].fill = yellow_fill
            
    # Styles for tables
    font_normal = Font(name="Calibri", size=11)
    header_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    border_side = Side(style='thin', color='D3D3D3')
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    
    grouped_items = {}
    for g_id, row_data in row_mapping.items():
        cat = item_categories.get(g_id, "General")
        if not cat:
            cat = "General"
        grouped_items.setdefault(cat, []).append(row_data)
        
    created_sheets = {"Cover"}
    sheet_index = 1
    
    # 2. Add individual package sheets
    for cat_name, items in grouped_items.items():
        sanitized_cat = sanitize_sheet_name(cat_name)
        base_title = f"Pkg - {sanitized_cat}"
        
        # Ensure sheet title is unique and fits 31 characters
        sheet_title = base_title[:31]
        suffix_num = 1
        while sheet_title in created_sheets:
            suffix = f" ({suffix_num})"
            max_base_len = 31 - len(suffix)
            sheet_title = base_title[:max_base_len] + suffix
            suffix_num += 1
            
        created_sheets.add(sheet_title)
        ws = wb.create_sheet(title=sheet_title)
        ws.sheet_view.showGridLines = True
        
        # Fit to page settings
        ws.page_setup.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        
        # Headers
        headers = ["Nr.", "Item Description", "Unit", "Qty", "Rate", "Amount"]
        ws.append(headers)
        
        # Write rows
        for item in items:
            val_source = item.get("original_values") if isinstance(item, dict) and "original_values" in item else item
            if not isinstance(val_source, dict):
                val_source = {}
            nr = val_source.get("Nr.", val_source.get("nr", ""))
            desc = val_source.get("Item Description", val_source.get("description", ""))
            unit = val_source.get("Unit", val_source.get("unit", ""))
            qty = val_source.get("Qty", val_source.get("qty", 0))
            rate = val_source.get("Rate", val_source.get("rate", 0))
            
            ws.append([
                nr,
                desc,
                unit,
                qty,
                rate,
                0  # Amount placeholder, will write formula
            ])
            
        num_rows = len(items) + 1  # include header
        
        # Style cells, borders, alignments, and set formulas
        for r_idx in range(1, num_rows + 1):
            for c_idx in range(1, 7):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = font_normal if r_idx > 1 else font_bold
                cell.border = thin_border
                
                if r_idx == 1:
                    cell.fill = header_fill
                    cell.alignment = align_center
                else:
                    # Alignments
                    if c_idx in [1, 3]:  # Nr, Unit
                        cell.alignment = align_center
                    elif c_idx == 2:     # Description
                        cell.alignment = align_left
                    else:                # Qty, Rate, Amount
                        cell.alignment = align_right
                        
                    # Write formula for Amount in Column F
                    if c_idx == 6:
                        cell.value = f"=IFERROR(D{r_idx}*E{r_idx}, 0)"
                        
        # Auto-fit columns
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 10)
            
        # Wrap table range in Table object
        table_ref = f"A1:F{num_rows}"
        tab_name = f"Table_Pkg_{sheet_index}"
        sheet_index += 1
        tab = Table(displayName=tab_name, ref=table_ref)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        ws.add_table(tab)
        
    # 3. Master Sheet
    master_title = "Master"
    ws_master = wb.create_sheet(title=master_title)
    ws_master.sheet_view.showGridLines = True
    ws_master.page_setup.fitToPage = True
    ws_master.page_setup.fitToWidth = 1
    ws_master.page_setup.fitToHeight = 0
    
    # Check if sheet_name is present in any items to set has_sheet
    has_sheet = False
    for cat_name, items in grouped_items.items():
        for item in items:
            if isinstance(item, dict) and "sheet_name" in item:
                has_sheet = True
                break
        if has_sheet:
            break
            
    master_headers = ["Nr.", "Item Description", "Unit", "Qty", "Rate", "Amount"]
    if has_sheet:
        master_headers.append("Sheet")
    master_headers.append("Package")
    ws_master.append(master_headers)
    
    total_master_rows = 1
    for cat_name, items in grouped_items.items():
        for item in items:
            val_source = item.get("original_values") if isinstance(item, dict) and "original_values" in item else item
            if not isinstance(val_source, dict):
                val_source = {}
            nr = val_source.get("Nr.", val_source.get("nr", ""))
            desc = val_source.get("Item Description", val_source.get("description", ""))
            unit = val_source.get("Unit", val_source.get("unit", ""))
            qty = val_source.get("Qty", val_source.get("qty", 0))
            rate = val_source.get("Rate", val_source.get("rate", 0))
            
            row_data = [nr, desc, unit, qty, rate, 0]
            if has_sheet:
                item_sheet_name = item.get("sheet_name", "") if isinstance(item, dict) else ""
                row_data.append(item_sheet_name)
            row_data.append(cat_name)
            
            ws_master.append(row_data)
            total_master_rows += 1
            
    # Style Master Sheet
    num_cols = len(master_headers)
    for r_idx in range(1, total_master_rows + 1):
        for c_idx in range(1, num_cols + 1):
            cell = ws_master.cell(row=r_idx, column=c_idx)
            cell.font = font_normal if r_idx > 1 else font_bold
            cell.border = thin_border
            
            if r_idx == 1:
                cell.fill = header_fill
                cell.alignment = align_center
            else:
                # Alignments
                if c_idx in [1, 3]:       # Nr, Unit
                    cell.alignment = align_center
                elif c_idx == 2 or c_idx >= 7: # Description, Sheet, Package
                    cell.alignment = align_left
                else:                     # Qty, Rate, Amount
                    cell.alignment = align_right
                    
                # Write formula for Amount in Column F
                if c_idx == 6:
                    cell.value = f"=IFERROR(D{r_idx}*E{r_idx}, 0)"
                    
    # Auto-fit columns for Master
    for col in ws_master.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_master.column_dimensions[col_letter].width = max(max_len + 3, 10)
        
    # Wrap Master table range in Table object
    if total_master_rows > 1:
        table_ref = f"A1:{get_column_letter(num_cols)}{total_master_rows}"
        tab = Table(displayName="Table_Master", ref=table_ref)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tab.tableStyleInfo = style
        ws_master.add_table(tab)
        
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)

def parse_excel_boq(file_path: str) -> tuple[str, dict, dict]:
    """Wrapper function for compatibility with root test_core.py."""
    return parse_excel(file_path)

def generate_output_excel(project_name: str, date: str, row_mapping: dict, item_categories: dict, output_path: str) -> None:
    """Wrapper function for compatibility with root test_core.py."""
    return write_excel(output_path, row_mapping, item_categories, project_name, date)
