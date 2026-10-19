import csv
import io
import os
import zipfile
from xml.sax.saxutils import escape

from seed_data import SEED_CSV

COLUMNS = ["RecordType", "Name", "Date", "Pending", "Settled", "Label", "SessionsPerWeek", "Level", "Term", "OriginalTerm", "PendingSessions", "Note", "Labels", "ClassDays"]


def csv_rows(text):
    return list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))


async def data_file(page):
    if page.web:
        return None
    import flet as ft
    folder = await ft.StoragePaths().get_application_documents_directory()
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "combined_data.csv")


async def load_records(page):
    path = await data_file(page)
    if path is None:
        import flet as ft
        prefs = ft.SharedPreferences()
        text = await prefs.get("attendance_csv")
        if not text:
            text = SEED_CSV
            await prefs.set("attendance_csv", text)
        return csv_rows(text)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            f.write(SEED_CSV)
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


async def save_records(page, rows):
    path = await data_file(page)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in COLUMNS})
    text = stream.getvalue()
    if path is None:
        import flet as ft
        await ft.SharedPreferences().set("attendance_csv", text)
    else:
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8-sig", newline="") as f:
            f.write(text)
        os.replace(temporary, path)


def blank_record(record_type, **values):
    row = {key: "" for key in COLUMNS}
    row["RecordType"] = record_type
    row.update(values)
    return row


def xlsx_bytes(rows):
    """Create a basic standards-compliant one-sheet XLSX without native deps."""
    def col_name(n):
        result = ""
        while n:
            n, r = divmod(n - 1, 26)
            result = chr(65 + r) + result
        return result

    all_rows = [COLUMNS] + [[str(row.get(k, "") or "") for k in COLUMNS] for row in rows]
    sheet_rows = []
    for r_idx, row in enumerate(all_rows, 1):
        cells = []
        for c_idx, value in enumerate(row, 1):
            ref = f"{col_name(c_idx)}{r_idx}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>')
        sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    sheet = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + "".join(sheet_rows) + "</sheetData></worksheet>"
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Attendance Data" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()
