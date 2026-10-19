from storage import blank_record

DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
FA_DAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
DAY_FA = dict(zip(DAYS, FA_DAYS))
DAY_EN = dict(zip(FA_DAYS, DAYS))


def as_int(value, default=0):
    try:
        return int(float(str(value or "").strip()))
    except (ValueError, TypeError):
        return default


def truth(value):
    return str(value).strip().lower() in ("true", "1", "yes")


def parse_records(rows):
    students, attendance, labels = {}, [], []
    levels = ["Beginner", "Intermediate", "Advanced"]
    for row in rows:
        kind = (row.get("RecordType") or "").strip().lower()
        if kind == "student" and row.get("Name"):
            name = row["Name"].strip()
            student_labels = [x.strip() for x in (row.get("Labels") or "").split(",") if x.strip()]
            student = {
                "sessions_per_week": max(1, as_int(row.get("SessionsPerWeek"), 1)),
                "level": (row.get("Level") or "Beginner").strip(),
                "term": as_int(row.get("Term")),
                "original_term": as_int(row.get("OriginalTerm")),
                "pending_sessions": as_int(row.get("PendingSessions")),
                "note": row.get("Note") or "",
                "labels": student_labels,
                "class_days": [x.strip() for x in (row.get("ClassDays") or "").split(",") if x.strip()],
            }
            students[name] = student
            if student["level"] and student["level"] not in levels:
                levels.append(student["level"])
        elif kind == "attendance" and row.get("Name"):
            attendance.append({"Name": row.get("Name", ""), "Date": row.get("Date", ""), "Pending": truth(row.get("Pending")), "Settled": truth(row.get("Settled"))})
        elif kind == "label" and (row.get("Label") or "").strip():
            label = row["Label"].strip()
            if label not in labels:
                labels.append(label)
    return students, attendance, labels, levels


def serialize(students, attendance, labels):
    rows = []
    for name, student in students.items():
        rows.append(blank_record("student", Name=name,
            SessionsPerWeek=student["sessions_per_week"], Level=student["level"],
            Term=student["term"], OriginalTerm=student["original_term"],
            PendingSessions=student["pending_sessions"], Note=student["note"],
            Labels=",".join(student["labels"]), ClassDays=",".join(student["class_days"])))
    for item in attendance:
        rows.append(blank_record("attendance", Name=item["Name"], Date=item["Date"],
            Pending=str(item["Pending"]), Settled=str(item["Settled"])))
    for label in labels:
        rows.append(blank_record("label", Label=label))
    return rows
