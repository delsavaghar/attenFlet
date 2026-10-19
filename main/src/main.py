import asyncio
import logging
import re
from datetime import date, datetime

import flet as ft

from attendance import DAYS, DAY_EN, DAY_FA, as_int, parse_records, serialize
from storage import load_records, save_records, xlsx_bytes

LOG_LEVEL = logging.INFO
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.attendance")
log.setLevel(LOG_LEVEL)

PALETTE = {"main": "#CAD2C5", "green": "#84A98C", "light": "#F8F9F7", "accent": "#52796F", "deep": "#354F52", "ink": "#2F3E46"}

T = {
"en": {"app":"Attendance Manager","home":"Students","calendar":"Calendar","add":"Add student","reports":"Reports","settings":"Settings","help":"Help","all":"All","search":"Search students...","name":"Name","sessions":"Sessions/week","level":"Level","term":"Sessions in term","note":"Note","labels":"Labels","days":"Class days","attendance":"Attendance","edit":"Edit","delete":"Delete","back":"Back","save":"Save","cancel":"Cancel","confirm":"Confirm","today":"Today","pick_date":"Pick date","date":"Attendance date","question":"Did {name} attend?","students":"Students","renew":"Renew term","remaining":"{name}: {count} sessions left","no_students":"No students found","no_attendance":"No attendance history","reports_title":"Sessions remaining","language":"Language","export":"Export Excel","help_title":"Help","help_text":"Add students and set their weekly class days. Record attendance for today or another date. Each attendance uses one remaining session; attendance after a term ends is tracked as pending. Reports let you renew a term, the calendar shows scheduled weekdays, and Settings changes language or exports the data.","levels":"Manage levels","new_level":"New level","add_level":"Add level","rename":"Rename","level_delete":"Delete level","delete_student":"Delete this student and their attendance?","delete_attendance":"Delete this attendance record?","add_ok":"Student added.","edit_ok":"Student updated.","attendance_ok":"Attendance recorded.","renew_ok":"Term renewed.","save_ok":"Saved","required":"Fill in the name, sessions, level and term.","invalid":"Check the name and numeric fields.","duplicate":"A student with that name already exists.","choose_days":"Select one class day for each weekly session.","select_date":"Choose Today or a date first.","no_labels":"No saved labels yet","filter":"Filter labels","label_new":"New label","label_rename":"Rename label","label_delete":"Delete label","zero":"Term ended","today_count":"Classes today","total":"Total students","weekdays":"Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday"},
"fa": {"app":"مدیریت حضور و غیاب","home":"دانش‌آموزان","calendar":"تقویم","add":"افزودن دانش‌آموز","reports":"گزارش‌ها","settings":"تنظیمات","help":"راهنما","all":"همه","search":"جستجوی دانش‌آموز...","name":"نام","sessions":"جلسه در هفته","level":"سطح","term":"جلسات ترم","note":"یادداشت","labels":"برچسب‌ها","days":"روزهای کلاس","attendance":"حضور و غیاب","edit":"ویرایش","delete":"حذف","back":"بازگشت","save":"ذخیره","cancel":"انصراف","confirm":"تأیید","today":"امروز","pick_date":"انتخاب تاریخ","date":"تاریخ حضور","question":"{name} حضور داشت؟","students":"دانش‌آموزان","renew":"تمدید ترم","remaining":"{name}: {count} جلسه باقی‌مانده","no_students":"دانش‌آموزی پیدا نشد","no_attendance":"سابقه‌ای نیست","reports_title":"جلسات باقی‌مانده","language":"زبان","export":"خروجی اکسل","help_title":"راهنما","help_text":"دانش‌آموزان را اضافه و روزهای کلاس هفتگی را تعیین کنید. حضور امروز یا تاریخ دیگری را ثبت کنید. با هر حضور یک جلسه از باقیمانده کم می‌شود؛ پس از پایان ترم حضورها به‌صورت معوق ثبت می‌شوند. از گزارش‌ها برای تمدید ترم، از تقویم برای دیدن روزهای کلاس و از تنظیمات برای تغییر زبان یا خروجی داده‌ها استفاده کنید.","levels":"مدیریت سطوح","new_level":"سطح جدید","add_level":"افزودن سطح","rename":"تغییر نام","level_delete":"حذف سطح","delete_student":"این دانش‌آموز و حضورهایش حذف شود؟","delete_attendance":"این حضور حذف شود؟","add_ok":"دانش‌آموز اضافه شد.","edit_ok":"دانش‌آموز ویرایش شد.","attendance_ok":"حضور ثبت شد.","renew_ok":"ترم تمدید شد.","save_ok":"ذخیره شد","required":"نام، جلسات، سطح و ترم را وارد کنید.","invalid":"نام یا فیلد عددی را بررسی کنید.","duplicate":"دانش‌آموزی با این نام وجود دارد.","choose_days":"برای هر جلسه هفتگی یک روز کلاس انتخاب کنید.","select_date":"ابتدا امروز یا یک تاریخ را انتخاب کنید.","no_labels":"برچسبی ثبت نشده","filter":"فیلتر برچسب‌ها","label_new":"برچسب جدید","label_rename":"تغییر نام برچسب","label_delete":"حذف برچسب","zero":"ترم پایان‌یافته","today_count":"کلاس‌های امروز","total":"تعداد کل دانش‌آموزان","weekdays":"شنبه,یکشنبه,دوشنبه,سه‌شنبه,چهارشنبه,پنجشنبه,جمعه"}}

class AttendanceApp:
    def __init__(self, page):
        self.page = page
        self.lang = "fa"
        self.students = {}
        self.attendance = []
        self.labels = []
        self.levels = ["Beginner", "Intermediate", "Advanced"]
        self.screen = "home"
        self.selected = None
        self.filter_label = None
        self.query = ""
        self.attendance_name = None
        self.attendance_query = ""
        self.attendance_date_text = ""
        self.attendance_today = False
        self.level_return = "add"
        self.day_values = []

    def tr(self, key, **kwargs):
        return T[self.lang].get(key, key).format(**kwargs)

    def rtl_day(self, day):
        return DAY_FA.get(day, day) if self.lang == "fa" else day

    async def persist(self):
        await save_records(self.page, serialize(self.students, self.attendance, self.labels))

    def notify(self, message):
        self.page.show_dialog(ft.AlertDialog(content=ft.Text(message), actions=[ft.TextButton(content="OK", on_click=lambda: self.page.pop_dialog())]))

    def confirm(self, message, callback):
        dialog = ft.AlertDialog(content=ft.Text(message), actions=[
            ft.TextButton(content=self.tr("confirm"), on_click=lambda: (self.page.pop_dialog(), callback())),
            ft.TextButton(content=self.tr("cancel"), on_click=lambda: self.page.pop_dialog()),
        ])
        self.page.show_dialog(dialog)

    def set_screen(self, screen):
        self.screen = screen
        self.render()

    def base(self, title, body, show_back=True):
        self.page.controls.clear()
        self.page.title = self.tr("app")
        self.page.bgcolor = PALETTE["main"]
        self.page.padding = 12
        self.page.rtl = self.lang == "fa"
        def go_back():
            self.set_screen(self.level_return if self.screen == "levels" else "home")
        header = ft.Row(controls=[ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=PALETTE["deep"], expand=True)] + ([ft.TextButton(content=self.tr("back"), on_click=go_back)] if show_back and self.screen != "home" else []))
        self.page.add(ft.Column(expand=True, spacing=10, controls=[header, body]))
        self.page.update()

    def btn(self, text, fn, color=None):
        return ft.Button(content=text, on_click=fn, bgcolor=color or PALETTE["green"], color=PALETTE["ink"])

    def render(self):
        if self.screen == "home": self.home()
        elif self.screen == "add": self.student_form(False)
        elif self.screen == "edit": self.student_form(True)
        elif self.screen == "reports": self.reports()
        elif self.screen == "calendar": self.calendar()
        elif self.screen == "attendance": self.attendance_screen()
        elif self.screen == "settings": self.settings()
        elif self.screen == "help": self.help_screen()
        elif self.screen == "levels": self.level_screen()

    def home(self):
        today = date.today().weekday()
        today_en = DAYS[(today + 2) % 7]
        class_count = sum(today_en in s["class_days"] for s in self.students.values())
        stats = ft.Row(wrap=True, controls=[ft.Text(f"{self.tr('total')}: {len(self.students)}"), ft.Text(f"{self.tr('today_count')}: {class_count}"), ft.Text(f"{self.tr('zero')}: {sum(s['term'] <= 0 for s in self.students.values())}")])
        nav = ft.Row(wrap=True, controls=[self.btn(self.tr(x), lambda e, x=x: self.set_screen(x)) for x in ("calendar", "add", "reports", "settings", "help")])
        search = ft.TextField(label=self.tr("search"), value=self.query, on_change=self.on_search)
        chip_controls = [self.btn(self.tr("all"), lambda: self.choose_filter(None)), self.btn("+", self.add_label_dialog)]
        for label in self.labels:
            chip_controls.extend([self.btn(label, lambda e, label=label: self.choose_filter(label)), self.btn("⋮", lambda e, label=label: self.label_menu(label))])
        chips = ft.Row(scroll=ft.ScrollMode.AUTO, controls=chip_controls)
        displayed = sorted(self.students)
        if self.filter_label:
            displayed = [n for n in displayed if self.filter_label in self.students[n]["labels"]]
        if self.query.strip():
            displayed = [n for n in displayed if self.query.casefold() in n.casefold()]
        items = []
        for name in displayed:
            s = self.students[name]
            summary = f"{name}  •  {s['sessions_per_week']}/week  •  {s['level']}  •  {s['term']}/{s['original_term']}  •  {s['note']}  •  {', '.join(s['labels'])}"
            items.append(ft.Card(content=ft.Column(controls=[ft.Text(summary, selectable=True), ft.Row(wrap=True, controls=[self.btn(self.tr("attendance"), lambda e, n=name: self.open_attendance(n)), self.btn(self.tr("edit"), lambda e, n=name: self.edit_student(n)), self.btn(self.tr("delete"), lambda e, n=name: self.delete_student(n), PALETTE["main"])])])) )
        if not items: items = [ft.Text(self.tr("no_students"))]
        self.base(self.tr("app"), ft.Column(expand=True, controls=[nav, stats, search, chips, ft.ListView(expand=True, spacing=6, controls=items)]), False)

    def on_search(self, e):
        self.query = e.control.value or ""
        self.home()

    def choose_filter(self, label):
        self.filter_label = label
        self.home()

    def add_label_dialog(self):
        field = ft.TextField(label=self.tr("label_new"))
        def add():
            label = (field.value or "").strip()
            if label and label not in self.labels:
                self.labels.append(label)
                asyncio.create_task(self.persist())
            self.page.pop_dialog(); self.home()
        dialog = ft.AlertDialog(title=ft.Text(self.tr("label_new")), content=field, actions=[ft.TextButton(content=self.tr("add"), on_click=lambda: add()), ft.TextButton(content=self.tr("cancel"), on_click=lambda: self.page.pop_dialog())])
        self.page.show_dialog(dialog)

    def label_menu(self, label):
        field = ft.TextField(label=self.tr("label_rename"), value=label)
        def rename():
            new = (field.value or "").strip()
            if new and new != label and new not in self.labels:
                self.labels[self.labels.index(label)] = new
                for student in self.students.values():
                    student["labels"] = [new if x == label else x for x in student["labels"]]
                asyncio.create_task(self.persist())
            self.page.pop_dialog(); self.home()
        def remove():
            self.labels.remove(label)
            for student in self.students.values():
                student["labels"] = [x for x in student["labels"] if x != label]
            asyncio.create_task(self.persist()); self.page.pop_dialog(); self.home()
        self.page.show_dialog(ft.AlertDialog(title=ft.Text(label), content=field, actions=[ft.TextButton(content=self.tr("rename"), on_click=lambda: rename()), ft.TextButton(content=self.tr("delete"), on_click=lambda: (self.page.pop_dialog(), self.confirm(self.tr("label_delete"), remove))), ft.TextButton(content=self.tr("cancel"), on_click=lambda: self.page.pop_dialog())]))

    def student_form(self, editing):
        original = self.students.get(self.selected, {}) if editing else {}
        saved = getattr(self, "form_state", None) if getattr(self, "form_editing", None) == editing else None
        name = ft.TextField(label=self.tr("name"), value=(saved[0] if saved else (self.selected if editing else "")))
        sessions = ft.Dropdown(label=self.tr("sessions"), value=str(saved[1] if saved else original.get("sessions_per_week", 1)), options=[ft.DropdownOption(key=str(n), text=str(n)) for n in range(1, 8)])
        term = ft.TextField(label=self.tr("term"), value=(saved[2] if saved else str(original.get("term", ""))), keyboard_type=ft.KeyboardType.NUMBER)
        level = ft.Dropdown(label=self.tr("level"), value=(saved[3] if saved else original.get("level", self.levels[0] if self.levels else "Beginner")), options=[ft.DropdownOption(key=x, text=x) for x in self.levels])
        note = ft.TextField(label=self.tr("note"), value=(saved[4] if saved else original.get("note", "")), multiline=True, min_lines=1, max_lines=3)
        chosen = set(saved[5] if saved else original.get("labels", []))
        checks = {x: ft.Checkbox(label=x, value=x in chosen) for x in self.labels}
        days = list(saved[6] if saved else original.get("class_days", []))
        day_fields = []
        for i in range(int(sessions.value or 1)):
            default = days[i] if i < len(days) else ""
            day_fields.append(ft.Dropdown(label=f"{self.tr('days')} {i+1}", value=default if default in DAYS else None, options=[ft.DropdownOption(key=d, text=self.rtl_day(d)) for d in DAYS]))
        def count_changed(e):
            try:
                n = int(e.control.value)
                if not 1 <= n <= 7: return
                current = [f.value for f in day_fields]
                day_fields.clear()
                for i in range(n):
                    default = current[i] if i < len(current) else (days[i] if i < len(days) else None)
                    day_fields.append(ft.Dropdown(label=f"{self.tr('days')} {i+1}", value=default if default in DAYS else None, options=[ft.DropdownOption(key=d, text=self.rtl_day(d)) for d in DAYS]))
                self.form_state = (name.value, sessions.value, term.value, level.value, note.value, [x for x, c in checks.items() if c.value], [f.value for f in day_fields])
                self.form_editing = editing
                self.student_form(editing)
            except (ValueError, TypeError): pass
        sessions.on_select = count_changed
        self.form_state = (name.value, sessions.value, term.value, level.value, note.value, [x for x, c in checks.items() if c.value], days)
        self.form_editing = editing
        def save():
            n = (name.value or "").strip()
            try:
                count, term_count = int(sessions.value), int((term.value or "").strip())
            except (ValueError, TypeError):
                self.notify(self.tr("invalid")); return
            if not n or not level.value or not term.value:
                self.notify(self.tr("required")); return
            if not re.fullmatch(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*", n, flags=re.UNICODE):
                self.notify(self.tr("invalid")); return
            if n != self.selected and n in self.students:
                self.notify(self.tr("duplicate")); return
            if len(day_fields) != count or any(not f.value for f in day_fields):
                self.notify(self.tr("choose_days")); return
            previous = original
            self.students.pop(self.selected, None) if editing else None
            self.students[n] = {"sessions_per_week": count, "level": level.value, "term": term_count,
                "original_term": previous.get("original_term", term_count), "pending_sessions": previous.get("pending_sessions", 0),
                "note": note.value or "", "labels": [x for x, c in checks.items() if c.value], "class_days": [f.value for f in day_fields]}
            asyncio.create_task(self.persist())
            self.notify(self.tr("edit_ok" if editing else "add_ok")); self.set_screen("home")
        def open_levels():
            self.level_return = "edit" if editing else "add"
            self.form_state = (name.value, sessions.value, term.value, level.value, note.value, [x for x, c in checks.items() if c.value], [f.value for f in day_fields])
            self.form_editing = editing
            self.set_screen("levels")
        form_controls = [name, ft.Row(wrap=True, controls=[sessions, term]), ft.Row(wrap=True, controls=[level, self.btn(self.tr("levels"), open_levels)]), note, ft.Text(self.tr("labels")), ft.Row(wrap=True, controls=list(checks.values())), ft.Text(self.tr("days")), *day_fields, self.btn(self.tr("save"), save, PALETTE["accent"])]
        self.base(self.tr("edit" if editing else "add"), ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, controls=form_controls))

    def edit_student(self, name):
        self.selected = name
        self.set_screen("edit")

    def delete_student(self, name):
        def remove():
            self.students.pop(name, None)
            self.attendance = [a for a in self.attendance if a["Name"] != name]
            asyncio.create_task(self.persist()); self.home()
        self.confirm(self.tr("delete_student"), remove)

    def reports_search_changed(self, e):
        self.report_query = e.control.value or ""
        self.reports()

    def reports(self):
        query = ft.TextField(label=self.tr("search"), value=getattr(self, "report_query", ""), on_change=self.reports_search_changed)
        entries = []
        for name, student in sorted(self.students.items(), key=lambda pair: (pair[1]["term"], pair[0])):
            if query.value and query.value.casefold() not in name.casefold(): continue
            row = ft.Row(controls=[ft.Text(self.tr("remaining", name=name, count=student["term"]), expand=True), self.btn(self.tr("renew"), lambda e, n=name: self.renew(n)) if student["term"] <= 0 else ft.Text("")])
            entries.append(row)
        self.base(self.tr("reports_title"), ft.Column(expand=True, controls=[query, ft.ListView(expand=True, controls=entries or [ft.Text(self.tr("no_students"))])]))

    def renew(self, name):
        def done():
            student = self.students[name]
            student["term"] = student["original_term"] - student["pending_sessions"]
            student["pending_sessions"] = 0
            for item in self.attendance:
                if item["Name"] == name and item["Pending"] and not item["Settled"]: item["Settled"] = True
            asyncio.create_task(self.persist()); self.reports()
        self.confirm(self.tr("renew"), done)

    def calendar_search_changed(self, e):
        self.calendar_query = e.control.value or ""
        self.calendar()

    def calendar(self):
        query = ft.TextField(label=self.tr("search"), value=getattr(self, "calendar_query", ""), on_change=self.calendar_search_changed)
        headers = [ft.Text(self.tr("name"), weight=ft.FontWeight.BOLD)] + [ft.Text(self.rtl_day(d), weight=ft.FontWeight.BOLD) for d in DAYS]
        rows = [ft.Row(scroll=ft.ScrollMode.AUTO, controls=headers)]
        for name, student in sorted(self.students.items()):
            if query.value and query.value.casefold() not in name.casefold(): continue
            rows.append(ft.Row(scroll=ft.ScrollMode.AUTO, controls=[ft.Text(name, width=130)] + [ft.Text("✓" if d in student["class_days"] else "", width=65) for d in DAYS]))
        self.base(self.tr("calendar"), ft.Column(expand=True, controls=[query, ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=rows)]))

    def open_attendance(self, name):
        self.attendance_name = name
        self.set_screen("attendance")

    def attendance_screen(self):
        name = self.attendance_name
        picker_value = {"value": ""}
        date_field = ft.TextField(label=self.tr("date"), read_only=True, value="")
        today_check = ft.Checkbox(label=self.tr("today"), value=False)
        picker = ft.DatePicker(first_date=datetime(2000, 1, 1), last_date=datetime(2100, 12, 31), on_change=lambda e: setattr(date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""))
        def pick():
            self.page.show_dialog(picker)
        def save():
            chosen = date_field.value or (date.today().strftime("%Y-%m-%d") if today_check.value else "")
            if not chosen:
                self.notify(self.tr("select_date")); return
            student = self.students[name]
            pending = student["term"] <= 0
            if pending: student["pending_sessions"] += 1
            else: student["term"] -= 1
            self.attendance.append({"Name": name, "Date": chosen, "Pending": pending, "Settled": False})
            asyncio.create_task(self.persist()); self.notify(self.tr("attendance_ok")); self.attendance_screen()
        search = ft.TextField(label=self.tr("search"), value=self.attendance_query, on_change=self.on_attendance_search)
        records = [x for x in self.attendance if x["Name"] == name and (not self.attendance_query or self.attendance_query.casefold() in x["Date"].casefold())]
        history = []
        for item in records:
            suffix = "  • pending/settled" if item["Pending"] and item["Settled"] else ("  • pending/unsettled" if item["Pending"] else "")
            idx = self.attendance.index(item)
            history.append(ft.Row(controls=[ft.Text(item["Date"] + suffix, expand=True), self.btn(self.tr("delete"), lambda e, i=idx: self.delete_attendance(i), PALETTE["main"])]))
        self.base(self.tr("attendance") + " — " + name, ft.Column(expand=True, controls=[ft.Text(self.tr("question", name=name)), today_check, ft.Row(wrap=True, controls=[date_field, self.btn(self.tr("pick_date"), pick)]), self.btn(self.tr("save"), save, PALETTE["accent"]), ft.Text(self.tr("attendance")), search, ft.ListView(expand=True, controls=history or [ft.Text(self.tr("no_attendance"))])]))

    def on_attendance_search(self, e):
        self.attendance_query = e.control.value or ""
        self.attendance_screen()

    def delete_attendance(self, index):
        def remove():
            if 0 <= index < len(self.attendance): self.attendance.pop(index)
            asyncio.create_task(self.persist()); self.attendance_screen()
        self.confirm(self.tr("delete_attendance"), remove)

    def settings(self):
        language = ft.Dropdown(label=self.tr("language"), value=self.lang, options=[ft.DropdownOption(key="fa", text="فارسی"), ft.DropdownOption(key="en", text="English")], on_select=self.change_language)
        self.base(self.tr("settings"), ft.Column(controls=[language, self.btn(self.tr("export"), self.export_data, PALETTE["accent"]), ft.Text("Exports the complete combined data as an .xlsx file.")]))

    def change_language(self, e):
        self.lang = e.control.value or "fa"
        self.render()

    async def export_data(self):
        try:
            picker = ft.FilePicker()
            await picker.save_file(dialog_title=self.tr("export"), file_name="combined_data.xlsx", src_bytes=xlsx_bytes(serialize(self.students, self.attendance, self.labels)))
            self.notify(self.tr("save_ok"))
        except Exception as ex:
            log.exception("Excel export failed")
            self.notify(str(ex))

    def help_screen(self):
        self.base(self.tr("help_title"), ft.Text(self.tr("help_text"), selectable=True))

    def level_screen(self):
        saved = getattr(self, "level_state", None)
        entry = ft.TextField(label=self.tr("new_level"), value=saved[0] if saved else "")
        selected = {"value": saved[1] if saved else None}
        rows = []
        for value in self.levels:
            rows.append(ft.ListTile(title=ft.Text(value), on_click=lambda e, v=value: self.select_level(v)))
        self.level_screen_content(entry, selected, rows)

    def select_level(self, value):
        self.level_state = (value, value)
        self.render()

    def level_screen_content(self, entry, selected, rows):
        def add():
            value = (entry.value or "").strip()
            if value and value not in self.levels: self.levels.append(value)
            if self.level_return == "edit": self.set_screen("edit")
            else: self.set_screen("add")
        def rename():
            old, new = selected["value"], (entry.value or "").strip()
            if old and new and new not in self.levels:
                self.levels[self.levels.index(old)] = new
                for student in self.students.values():
                    if student["level"] == old: student["level"] = new
                asyncio.create_task(self.persist())
            self.level_state = ((entry.value or ""), selected["value"])
            self.render()
        def delete():
            old = selected["value"]
            if old and old not in {s["level"] for s in self.students.values()}:
                self.levels.remove(old); self.render()
        self.base(self.tr("levels"), ft.Column(expand=True, controls=[ft.ListView(expand=True, controls=rows), entry, ft.Row(wrap=True, controls=[self.btn(self.tr("add_level"), add), self.btn(self.tr("rename"), rename), self.btn(self.tr("delete"), delete)])]))

    async def start(self):
        rows = await load_records(self.page)
        self.students, self.attendance, self.labels, self.levels = parse_records(rows)
        log.info("Loaded %d students, %d attendance records, %d labels", len(self.students), len(self.attendance), len(self.labels))
        self.render()


async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    app = AttendanceApp(page)
    await app.start()


ft.run(main)
