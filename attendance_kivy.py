# ============================================================
# ATTENDANCE - KIVY VERSION
# Converted from the original Tkinter application
# ============================================================

import os
import calendar as cal_mod
from datetime import datetime

import pandas as pd

from kivy.config import Config

# Disable Kivy touch-ring visualization and treat right mouse clicks as non-button actions.
Config.set("modules", "touchring", "")
Config.set("input", "mouse", "mouse,disable_multitouch")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    arabic_reshaper = None
    get_display = None


# ============================================================
# GLOBALS
# ============================================================

students_dict = {}
combined_file = "combined_data.csv"

COMBINED_COLUMNS = [
    "RecordType", "Name", "Date", "Pending", "Settled", "Label",
    "SessionsPerWeek", "Level", "Term", "OriginalTerm",
    "PendingSessions", "Note", "Labels", "ClassDays",
]

selected_index = None
old_name = None
active_filter = None
attendance_student = None
attendance_date = ""
add_session_mode = "add"

saved_labels = []
level_list = ["Beginner", "Intermediate", "Advanced"]
days_list = [
    "Saturday", "Sunday", "Monday", "Tuesday",
    "Wednesday", "Thursday", "Friday"
]

pages = {}
filter_widgets = []

name_entry = None
sessions_entry = None
term_entry = None
note_entry = None
labels_entry = None
level_entry = None

attendance_question_label = None
attendance_today_check = None
attendance_listbox = None
attendance_search_entry = None
attendance_date_widget = None
update_listbox = None
reports_search_entry = None

calendar_grid = None
calendar_search_entry = None
levels_return_page = "main"
student_grid = None
stats_labels = []

add_steps = {}
add_day_combos = {}
add_next_btns = {}

edit_steps = {}
edit_day_combos = {}
edit_next_btns = {}

add_step_box = None
edit_step_box = None

# Keep Add and Edit form widgets separate so opening one page never breaks the other.
add_widgets = {}
edit_widgets = {}


# ============================================================
# COLORS / FONT SIZES
# ============================================================

BG_MAIN = "#CAD2C5"
BG_SECOND = "#84A98C"
BG_LIGHT = "#F8F9F7"
ENTRY_BG = "#FFFFFF"
RED = "#52796F"
RED_ACTIVE = "#354F52"
TEXT_LIGHT = "#FFFFFF"
TEXT_DARK = "#2F3E46"
BG_LINE = "#6B7F72"

FONT = dp(16)
FONT_BOLD = dp(16)
if os.path.exists(r"C:\Windows\Fonts\tahoma.ttf"):
    FONT_NAME = r"C:\Windows\Fonts\tahoma.ttf"
elif os.path.exists(r"C:\Windows\Fonts\arial.ttf"):
    FONT_NAME = r"C:\Windows\Fonts\arial.ttf"
else:
    FONT_NAME = "DejaVuSans.ttf"

def rtl_text(text):
    """Prepare Persian/Arabic text for Kivy's LTR text renderer.
    Arabic shaping + bidi visual ordering prevents Persian labels from appearing
    backwards while leaving mixed/English text unchanged.
    """
    text = str(text)
    if lang != "fa" or not text.strip():
        return text
    if arabic_reshaper is None or get_display is None:
        return text
    try:
        reshaped = arabic_reshaper.reshape(
            text,
            configuration={
                "delete_harakat": False,
                "support_ligatures": True,
            },
        )
        return get_display(reshaped, base_dir="R")
    except Exception:
        try:
            return get_display(arabic_reshaper.reshape(text), base_dir="R")
        except Exception:
            return text


# Use a Windows font with Persian glyphs when available instead of Kivy's default Roboto.
if os.path.exists(r"C:\Windows\Fonts\tahoma.ttf"):
    FONT_NAME = r"C:\Windows\Fonts\tahoma.ttf"
elif os.path.exists(r"C:\Windows\Fonts\arial.ttf"):
    FONT_NAME = r"C:\Windows\Fonts\arial.ttf"
else:
    FONT_NAME = "DejaVuSans.ttf"


def rtl_text(text):
    text = str(text)
    if lang == "fa" and arabic_reshaper is not None and get_display is not None:
        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            pass
    return text


# ============================================================
# TRANSLATIONS
# ============================================================

lang = "fa"

TRANSLATIONS = {
    "en": {
        "app_title": "Attendance",
        "btn_help": "Help",
        "btn_reports": "Reports",
        "btn_add": "Add",
        "btn_calendar": "Calendar",
        "btn_settings": "Settings",
        "btn_all": "All",
        "hint_main": "Select a student and use the buttons above.",
        "col_name": "Name",
        "col_sessions": "Sessions",
        "col_level": "Level",
        "col_term": "Term",
        "col_note": "Note",
        "col_labels": "Labels",
        "col_days": "Class Days",
        "menu_attendance": "Attendance",
        "menu_edit": "Edit",
        "menu_delete": "Delete",
        "menu_close": "Close",
        "back": "← Back",
        "help_title": "Help",
        "help_text": (
            "How to use this app:\n\n"
            "• Add: register a new student. After choosing sessions per week "
            "you select the class day for each session.\n"
            "• Reports: shows how many sessions each student has left. "
            "Students with 0 sessions can be renewed.\n"
            "• Calendar: shows class days for each student.\n"
            "• Attendance: register today's class or a custom date.\n"
            "• Settings: change language or export data to Excel."
        ),
        "reports_title": "Reports",
        "sessions_left": "{name} : {count} sessions left",
        "renew": "Renew",
        "renew_question": "Do you want to renew this student term?",
        "renew_success": "Term renewed successfully",
        "levels_title": "Levels",
        "add": "Add",
        "rename": "Rename",
        "delete": "Delete",
        "enter_new_name": "Enter new name:",
        "delete_level_confirm": "Delete this level?",
        "add_title": "Add Student",
        "edit_title": "Edit Student",
        "name": "Name:",
        "sessions_week": "Sessions\nin week:",
        "term": "Term:",
        "level": "Level",
        "note": "Note:",
        "labels": "Labels:",
        "edit_levels": "Edit",
        "next": "Next",
        "submit": "Submit",
        "save": "Save",
        "session_n": "Session {n}",
        "class_day": "Class day:",
        "day_Saturday": "Saturday",
        "day_Sunday": "Sunday",
        "day_Monday": "Monday",
        "day_Tuesday": "Tuesday",
        "day_Wednesday": "Wednesday",
        "day_Thursday": "Thursday",
        "day_Friday": "Friday",
        "attendance_title": "Attendance",
        "attendance_question": "Did {name} have class today?",
        "today": "Today",
        "or_enter_date": "Or enter date:",
        "pick_date": "Pick Date",
        "term_sessions": "{n} sessions",
        "sessions_in_term": "Sessions in term:",
        "pending_settled": "   (Pending ✓ Settled)",
        "pending_not_settled": "   (Pending ✗ Not Settled)",
        "delete_attendance_confirm": "Delete this attendance?",
        "attendance_confirm": "Do you want to register attendance for this student?",
        "attendance_success": "Attendance was registered successfully",
        "attended_on": "{name} attended on {date}",
        "cancel": "Cancel",
        "calendar_title": "Calendar",
        "settings_title": "Settings",
        "language": "Language:",
        "lang_en": "English",
        "lang_fa": "Persian",
        "export_section": "Export data to Excel files (saved in the app folder):",
        "export_btn": "Export Excel",
        "export_success": "Excel files were exported successfully",
        "export_fail": "Some files could not be exported",
        "error": "Error",
        "success": "Success",
        "confirm": "Confirm",
        "err_all_fields": "All fields must be filled",
        "err_name_letters": "Name must contain only letters",
        "err_term_number": "Term must contain only numbers",
        "err_exists": "This student already exists",
        "err_select_first": "Select a student first",
        "err_select_day": "Select a class day for this session",
        "add_confirm": "Add this student?",
        "edit_confirm": "Save the changes for this student?",
        "delete_confirm": "Delete this student?",
        "delete_success": "Student deleted successfully",
        "add_success": "Student added successfully",
        "edit_success": "Student edited successfully",
        "stat_total": "Total students: {count}",
        "stat_today": "Students with class today: {count}",
        "stat_zero": "Students with term ended: {count}",
    },
    "fa": {
        "app_title": "حضور و غیاب",
        "btn_help": "راهنما",
        "btn_reports": "گزارش‌ها",
        "btn_add": "افزودن",
        "btn_calendar": "تقویم",
        "btn_settings": "تنظیمات",
        "btn_all": "همه",
        "hint_main": "یک دانش‌آموز را انتخاب کنید و از دکمه‌های بالا استفاده کنید.",
        "col_name": "نام",
        "col_sessions": "جلسات",
        "col_level": "سطح",
        "col_term": "ترم",
        "col_note": "یادداشت",
        "col_labels": "برچسب‌ها",
        "col_days": "روزهای کلاس",
        "menu_attendance": "حضور و غیاب",
        "menu_edit": "ویرایش",
        "menu_delete": "حذف",
        "menu_close": "بستن",
        "back": "← بازگشت",
        "help_title": "راهنما",
        "help_text": (
            "راهنمای استفاده از برنامه:\n\n"
            "• افزودن: برای ثبت دانش‌آموز جدید.\n"
            "• گزارش‌ها: تعداد جلسات باقی‌مانده را نشان می‌دهد.\n"
            "• تقویم: روزهای کلاس هر دانش‌آموز را نشان می‌دهد.\n"
            "• حضور و غیاب: حضور امروز یا یک تاریخ دلخواه را ثبت کنید.\n"
            "• تنظیمات: زبان را تغییر دهید یا داده‌ها را به Excel خروجی بگیرید."
        ),
        "reports_title": "گزارش‌ها",
        "sessions_left": "{name} : {count} جلسه باقی‌مانده",
        "renew": "تمدید",
        "renew_question": "ترم این دانش‌آموز تمدید شود؟",
        "renew_success": "ترم با موفقیت تمدید شد",
        "levels_title": "سطوح",
        "add": "افزودن",
        "rename": "تغییر نام",
        "delete": "حذف",
        "enter_new_name": "نام جدید را وارد کنید:",
        "delete_level_confirm": "این سطح حذف شود؟",
        "add_title": "افزودن دانش‌آموز",
        "edit_title": "ویرایش دانش‌آموز",
        "name": "نام:",
        "sessions_week": "جلسات\nدر هفته:",
        "term": "ترم:",
        "level": "سطح",
        "note": "یادداشت:",
        "labels": "برچسب‌ها:",
        "edit_levels": "ویرایش",
        "next": "بعدی",
        "submit": "ثبت",
        "save": "ذخیره",
        "session_n": "جلسه {n}",
        "class_day": "روز کلاس:",
        "day_Saturday": "شنبه",
        "day_Sunday": "یکشنبه",
        "day_Monday": "دوشنبه",
        "day_Tuesday": "سه‌شنبه",
        "day_Wednesday": "چهارشنبه",
        "day_Thursday": "پنجشنبه",
        "day_Friday": "جمعه",
        "attendance_title": "حضور و غیاب",
        "attendance_question": "آیا {name} امروز کلاس داشت؟",
        "today": "امروز",
        "or_enter_date": "یا تاریخ را وارد کنید:",
        "pick_date": "انتخاب تاریخ",
        "term_sessions": "{n} جلسه",
        "sessions_in_term": "جلسات ترم:",
        "pending_settled": "   (در انتظار ✓ تسویه شد)",
        "pending_not_settled": "   (در انتظار ✗ تسویه نشده)",
        "delete_attendance_confirm": "این حضور و غیاب حذف شود؟",
        "attendance_confirm": "حضور و غیاب این دانش‌آموز ثبت شود؟",
        "attendance_success": "حضور و غیاب با موفقیت ثبت شد",
        "attended_on": "{name} در تاریخ {date} حضور داشت",
        "cancel": "انصراف",
        "calendar_title": "تقویم",
        "settings_title": "تنظیمات",
        "language": "زبان:",
        "lang_en": "انگلیسی",
        "lang_fa": "فارسی",
        "export_section": "خروجی اکسل از داده‌ها (در پوشه برنامه ذخیره می‌شود):",
        "export_btn": "خروجی اکسل",
        "export_success": "فایل‌های اکسل با موفقیت ذخیره شدند",
        "export_fail": "برخی فایل‌ها خروجی گرفته نشدند",
        "error": "خطا",
        "success": "موفق",
        "confirm": "تأیید",
        "err_all_fields": "همه فیلدها باید پر شوند",
        "err_name_letters": "نام باید فقط شامل حروف باشد",
        "err_term_number": "ترم باید فقط شامل عدد باشد",
        "err_exists": "این دانش‌آموز قبلاً وجود دارد",
        "err_select_first": "ابتدا یک دانش‌آموز انتخاب کنید",
        "err_select_day": "برای این جلسه یک روز انتخاب کنید",
        "add_confirm": "این دانش‌آموز اضافه شود؟",
        "edit_confirm": "تغییرات این دانش‌آموز ذخیره شود؟",
        "delete_confirm": "این دانش‌آموز حذف شود؟",
        "delete_success": "دانش‌آموز با موفقیت حذف شد",
        "add_success": "دانش‌آموز با موفقیت اضافه شد",
        "edit_success": "دانش‌آموز با موفقیت ویرایش شد",
        "stat_total": "تعداد کل دانش‌آموزان: {count}",
        "stat_today": "تعداد دانش‌آموزان دارای کلاس امروز: {count}",
        "stat_zero": "تعداد دانش‌آموزان با ترم تمام‌شده: {count}",
    },
}


# ============================================================
# SECTION 1: CONFIG & LANGUAGE
# ============================================================

def tr(key):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


DAY_FA_TO_EN = {
    "شنبه": "Saturday",
    "یکشنبه": "Sunday",
    "دوشنبه": "Monday",
    "سه‌شنبه": "Tuesday",
    "چهارشنبه": "Wednesday",
    "پنجشنبه": "Thursday",
    "جمعه": "Friday",
}
DAY_EN_TO_FA = {v: k for k, v in DAY_FA_TO_EN.items()}


def local_days():
    if lang == "fa":
        return [rtl_text(DAY_EN_TO_FA[d]) for d in days_list]
    return days_list


def combo_to_en(value):
    if lang == "fa":
        for fa_day, en_day in DAY_FA_TO_EN.items():
            if value in (fa_day, rtl_text(fa_day)):
                return en_day
    return value


def en_to_combo(value):
    if lang == "fa":
        return rtl_text(DAY_EN_TO_FA.get(value, value))
    return value


def apply_rtl(widget):
    """Kivy replacement for the original Tkinter RTL helper."""
    if lang != "fa":
        return

    if isinstance(widget, (Label, TextInput, Spinner)):
        if hasattr(widget, "halign"):
            widget.halign = "right"
        if isinstance(widget, TextInput):
            widget.cursor_color = (1, 1, 1, 1)

    for child in widget.children:
        apply_rtl(child)


# ============================================================
# SECTION 2: DATA LAYER
# ============================================================

def read_combined():
    if os.path.exists(combined_file):
        return pd.read_csv(combined_file)
    return pd.DataFrame(columns=COMBINED_COLUMNS)


def write_combined(df):
    if "RecordType" in df.columns:
        order = {"student": 0, "attendance": 1, "label": 2}
        df = df.assign(_order=df["RecordType"].map(order).fillna(99))
        df = df.sort_values("_order", kind="stable").drop(columns="_order")

    for column in COMBINED_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df[COMBINED_COLUMNS].to_csv(combined_file, index=False)


def replace_records(record_type, new_records):
    df = read_combined()

    if "RecordType" in df.columns:
        df = df[df["RecordType"] != record_type]

    df = pd.concat([df, new_records], ignore_index=True)
    write_combined(df)


def load_data():
    global students_dict

    df = read_combined()

    if "RecordType" in df.columns:
        df = df[df["RecordType"] == "student"]

    for _, row in df.iterrows():
        name = row["Name"]
        sessions_per_week = int(row["SessionsPerWeek"])
        level = row["Level"]
        term = int(row["Term"])
        original_term = int(row["OriginalTerm"])
        note = row["Note"]
        class_days = []

        if "ClassDays" in df.columns:
            raw = str(row["ClassDays"])
            if raw != "nan" and raw:
                class_days = raw.split(",")

        labels = []

        if "Labels" in df.columns:
            labels = str(row["Labels"]).split(",")
            if labels == ["nan"]:
                labels = []

        pending_sessions = 0

        if "PendingSessions" in df.columns:
            pending_sessions = int(row["PendingSessions"])

        students_dict[name] = {
            "sessions_per_week": sessions_per_week,
            "level": level,
            "term": term,
            "original_term": original_term,
            "pending_sessions": pending_sessions,
            "note": note,
            "labels": labels,
            "class_days": class_days,
        }


def save_to_csv():
    rows = []

    for name, info in students_dict.items():
        rows.append({
            "RecordType": "student",
            "Name": name,
            "SessionsPerWeek": info["sessions_per_week"],
            "Level": info["level"],
            "Term": info["term"],
            "OriginalTerm": info["original_term"],
            "PendingSessions": info["pending_sessions"],
            "Note": info["note"],
            "Labels": ",".join(info["labels"]),
            "ClassDays": ",".join(info.get("class_days", [])),
        })

    replace_records(
        "student",
        pd.DataFrame(
            rows,
            columns=[
                "RecordType", "Name", "SessionsPerWeek", "Level",
                "Term", "OriginalTerm", "PendingSessions", "Note",
                "Labels", "ClassDays"
            ]
        )
    )


def save_attendance_to_csv(name, date, pending=False):
    df = read_combined()

    if "RecordType" in df.columns:
        df = df[df["RecordType"] == "attendance"]
    else:
        df = pd.DataFrame(
            columns=["RecordType", "Name", "Date", "Pending", "Settled"]
        )

    if "Pending" not in df.columns:
        df["Pending"] = False
    if "Settled" not in df.columns:
        df["Settled"] = False

    new_data = pd.DataFrame({
        "RecordType": ["attendance"],
        "Name": [name],
        "Date": [date],
        "Pending": [pending],
        "Settled": [False],
    })

    df = pd.concat([df, new_data], ignore_index=True)
    df["Pending"] = df["Pending"].astype(bool)
    df["Settled"] = df["Settled"].astype(bool)
    replace_records("attendance", df)


def remaining_sessions(name):
    return int(students_dict[name]["term"])


def load_labels():
    global saved_labels

    saved_labels.clear()

    try:
        df = read_combined()

        if "RecordType" in df.columns:
            df = df[df["RecordType"] == "label"]

        for label in df["Label"]:
            label = str(label)
            if label != "nan" and label not in saved_labels:
                saved_labels.append(label)
    except Exception:
        pass


def save_labels():
    rows = [{"RecordType": "label", "Label": label} for label in saved_labels]
    replace_records(
        "label",
        pd.DataFrame(rows, columns=["RecordType", "Label"]),
    )


# ============================================================
# KIVY HELPERS
# ============================================================

def color_tuple(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)


def set_widget_background(widget, hex_color):
    """Give a Kivy layout a real background, matching Tkinter's bg= option."""
    if getattr(widget, "_attendance_bg_ready", False):
        widget._attendance_bg_color.rgba = color_tuple(hex_color)
        return

    with widget.canvas.before:
        widget._attendance_bg_color = Color(*color_tuple(hex_color))
        widget._attendance_bg_rect = Rectangle(pos=widget.pos, size=widget.size)

    def update_rect(instance, _value):
        instance._attendance_bg_rect.pos = instance.pos
        instance._attendance_bg_rect.size = instance.size

    widget.bind(pos=update_rect, size=update_rect)
    widget._attendance_bg_ready = True


# Use the app background instead of Kivy's default black.
Window.clearcolor = color_tuple(BG_MAIN)


def tk_place(widget, parent, x, y, width, height):
    """Tkinter-like fixed placement for the internal 1000x700 pages.
    The original Tkinter app uses fixed pixel coordinates, so internal pages
    intentionally stay 1000x700 and are anchored at the top-left.
    """
    widget.size_hint = (None, None)
    widget.size = (dp(width), dp(height))

    def update(*_):
        widget.size = (dp(width), dp(height))
        widget.pos = (dp(x), parent.height - dp(y + height))

    parent.bind(size=update)
    Clock.schedule_once(lambda *_: update(), 0)
    return widget


def tk_place_rel(widget, parent, x, y, relwidth, relheight):
    """Relative placement against the original 1000x700 Tkinter canvas."""
    width = 1000 * relwidth
    height = 700 * relheight
    return tk_place(widget, parent, x, y, width, height)

def make_page():
    page = FloatLayout()
    set_widget_background(page, BG_SECOND)
    return page


class SafeButton(Button):
    """Button that ignores right mouse clicks so they never trigger a button action."""
    def on_touch_down(self, touch):
        if getattr(touch, "button", None) == "right":
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if getattr(touch, "button", None) == "right":
            return True
        return super().on_touch_up(touch)


def make_button(text="", command=None, bg=BG_MAIN, fg=TEXT_DARK,
                height=dp(50), size_hint_y=None, font_size=FONT_BOLD):
    b = SafeButton(
        text=rtl_text(text),
        font_name=FONT_NAME,
        size_hint_y=size_hint_y,
        height=height,
        font_size=font_size,
        background_normal="",
        background_color=color_tuple(bg),
        color=color_tuple(fg),
        halign="center",
        valign="middle",
    )
    b.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    if command:
        b.bind(on_release=lambda *_: command())
    return b


def make_label(text="", bg=BG_SECOND, fg=TEXT_LIGHT,
               height=dp(45), font_size=FONT):
    l = Label(
        text=rtl_text(text),
        font_name=FONT_NAME,
        size_hint_y=None,
        height=height,
        font_size=font_size,
        color=color_tuple(fg),
        halign="center",
        valign="middle",
    )
    l.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    set_widget_background(l, bg)
    return l


def make_input(text="", multiline=False):
    entry = TextInput(
        text=str(text),
        font_name=FONT_NAME,
        multiline=multiline,
        size_hint_y=None,
        height=dp(55),
        font_size=FONT,
        background_color=color_tuple(ENTRY_BG),
        foreground_color=color_tuple(TEXT_DARK),
        padding=[dp(10), dp(10)],
    )
    entry.halign = "right" if lang == "fa" else "left"
    return entry


def show_popup(title, message, buttons=None, width=dp(600), height=dp(280)):
    box = BoxLayout(
        orientation="vertical",
        padding=dp(15),
        spacing=dp(15),
    )

    box.add_widget(make_label(
        message,
        bg=BG_LIGHT,
        fg=TEXT_DARK,
        height=dp(130),
        font_size=dp(16),
    ))

    button_row = BoxLayout(
        size_hint_y=None,
        height=dp(55),
        spacing=dp(10),
    )

    popup = Popup(
        title=title,
        content=box,
        size_hint=(None, None),
        size=(width, height),
        auto_dismiss=False,
    )

    if buttons is None:
        buttons = [("OK", popup.dismiss)]

    for text, callback in buttons:
        b = make_button(text, bg=BG_MAIN)
        b.bind(on_release=lambda *_,
                cb=callback: (cb(), popup.dismiss()))
        button_row.add_widget(b)

    box.add_widget(button_row)
    popup.open()
    return popup


def confirm_popup(title, message, yes_callback):
    show_popup(
        title,
        message,
        [
            (tr("confirm"), yes_callback),
            (tr("cancel"), lambda: None),
        ],
        height=dp(270),
    )


# ============================================================
# SECTION 3: MAIN WINDOW UI
# ============================================================

def show_main():
    show_page("main")
    refresh_listbox()


def show_page(page):
    if page not in pages:
        return

    target = pages[page]
    root_manager.clear_widgets()
    target.size_hint = (1, 1)
    target.pos = (0, 0)
    target.opacity = 1
    target.disabled = False
    root_manager.add_widget(target)

def refresh_stats():
    total = len(students_dict)

    today_index = (datetime.now().weekday() + 2) % 7
    today_en = days_list[today_index]

    today_count = sum(
        1 for info in students_dict.values()
        if today_en in info.get("class_days", [])
    )

    zero_count = sum(
        1 for info in students_dict.values()
        if info.get("term", 1) <= 0
    )

    if len(stats_labels) >= 3:
        stats_labels[0].text = rtl_text(tr("stat_total").format(count=total))
        stats_labels[1].text = rtl_text(tr("stat_today").format(count=today_count))
        stats_labels[2].text = rtl_text(tr("stat_zero").format(count=zero_count))


def make_live_search(parent, hint, callback, x=None, y=None, width=500):
    entry = make_input()
    entry.hint_text = rtl_text(hint)
    entry.halign = "right" if lang == "fa" else "left"
    if x is not None:
        tk_place(entry, parent, x, y, width, 45)
        parent.add_widget(entry)
    else:
        parent.add_widget(entry)
    entry.bind(text=lambda widget, value: callback(value))
    return entry


def show_not_found(container, message="پیدا نشد"):
    container.clear_widgets()
    container.add_widget(make_label(message, bg=BG_LIGHT, fg=TEXT_DARK, height=dp(45), font_size=dp(14)))


def refresh_listbox(student_names=None):
    if student_grid is None:
        return

    student_grid.clear_widgets()

    if student_names is None:
        student_names = list(students_dict.keys())
    if not student_names:
        show_not_found(student_grid)
        refresh_stats()
        return

    for name in student_names:
        info = students_dict[name]
        labels_text = ", ".join(info["labels"])

        row = Button(
            text=(
                f"{name}    |    "
                f"{info['sessions_per_week']}/week    |    "
                f"{info['level']}    |    "
                f"{tr('term_sessions').format(n=info['original_term'])}    |    "
                f"{info['note']}    |    "
                f"[{labels_text}]"
            ),
            size_hint_y=None,
            height=dp(48),
            font_size=dp(14),
            background_normal="",
            background_color=color_tuple(TEXT_LIGHT),
            color=color_tuple(TEXT_DARK),
            halign="left",
            valign="middle",
        )

        row.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        row.bind(on_release=lambda _, n=name: select_student(n))
        student_grid.add_widget(row)

    refresh_stats()


def select_student(name):
    global selected_index
    selected_index = name

    # Kivy replacement for Tkinter right-click context menu:
    # show action buttons in a popup.
    box = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        padding=dp(10),
    )

    popup = Popup(
        title=name,
        content=box,
        size_hint=(None, None),
        size=(dp(330), dp(280)),
        auto_dismiss=True,
    )

    for text, callback in [
        (tr("menu_attendance"), attendance_clicked),
        (tr("menu_edit"), edit_clicked),
        (tr("menu_delete"), delete_clicked),
    ]:
        b = make_button(text, bg=BG_MAIN)
        b.bind(on_release=lambda *_,
                cb=callback: (popup.dismiss(), cb()))
        box.add_widget(b)

    popup.open()


def show_all_students():
    global active_filter
    active_filter = None
    refresh_listbox()


def create_filter():
    box = BoxLayout(
        orientation="horizontal",
        spacing=dp(8),
        padding=dp(10),
        size_hint_y=None,
        height=dp(65),
    )

    entry = make_input()
    entry.hint_text = tr("labels")
    box.add_widget(entry)

    popup = Popup(
        title=tr("add"),
        content=box,
        size_hint=(None, None),
        size=(dp(600), dp(170)),
    )

    def finish(*_):
        text = entry.text.strip()
        if not text:
            popup.dismiss()
            return

        if text not in saved_labels:
            saved_labels.append(text)
            save_labels()

        create_tag(text)
        popup.dismiss()

    add = make_button(tr("add"), bg=RED)
    add.bind(on_release=finish)
    box.add_widget(add)

    popup.open()


def create_tag(text):
    if filter_container is None:
        return

    tag = make_button(
        text=text,
        bg=BG_SECOND,
        fg=TEXT_LIGHT,
        height=dp(42),
        font_size=dp(14),
    )
    tag.size_hint_x = None
    tag.width = max(dp(80), dp(len(text) * 9 + 35))

    def filter_students():
        global active_filter
        active_filter = text
        filtered = [
            name for name, info in students_dict.items()
            if text in info["labels"]
        ]
        refresh_listbox(filtered)

    def tag_menu():
        box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10),
        )

        popup = Popup(
            title=text,
            content=box,
            size_hint=(None, None),
            size=(dp(320), dp(220)),
        )

        rename_btn = make_button(tr("rename"), bg=BG_MAIN)
        delete_btn = make_button(tr("delete"), bg=RED)

        rename_btn.bind(
            on_release=lambda *_: (
                popup.dismiss(),
                rename_tag(text),
            )
        )
        delete_btn.bind(
            on_release=lambda *_: (
                popup.dismiss(),
                delete_tag(text),
            )
        )

        box.add_widget(rename_btn)
        box.add_widget(delete_btn)
        popup.open()

    tag.bind(on_release=lambda *_: filter_students())

    # Long/right click is platform-dependent in Kivy.
    # A second action button is therefore used for rename/delete.
    menu_btn = make_button("⋮", bg=BG_SECOND, fg=TEXT_LIGHT,
                           height=dp(42), font_size=dp(18))
    menu_btn.size_hint_x = None
    menu_btn.width = dp(42)
    menu_btn.bind(on_release=lambda *_: tag_menu())

    tag_row = BoxLayout(
        orientation="horizontal",
        size_hint_x=None,
        width=tag.width + dp(50),
        size_hint_y=None,
        height=dp(42),
        spacing=dp(4),
    )
    tag_row.add_widget(tag)
    tag_row.add_widget(menu_btn)

    filter_widgets.append(tag_row)
    filter_bar.add_widget(tag_row)


def rename_tag(old_text):
    box = BoxLayout(
        orientation="vertical",
        padding=dp(10),
        spacing=dp(10),
    )

    entry = make_input(old_text)
    box.add_widget(entry)

    popup = Popup(
        title=tr("rename"),
        content=box,
        size_hint=(None, None),
        size=(dp(500), dp(210)),
    )

    save = make_button(tr("save"), bg=RED)

    def do_rename(*_):
        new_text = entry.text.strip()
        if not new_text:
            return

        if old_text in saved_labels:
            saved_labels.remove(old_text)
        if new_text not in saved_labels:
            saved_labels.append(new_text)

        for info in students_dict.values():
            info["labels"] = [
                new_text if x == old_text else x
                for x in info["labels"]
            ]

        save_labels()
        save_to_csv()
        rebuild_filter_bar()
        refresh_listbox()
        popup.dismiss()

    save.bind(on_release=do_rename)
    box.add_widget(save)
    popup.open()


def delete_tag(text):
    def do_delete():
        if text in saved_labels:
            saved_labels.remove(text)

        for info in students_dict.values():
            if text in info["labels"]:
                info["labels"].remove(text)

        save_labels()
        save_to_csv()
        rebuild_filter_bar()
        refresh_listbox()

    confirm_popup(tr("confirm"), tr("delete_confirm"), do_delete)


def rebuild_filter_bar():
    filter_bar.clear_widgets()
    filter_widgets.clear()

    all_btn = make_button(
        tr("btn_all"),
        bg=BG_SECOND,
        height=dp(42),
        font_size=dp(14),
    )
    all_btn.size_hint_x = None
    all_btn.width = dp(70)
    all_btn.bind(on_release=lambda *_: show_all_students())
    filter_bar.add_widget(all_btn)

    plus = make_button("+", bg=BG_SECOND, height=dp(42))
    plus.size_hint_x = None
    plus.width = dp(45)
    plus.bind(on_release=lambda *_: create_filter())
    filter_bar.add_widget(plus)

    for label in saved_labels:
        create_tag(label)


def setup_main_window():
    global main_root, student_grid, filter_bar, filter_container
    global stats_labels

    main_root = BoxLayout(
        orientation="vertical",
        padding=dp(10),
        spacing=dp(10),
    )

    # Top navigation
    nav = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(52),
        spacing=dp(6),
    )

    for text, callback in [
        (tr("btn_calendar"), calendar_clicked),
        (tr("btn_add"), addbtn_clicked),
        (tr("btn_reports"), updatebtn_clicked),
        (tr("btn_settings"), settings_clicked),
        (tr("btn_help"), helpbtn_clicked),
    ]:
        nav.add_widget(make_button(text, command=callback, bg=BG_SECOND))

    main_root.add_widget(nav)

    # Filter bar
    filter_container = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(55),
    )

    filter_scroll = ScrollView(
        do_scroll_y=False,
        do_scroll_x=True,
    )

    filter_bar = BoxLayout(
        orientation="horizontal",
        spacing=dp(6),
        size_hint_x=None,
        size_hint_y=None,
        height=dp(45),
    )

    filter_bar.bind(minimum_width=lambda w, value: setattr(w, "width", value))
    filter_scroll.add_widget(filter_bar)
    filter_container.add_widget(filter_scroll)
    main_root.add_widget(filter_container)

    # Statistics
    stats = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(58),
        spacing=dp(4),
    )

    stats_labels.clear()

    for text in ["", "", ""]:
        label = make_label(
            text,
            bg=BG_SECOND,
            fg=TEXT_LIGHT,
            height=dp(58),
            font_size=dp(14),
        )
        stats_labels.append(label)
        stats.add_widget(label)

    main_root.add_widget(stats)

    # Live student search
    make_live_search(main_root, "Search students...", lambda value: refresh_listbox(
        [n for n in students_dict if value.strip().lower() in n.lower()] if value.strip() else None
    ))

    # Student list
    scroll = ScrollView()
    student_grid = GridLayout(
        cols=1,
        spacing=dp(2),
        size_hint_y=None,
    )
    student_grid.bind(minimum_height=student_grid.setter("height"))
    scroll.add_widget(student_grid)
    main_root.add_widget(scroll)

    pages["main"] = main_root


# ============================================================
# SECTION 4: ADD STUDENT
# ============================================================

def addbtn_clicked():
    global name_entry, sessions_entry, term_entry, note_entry, labels_entry, level_entry
    global add_session_mode

    add_session_mode = "add"

    if "add" not in pages:
        build_add_page()

    # Restore the Add page's own widgets. Edit has a separate set.
    name_entry = add_widgets["name_entry"]
    sessions_entry = add_widgets["sessions_entry"]
    term_entry = add_widgets["term_entry"]
    note_entry = add_widgets["note_entry"]
    labels_entry = add_widgets["labels_entry"]
    level_entry = add_widgets["level_entry"]

    name_entry.text = ""
    sessions_entry.text = ""
    sessions_entry.values = [str(x) for x in range(1, 8)]
    term_entry.text = ""
    note_entry.text = ""
    level_entry.text = ""

    labels_entry.clear_widgets()
    for label in saved_labels:
        b = make_button(label, bg=BG_LIGHT, fg=TEXT_DARK, height=dp(27), font_size=dp(13))
        b.selected_for_labels = False

        def toggle(widget, label=label):
            widget.selected_for_labels = not widget.selected_for_labels
            if widget.selected_for_labels:
                widget.background_color = color_tuple(BG_SECOND)
                widget.color = color_tuple(TEXT_LIGHT)
            else:
                widget.background_color = color_tuple(BG_LIGHT)
                widget.color = color_tuple(TEXT_DARK)

        b.bind(on_release=toggle)
        labels_entry.add_widget(b)

    build_session_steps_kivy(add_steps, add_day_combos, add_next_btns, 0, None, add=True)
    show_page("add")
    show_step(add_steps, 0, add_next_btns)

def build_add_page():
    global name_entry, sessions_entry, term_entry, note_entry, labels_entry, level_entry
    global add_step_box

    root = make_page()

    back = make_button(tr("back"), bg=BG_MAIN, height=dp(45), font_size=dp(14))
    tk_place(back, root, 15, 15, 180, 45)
    back.bind(on_release=lambda *_: show_main())
    root.add_widget(back)

    title = make_label(tr("add_title"), bg=RED, height=dp(45), font_size=FONT_BOLD)
    tk_place(title, root, 15, 75, 960, 45)
    root.add_widget(title)

    info = FloatLayout()
    set_widget_background(info, BG_SECOND)
    tk_place(info, root, 0, 45, 1000, 500)
    root.add_widget(info)

    def add_label(text, x, y, w=220):
        l = make_label(text, bg=RED, fg=TEXT_LIGHT, height=dp(55), font_size=dp(14))
        l.halign = "left"
        l.padding_x = dp(8) if hasattr(l, 'padding_x') else 0
        tk_place(l, info, x, y, w, 55)
        info.add_widget(l)
        return l

    add_label(tr("name"), 15, -365)
    add_label(tr("sessions_week"), 515, -365, 200)
    add_label(tr("sessions_in_term"), 15, -300)
    add_label(tr("level"), 515, -300, 200)
    add_label(tr("note"), 15, -235)
    add_label(tr("labels"), 515, -235, 200)

    name_entry = make_input()
    tk_place(name_entry, info, 255, -365, 220, 55); info.add_widget(name_entry)

    sessions_entry = Spinner(text="", values=[str(x) for x in range(1,8)], size_hint=(None,None),
                              height=dp(55), font_size=dp(14), font_name=FONT_NAME, background_normal="",
                              background_color=color_tuple(ENTRY_BG), color=color_tuple(TEXT_DARK))
    tk_place(sessions_entry, info, 734, -365, 240, 55); info.add_widget(sessions_entry)

    term_entry = make_input()
    tk_place(term_entry, info, 255, -300, 220, 55); info.add_widget(term_entry)

    level_entry = Spinner(text="", values=level_list, size_hint=(None,None), height=dp(55),
                          font_size=dp(14), font_name=FONT_NAME, background_normal="",
                          background_color=color_tuple(ENTRY_BG), color=color_tuple(TEXT_DARK))
    tk_place(level_entry, info, 735, -300, 240, 55); info.add_widget(level_entry)

    edit_levels = make_button(tr("edit_levels"), bg=BG_MAIN, height=dp(55), font_size=dp(14))
    tk_place(edit_levels, info, 933, -235, 40, 55); info.add_widget(edit_levels)
    edit_levels.bind(on_release=lambda *_: level_edit_clicked())

    note_entry = make_input()
    tk_place(note_entry, info, 255, -235, 220, 55); info.add_widget(note_entry)

    labels_entry = GridLayout(cols=1, spacing=dp(1))
    labels_entry.bind(minimum_height=labels_entry.setter("height"))
    label_scroll = ScrollView(do_scroll_y=True, do_scroll_x=False)
    tk_place(label_scroll, info, 735, -235, 190, 55); label_scroll.add_widget(labels_entry); info.add_widget(label_scroll)

    next_btn = make_button(tr("next"), bg=BG_MAIN, height=dp(55), font_size=FONT_BOLD)
    tk_place(next_btn, info, 15, 380, 960, 55); info.add_widget(next_btn)
    next_btn.bind(on_release=lambda *_: add_info_next())

    add_step_box = FloatLayout()
    set_widget_background(add_step_box, BG_SECOND)
    tk_place(add_step_box, root, 0, 135, 1000, 500)
    root.add_widget(add_step_box)
    add_step_box.opacity = 0; add_step_box.disabled = True

    add_steps[0] = info
    add_widgets.update({
        "name_entry": name_entry,
        "sessions_entry": sessions_entry,
        "term_entry": term_entry,
        "note_entry": note_entry,
        "labels_entry": labels_entry,
        "level_entry": level_entry,
    })
    # Keep navigation controls above the form layer.
    root.remove_widget(back)
    root.remove_widget(title)
    root.add_widget(back)
    root.add_widget(title)

    pages["add"] = root

def add_total_sessions():
    try:
        return int(sessions_entry.text)
    except (ValueError, AttributeError):
        return 0


def build_session_steps_kivy(steps, day_combos, next_btns, total, prefill_days=None, add=False):
    for s in list(steps.keys()):
        if s != 0:
            if steps[s].parent:
                steps[s].parent.remove_widget(steps[s])
            del steps[s]
    day_combos.clear(); next_btns.clear()
    container = add_step_box if add else edit_step_box
    if container is None or total <= 0:
        return
    container.clear_widgets()

    for i in range(1, total + 1):
        step = FloatLayout()
        set_widget_background(step, BG_SECOND)
        steps[i] = step

        back = make_button(tr("back"), bg=BG_MAIN, height=dp(40), font_size=dp(13))
        tk_place(back, step, 15, 0, 180, 40)
        step.add_widget(back)
        back.bind(
            on_release=lambda *_ , a=add: (
                show_page("add" if a else "edit"),
                show_step(add_steps if a else edit_steps, 0, add_next_btns if a else edit_next_btns),
            )
        )

        title = make_label(tr("session_n").format(n=i), bg=RED, height=dp(55), font_size=FONT_BOLD)
        tk_place(title, step, 15, 55, 970, 55); step.add_widget(title)

        day_label = make_label(tr("class_day"), bg=RED, height=dp(55), font_size=dp(14))
        day_label.halign = "left"
        tk_place(day_label, step, 15, 130, 250, 55); step.add_widget(day_label)

        combo = Spinner(text="", values=local_days(), size_hint=(None,None), height=dp(55), font_size=dp(14),
                        background_normal="", background_color=color_tuple(ENTRY_BG), color=color_tuple(TEXT_DARK))
        if prefill_days and i <= len(prefill_days) and prefill_days[i-1]:
            combo.text = en_to_combo(prefill_days[i-1])
        tk_place(combo, step, 285, 130, 350, 55); step.add_widget(combo)
        day_combos[i] = combo

        btn = make_button(tr("next"), bg=BG_MAIN, height=dp(55), font_size=FONT_BOLD)
        tk_place(btn, step, 15, 355, 970, 55); step.add_widget(btn)
        btn.bind(on_release=lambda _, s=i, a=add: session_step_next_kivy(s, a))
        next_btns[i] = btn
        container.add_widget(step)

def show_step(steps, step, next_btns):
    """Show either the information form or the Sessions-in-Week screen.

    The active layer is moved to the top of the page so transparent/disabled
    Kivy layouts can never block TextInput or Spinner mouse/touch events.
    """
    is_add = (steps is add_steps)
    info = steps.get(0)
    container = add_step_box if is_add else edit_step_box
    root = pages.get("add" if is_add else "edit")

    if root is None:
        return

    if step == 0:
        if container is not None and container.parent is root:
            root.remove_widget(container)
        if info is not None and info.parent is not root:
            root.add_widget(info)
        if info is not None:
            info.opacity = 1
            info.disabled = False
        if container is not None:
            container.opacity = 0
            container.disabled = True
    else:
        if info is not None:
            info.opacity = 0
            info.disabled = True
        if container is not None and container.parent is not root:
            root.add_widget(container)
        if container is not None:
            container.opacity = 1
            container.disabled = False

        for s, widget in steps.items():
            if s == 0:
                continue
            active = (s == step)
            widget.opacity = 1 if active else 0
            widget.disabled = not active

    if step in next_btns:
        next_btns[step].text = tr("submit") if step == len(next_btns) else tr("next")


def session_step_next_kivy(step, add=True):
    if add:
        steps = add_steps
        combos = add_day_combos
        next_btns = add_next_btns
        total = add_total_sessions()
        submit = submit_add
    else:
        steps = edit_steps
        combos = edit_day_combos
        next_btns = edit_next_btns
        total = edit_total_sessions()
        submit = submit_edit

    if step not in combos or not combos[step].text.strip():
        show_popup(tr("error"), tr("err_select_day"))
        return

    if step == total:
        submit()
    else:
        show_step(steps, step + 1, next_btns)


def add_info_next():
    name = name_entry.text.strip()
    sessions = sessions_entry.text.strip()
    level = level_entry.text.strip()
    term = term_entry.text.strip()
    note = note_entry.text.strip()

    if not name or not sessions or not level or not term:
        show_popup(tr("error"), tr("err_all_fields"))
        return

    if not name.replace(" ", "").isalpha():
        show_popup(tr("error"), tr("err_name_letters"))
        return

    if not term.isdigit():
        show_popup(tr("error"), tr("err_term_number"))
        return

    if name in students_dict:
        show_popup(tr("error"), tr("err_exists"))
        return

    build_session_steps_kivy(
        add_steps,
        add_day_combos,
        add_next_btns,
        int(sessions),
        add=True,
    )

    show_step(add_steps, 1, add_next_btns)


def selected_labels_from_box():
    result = []

    for child in labels_entry.children:
        if getattr(child, "selected_for_labels", False):
            result.append(child.text)

    return result


def submit_add():
    name = name_entry.text.strip()
    sessions = int(sessions_entry.text)
    level = level_entry.text.strip()
    term = int(term_entry.text.strip())
    note = note_entry.text.strip()

    selected_labels = selected_labels_from_box()

    class_days = [
        combo_to_en(add_day_combos[i].text)
        for i in range(1, sessions + 1)
    ]

    students_dict[name] = {
        "sessions_per_week": sessions,
        "level": level,
        "term": term,
        "original_term": term,
        "pending_sessions": 0,
        "note": note,
        "labels": selected_labels,
        "class_days": class_days,
    }

    save_to_csv()
    refresh_listbox()

    show_popup(tr("success"), tr("add_success"))
    show_main()


# ============================================================
# SECTION 5: EDIT STUDENT, LEVELS & DELETE
# ============================================================

def edit_total_sessions():
    try:
        return int(sessions_entry.text)
    except (ValueError, AttributeError):
        return 0


def build_edit_page():
    global edit_step_box

    root = make_page()

    back = make_button(tr("back"), bg=BG_MAIN, height=dp(45), font_size=dp(14))
    tk_place(back, root, 15, 15, 180, 45)
    root.add_widget(back)
    back.bind(on_release=lambda *_: show_main())

    title = make_label(tr("edit_title"), bg=RED, height=dp(45), font_size=FONT_BOLD)
    tk_place(title, root, 15, 75, 960, 45)
    root.add_widget(title)

    info = FloatLayout()
    set_widget_background(info, BG_SECOND)
    tk_place(info, root, 0, 45, 1000, 500)
    root.add_widget(info)

    def add_label(text, x, y, w=220):
        l = make_label(text, bg=RED, fg=TEXT_LIGHT, height=dp(55), font_size=dp(14))
        l.halign = "left"
        tk_place(l, info, x, y, w, 55)
        info.add_widget(l)

    add_label(tr("name"), 15, 80)
    add_label(tr("sessions_week"), 490, 80, 200)
    add_label(tr("sessions_in_term"), 15, 155)
    add_label(tr("level"), 490, 155, 200)
    add_label(tr("note"), 15, 230)
    add_label(tr("labels"), 490, 230, 200)

    e_name = make_input()
    tk_place(e_name, info, 255, 80, 220, 55)
    info.add_widget(e_name)

    e_sessions = Spinner(text="", values=[str(x) for x in range(1, 8)], size_hint=(None, None),
                         height=dp(55), font_size=dp(14), font_name=FONT_NAME, background_normal="",
                         background_color=color_tuple(ENTRY_BG), color=color_tuple(TEXT_DARK))
    tk_place(e_sessions, info, 710, 80, 240, 55)
    info.add_widget(e_sessions)

    e_term = make_input()
    tk_place(e_term, info, 255, 155, 220, 55)
    info.add_widget(e_term)

    e_level = Spinner(text="", values=level_list, size_hint=(None, None), height=dp(55),
                      font_size=dp(14), font_name=FONT_NAME, background_normal="",
                      background_color=color_tuple(ENTRY_BG), color=color_tuple(TEXT_DARK))
    tk_place(e_level, info, 710, 155, 210, 55)
    info.add_widget(e_level)

    edit_levels = make_button(tr("edit_levels"), bg=BG_MAIN, height=dp(55), font_size=dp(14))
    tk_place(edit_levels, info, 925, 155, 75, 55)
    info.add_widget(edit_levels)
    edit_levels.bind(on_release=lambda *_: level_edit_clicked())

    e_note = make_input()
    tk_place(e_note, info, 255, 230, 220, 55)
    info.add_widget(e_note)

    e_labels = GridLayout(cols=1, spacing=0, size_hint=(None, None))
    e_labels.bind(minimum_height=e_labels.setter("height"))
    label_scroll = ScrollView(do_scroll_y=True, do_scroll_x=False, size_hint=(None, None))
    tk_place(label_scroll, info, 710, 230, 245, 55)
    label_scroll.add_widget(e_labels)
    info.add_widget(label_scroll)

    next_btn = make_button(tr("next"), bg=BG_MAIN, height=dp(55), font_size=FONT_BOLD)
    tk_place(next_btn, info, 15, 380, 960, 55)
    info.add_widget(next_btn)
    next_btn.bind(on_release=lambda *_: edit_info_next())

    edit_step_box = FloatLayout()
    set_widget_background(edit_step_box, BG_SECOND)
    tk_place(edit_step_box, root, 0, 135, 1000, 500)
    root.add_widget(edit_step_box)
    edit_step_box.opacity = 0
    edit_step_box.disabled = True

    edit_steps[0] = info
    edit_widgets.update({
        "name_entry": e_name,
        "sessions_entry": e_sessions,
        "term_entry": e_term,
        "note_entry": e_note,
        "labels_entry": e_labels,
        "level_entry": e_level,
    })
    # Keep navigation controls above the form layer.
    root.remove_widget(back)
    root.remove_widget(title)
    root.add_widget(back)
    root.add_widget(title)

    pages["edit"] = root

def edit_clicked():
    global old_name, add_session_mode
    global name_entry, sessions_entry, term_entry, note_entry, labels_entry, level_entry

    if not selected_index or selected_index not in students_dict:
        show_popup(tr("error"), tr("err_select_first"))
        return

    old_name = selected_index
    add_session_mode = "edit"

    if "edit" not in pages:
        build_edit_page()

    # Restore the Edit page's own widgets.
    name_entry = edit_widgets["name_entry"]
    sessions_entry = edit_widgets["sessions_entry"]
    term_entry = edit_widgets["term_entry"]
    note_entry = edit_widgets["note_entry"]
    labels_entry = edit_widgets["labels_entry"]
    level_entry = edit_widgets["level_entry"]

    student = students_dict[old_name]

    name_entry.text = old_name
    sessions_entry.text = str(student["sessions_per_week"])
    sessions_entry.values = [str(x) for x in range(1, 8)]
    level_entry.text = student["level"]
    term_entry.text = str(student["term"])
    note_entry.text = str(student["note"])

    labels_entry.clear_widgets()
    for label in saved_labels:
        b = make_button(
            label,
            bg=BG_SECOND if label in student["labels"] else BG_LIGHT,
            fg=TEXT_LIGHT if label in student["labels"] else TEXT_DARK,
            height=dp(27),
            font_size=dp(13),
        )
        b.selected_for_labels = label in student["labels"]

        def toggle(widget, label=label):
            widget.selected_for_labels = not widget.selected_for_labels
            if widget.selected_for_labels:
                widget.background_color = color_tuple(BG_SECOND)
                widget.color = color_tuple(TEXT_LIGHT)
            else:
                widget.background_color = color_tuple(BG_LIGHT)
                widget.color = color_tuple(TEXT_DARK)

        b.bind(on_release=toggle)
        labels_entry.add_widget(b)

    build_session_steps_kivy(edit_steps, edit_day_combos, edit_next_btns, 0, None, add=False)
    show_page("edit")
    show_step(edit_steps, 0, edit_next_btns)

def edit_info_next():
    new_name = name_entry.text.strip()
    new_sessions = sessions_entry.text.strip()
    new_level = level_entry.text.strip()
    new_term = term_entry.text.strip()
    new_note = note_entry.text.strip()

    if not new_name or not new_sessions or not new_level or not new_term:
        show_popup(tr("error"), tr("err_all_fields"))
        return

    if not new_name.replace(" ", "").isalpha():
        show_popup(tr("error"), tr("err_name_letters"))
        return

    if not new_term.isdigit():
        show_popup(tr("error"), tr("err_term_number"))
        return

    original_sessions = students_dict[old_name]["sessions_per_week"]

    if int(new_sessions) == original_sessions:
        submit_edit()
        return

    old_days = students_dict[old_name].get("class_days", [])

    build_session_steps_kivy(
        edit_steps,
        edit_day_combos,
        edit_next_btns,
        int(new_sessions),
        old_days,
        add=False,
    )

    show_step(edit_steps, 1, edit_next_btns)


def submit_edit():
    new_name = name_entry.text.strip()
    new_sessions = int(sessions_entry.text)
    new_level = level_entry.text.strip()
    new_term = int(term_entry.text.strip())
    new_note = note_entry.text.strip()

    selected_labels = selected_labels_from_box()

    if edit_day_combos:
        class_days = [
            combo_to_en(edit_day_combos[i].text)
            for i in range(1, new_sessions + 1)
        ]
    else:
        class_days = students_dict[old_name].get("class_days", [])

    original_term = students_dict[old_name]["original_term"]
    pending_sessions = students_dict[old_name]["pending_sessions"]

    del students_dict[old_name]

    students_dict[new_name] = {
        "sessions_per_week": new_sessions,
        "level": new_level,
        "term": new_term,
        "original_term": original_term,
        "pending_sessions": pending_sessions,
        "note": new_note,
        "labels": selected_labels,
        "class_days": class_days,
    }

    save_to_csv()
    refresh_listbox()

    show_popup(tr("success"), tr("edit_success"))
    show_main()


def delete_clicked():
    if not selected_index or selected_index not in students_dict:
        show_popup(tr("error"), tr("err_select_first"))
        return

    name = selected_index

    def do_delete():
        if name in students_dict:
            del students_dict[name]

        df = read_combined()
        if "Name" in df.columns:
            df = df[df["Name"] != name]
        write_combined(df)

        save_to_csv()
        refresh_listbox()
        show_main()

    confirm_popup(tr("confirm"), tr("delete_confirm"), do_delete)


def level_edit_clicked():
    global level_list, level_entry, levels_return_page
    levels_return_page = "edit" if add_session_mode == "edit" else "add"
    if "levels" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: return_from_levels())
        title=make_label(tr("levels_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)

        list_scroll=ScrollView(do_scroll_y=True,size_hint=(None,None)); tk_place(list_scroll,root,15,135,960,400)
        level_grid=GridLayout(cols=1,spacing=0,size_hint_y=None); level_grid.bind(minimum_height=level_grid.setter("height")); list_scroll.add_widget(level_grid); root.add_widget(list_scroll)

        entry=make_input(); tk_place(entry,root,15,555,500,50); root.add_widget(entry)
        selected={"index":None}

        def refresh():
            level_grid.clear_widgets()
            for i,item in enumerate(level_list):
                b=make_button(item,bg=BG_LIGHT,fg=TEXT_DARK,height=dp(27),font_size=dp(14))
                b.halign="left"
                b.bind(on_release=lambda _,idx=i: choose(idx))
                level_grid.add_widget(b)
        def choose(idx):
            selected["index"]=idx; entry.text=level_list[idx]
        def add_level(*_):
            text=entry.text.strip()
            if text and text not in level_list: level_list.append(text); entry.text=""; refresh()
        def rename_level(*_):
            idx=selected["index"]; text=entry.text.strip()
            if idx is not None and text and text not in level_list:
                old=level_list[idx]; level_list[idx]=text
                for info in students_dict.values():
                    if info["level"]==old: info["level"]=text
                save_to_csv(); selected["index"]=None; entry.text=""; refresh()
        def delete_level(*_):
            idx=selected["index"]
            if idx is None:return
            item=level_list[idx]
            def really():
                level_list.remove(item); selected["index"]=None; entry.text=""; refresh()
            confirm_popup(tr("confirm"),tr("delete_level_confirm"),really)
        add=make_button(tr("add"),bg=RED,height=dp(50)); tk_place(add,root,530,555,215,50); root.add_widget(add); add.bind(on_release=add_level)
        ren=make_button(tr("rename"),bg=RED,height=dp(50)); tk_place(ren,root,760,555,215,50); root.add_widget(ren); ren.bind(on_release=rename_level)
        pages["levels"]=root
        root._refresh_levels=refresh
    root=pages["levels"]; show_page("levels"); root._refresh_levels()



def return_from_levels():
    """Return to the Add/Edit page that opened the Levels screen."""
    global name_entry, sessions_entry, term_entry, note_entry, labels_entry, level_entry
    target = levels_return_page if levels_return_page in pages else "main"
    if target == "add" and add_widgets:
        name_entry = add_widgets.get("name_entry")
        sessions_entry = add_widgets.get("sessions_entry")
        term_entry = add_widgets.get("term_entry")
        note_entry = add_widgets.get("note_entry")
        labels_entry = add_widgets.get("labels_entry")
        level_entry = add_widgets.get("level_entry")
    elif target == "edit" and edit_widgets:
        name_entry = edit_widgets.get("name_entry")
        sessions_entry = edit_widgets.get("sessions_entry")
        term_entry = edit_widgets.get("term_entry")
        note_entry = edit_widgets.get("note_entry")
        labels_entry = edit_widgets.get("labels_entry")
        level_entry = edit_widgets.get("level_entry")
    show_page(target)

def updatebtn_clicked():
    global update_listbox, reports_search_entry
    if "update" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: show_main())
        title=make_label(tr("reports_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)
        reports_search_entry = make_live_search(root, "Search students...", lambda value: refresh_update_list(value), 15, 125, 960)
        scroll=ScrollView(do_scroll_y=True,size_hint=(None,None)); tk_place(scroll,root,15,185,960,552)
        update_listbox=GridLayout(cols=1,spacing=0,size_hint_y=None); update_listbox.bind(minimum_height=update_listbox.setter("height")); scroll.add_widget(update_listbox); root.add_widget(scroll)
        pages["update"]=root
    show_page("update"); refresh_update_list()

def refresh_update_list(query=""):
    if update_listbox is None:return
    update_listbox.clear_widgets()
    students=sorted([(remaining_sessions(n),n) for n in students_dict if not query.strip() or query.lower() in n.lower()],key=lambda x:(x[0],x[1]))
    if not students:
        show_not_found(update_listbox)
        return
    for remain,name in students:
        b=make_button(tr("sessions_left").format(name=name,count=remain),bg=RED if remain<=0 else ENTRY_BG,fg=TEXT_DARK,height=dp(27),font_size=dp(14))
        b.halign="left"
        b.bind(on_release=lambda _,n=name,r=remain: renew_student(n) if r<=0 else None)
        update_listbox.add_widget(b)

def renew_student(name):
    def do_renew():
        student = students_dict[name]

        student["term"] = (
            student["original_term"]
            - student["pending_sessions"]
        )
        student["pending_sessions"] = 0

        df = read_combined()

        if "Pending" in df.columns and "Settled" in df.columns:
            df["Pending"] = df["Pending"].astype(str)
            df["Settled"] = df["Settled"].astype(str)

            mask = (
                (df["Name"] == name) &
                (df["Pending"].str.lower() == "true") &
                (df["Settled"].str.lower() == "false")
            )

            df.loc[mask, "Settled"] = True
            write_combined(df)

        save_to_csv()
        refresh_stats()
        refresh_update_list()

    confirm_popup(tr("renew"), tr("renew_question"), do_renew)


# ============================================================
# SECTION 7: CALENDAR & ATTENDANCE
# ============================================================

def calendar_clicked():
    global calendar_grid, calendar_search_entry
    if "calendar" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: show_main())
        title=make_label(tr("calendar_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)
        calendar_search_entry = make_live_search(root, "Search students...", lambda value: refresh_calendar(value), 15, 125, 960)
        scroll=ScrollView(do_scroll_x=True,do_scroll_y=True,size_hint=(None,None)); tk_place(scroll,root,15,185,960,510)
        calendar_grid=GridLayout(cols=8,spacing=1,size_hint=(None,None),width=760); calendar_grid.bind(minimum_height=calendar_grid.setter("height")); scroll.add_widget(calendar_grid); root.add_widget(scroll)
        pages["calendar"]=root
    show_page("calendar")
    refresh_calendar(calendar_search_entry.text if calendar_search_entry else "")


def refresh_calendar(query=""):
    if calendar_grid is None:
        return
    calendar_grid.clear_widgets()
    q = query.strip().lower()
    matched = [(name, info) for name, info in students_dict.items() if not q or q in name.lower()]
    if not matched:
        show_not_found(calendar_grid)
        return

    headers = [tr("col_name")] + [tr("day_" + d) for d in days_list]
    widths = [200] + [80] * 7
    for text, width in zip(headers, widths):
        cell = make_label(text, bg=BG_MAIN, fg=TEXT_DARK, height=dp(35), font_size=dp(14))
        cell.size_hint_x = None
        cell.width = dp(width)
        calendar_grid.add_widget(cell)

    for name, info in matched:
        cell = make_label(name, bg=TEXT_LIGHT, fg=TEXT_DARK, height=dp(35), font_size=dp(14))
        cell.size_hint_x = None
        cell.width = dp(200)
        calendar_grid.add_widget(cell)
        for day in days_list:
            cell = make_label(
                "✓" if day in info.get("class_days", []) else "",
                bg=TEXT_LIGHT, fg=BG_LINE, height=dp(35), font_size=dp(14)
            )
            cell.size_hint_x = None
            cell.width = dp(80)
            calendar_grid.add_widget(cell)

def attendance_clicked():
    global attendance_student, attendance_question_label, attendance_today_check
    global attendance_listbox, attendance_date, attendance_date_widget, attendance_search_entry

    if not selected_index or selected_index not in students_dict:
        return

    attendance_student = selected_index

    if "attendance" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: show_main())
        title=make_label(tr("attendance_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)
        attendance_search_entry = make_live_search(root, "Search dates...", lambda value: refresh_attendance(value), 15, 300, 590)

        attendance_question_label=make_label("",bg=BG_SECOND,fg=TEXT_LIGHT,height=dp(50),font_size=FONT_BOLD); attendance_question_label.halign="left"; tk_place(attendance_question_label,root,15,135,700,50); root.add_widget(attendance_question_label)

        attendance_today_check=CheckBox(active=False,size_hint=(None,None),size=(dp(25),dp(25)))
        tk_place(attendance_today_check,root,15,195,35,35); root.add_widget(attendance_today_check)
        today_label=make_label(tr("today"),bg=BG_SECOND,height=dp(35),font_size=dp(14)); today_label.halign="left"; tk_place(today_label,root,50,195,150,35); root.add_widget(today_label)

        or_label=make_label(tr("or_enter_date"),bg=BG_SECOND,height=dp(45),font_size=dp(14)); or_label.halign="left"; tk_place(or_label,root,15,245,170,45); root.add_widget(or_label)
        attendance_date_widget=TextInput(text="",readonly=True,size_hint=(None,None),height=dp(45),font_size=dp(14),font_name=FONT_NAME,background_color=color_tuple(TEXT_LIGHT),foreground_color=color_tuple(TEXT_DARK),halign="center")
        tk_place(attendance_date_widget,root,195,240,240,45); root.add_widget(attendance_date_widget)
        pick=make_button(tr("pick_date"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(pick,root,455,240,150,45); root.add_widget(pick); pick.bind(on_release=lambda *_: open_date_picker())

        scroll=ScrollView(do_scroll_y=True,size_hint=(None,None)); tk_place(scroll,root,15,350,590,245)
        attendance_listbox=GridLayout(cols=1,spacing=0,size_hint_y=None); attendance_listbox.bind(minimum_height=attendance_listbox.setter("height")); scroll.add_widget(attendance_listbox); root.add_widget(scroll)

        save=make_button(tr("save"),bg=BG_MAIN,height=dp(55),font_size=FONT_BOLD); tk_place(save,root,15,630,590,55); root.add_widget(save); save.bind(on_release=lambda *_: save_attendance())
        pages["attendance"]=root

    show_page("attendance")
    attendance_question_label.text=rtl_text(tr("attendance_question").format(name=attendance_student))
    attendance_today_check.active=False
    attendance_date=""
    attendance_date_widget.text=""
    refresh_attendance()

def refresh_attendance(query=""):
    if attendance_listbox is None:
        return

    attendance_listbox.clear_widgets()

    df = read_combined()

    if "RecordType" in df.columns:
        df = df[df["RecordType"] == "attendance"]

    if "Pending" not in df.columns:
        df["Pending"] = False
    if "Settled" not in df.columns:
        df["Settled"] = False

    student_rows = df[df["Name"] == attendance_student]
    if query.strip():
        student_rows = student_rows[student_rows["Date"].astype(str).str.contains(query.strip(), case=False, na=False)]
    if student_rows.empty:
        show_not_found(attendance_listbox)
        return

    for row_index, row in student_rows.iterrows():
        text = str(row["Date"])

        pending = str(row["Pending"]).lower()
        settled = str(row["Settled"]).lower()

        if pending == "true":
            if settled == "true":
                text += tr("pending_settled")
            else:
                text += tr("pending_not_settled")

        b = make_button(
            text,
            bg=TEXT_LIGHT,
            fg=TEXT_DARK,
            height=dp(45),
            font_size=dp(14),
        )
        b.bind(
            on_release=lambda _, idx=row_index:
            delete_attendance_row(idx)
        )
        attendance_listbox.add_widget(b)


def delete_attendance_row(row_index):
    def do_delete():
        df = read_combined()

        if row_index not in df.index:
            return

        df = df.drop(row_index)
        write_combined(df)
        refresh_attendance()

    confirm_popup(
        tr("confirm"),
        tr("delete_attendance_confirm"),
        do_delete,
    )


def save_attendance():
    if attendance_date_widget is None or attendance_today_check is None:
        show_popup(tr("error"), tr("err_select_first"))
        return

    entered_date = attendance_date_widget.text.strip()

    if entered_date:
        date = entered_date
    elif attendance_today_check.active:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        return

    def do_save():
        student = students_dict[attendance_student]

        if student["term"] > 0:
            student["term"] -= 1
            pending = False
        else:
            student["pending_sessions"] += 1
            pending = True

        save_attendance_to_csv(
            attendance_student,
            date,
            pending,
        )

        save_to_csv()
        refresh_stats()
        refresh_attendance()
        refresh_update_list()

        attendance_date_widget.text = ""

        show_popup(
            tr("success"),
            tr("attended_on").format(
                name=attendance_student,
                date=date,
            ),
        )

    confirm_popup(
        tr("attendance_title"),
        tr("attendance_confirm"),
        do_save,
    )


def open_date_picker():
    if attendance_date_widget is None:
        return

    today = datetime.now().date()
    current = {
        "year": today.year,
        "month": today.month,
    }

    root = BoxLayout(
        orientation="vertical",
        spacing=dp(5),
        padding=dp(5),
    )

    nav = BoxLayout(
        size_hint_y=None,
        height=dp(50),
        spacing=dp(5),
    )

    month_label = make_label(
        "",
        bg=BG_SECOND,
        height=dp(50),
        font_size=FONT_BOLD,
    )

    grid = GridLayout(
        cols=7,
        spacing=dp(2),
        size_hint_y=None,
    )
    grid.bind(minimum_height=grid.setter("height"))

    root.add_widget(nav)
    root.add_widget(grid)

    popup = Popup(
        title=tr("pick_date"),
        content=root,
        size_hint=(None, None),
        size=(dp(600), dp(550)),
    )

    def render():
        month_label.text = rtl_text(
            f"{current['year']:04d} / {current['month']:02d}"
        )

        grid.clear_widgets()

        for name in local_days():
            grid.add_widget(
                make_label(
                    name[:3],
                    bg=RED,
                    height=dp(40),
                    font_size=dp(13),
                )
            )

        cal = cal_mod.Calendar(firstweekday=5)

        for week in cal.monthdayscalendar(
            current["year"],
            current["month"]
        ):
            for day in week:
                if day == 0:
                    grid.add_widget(
                        make_label(
                            "",
                            bg=TEXT_LIGHT,
                            height=dp(40),
                        )
                    )
                else:
                    b = make_button(
                        str(day),
                        bg=BG_MAIN,
                        height=dp(40),
                        font_size=dp(14),
                    )
                    b.bind(
                        on_release=lambda _, d=day:
                        pick_date(d)
                    )
                    grid.add_widget(b)

    def change_month(step):
        month = current["month"] + step
        year = current["year"]

        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        current["year"] = year
        current["month"] = month
        render()

    def pick_date(day):
        global attendance_date

        attendance_date = (
            f"{current['year']:04d}-"
            f"{current['month']:02d}-"
            f"{day:02d}"
        )

        attendance_date_widget.text = attendance_date
        popup.dismiss()

    prev_btn = make_button("◀", bg=BG_MAIN, height=dp(50))
    next_btn = make_button("▶", bg=BG_MAIN, height=dp(50))

    prev_btn.bind(on_release=lambda *_: change_month(-1))
    next_btn.bind(on_release=lambda *_: change_month(1))

    nav.add_widget(prev_btn)
    nav.add_widget(month_label)
    nav.add_widget(next_btn)

    render()
    popup.open()


# ============================================================
# SECTION 8: SETTINGS & HELP
# ============================================================

def helpbtn_clicked():
    if "help" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: show_main())
        title=make_label(tr("help_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)
        text=make_label(tr("help_text"),bg=BG_SECOND,fg=TEXT_LIGHT,height=dp(500),font_size=dp(14)); text.halign="left"; text.valign="top"
        tk_place(text,root,15,135,700,500); root.add_widget(text)
        pages["help"]=root
    show_page("help")

def export_excel():
    try:
        df = read_combined()
        df.to_excel(
            "combined_data.xlsx",
            index=False,
        )

        show_popup(
            tr("success"),
            tr("export_success"),
        )

    except Exception:
        show_popup(
            tr("error"),
            tr("export_fail"),
        )


def settings_clicked():
    global lang
    if "settings" not in pages:
        root=make_page()
        back=make_button(tr("back"),bg=BG_MAIN,height=dp(45),font_size=dp(14)); tk_place(back,root,15,15,180,45); root.add_widget(back); back.bind(on_release=lambda *_: show_main())
        title=make_label(tr("settings_title"),bg=RED,height=dp(45),font_size=FONT_BOLD); tk_place(title,root,15,75,960,45); root.add_widget(title)
        lab=make_label(tr("language"),bg=BG_SECOND,height=dp(60),font_size=dp(14)); lab.halign="left"; tk_place(lab,root,15,165,240,60); root.add_widget(lab)
        spinner=Spinner(text="en" if lang=="en" else "fa",values=["en","fa"],size_hint=(None,None),height=dp(60),font_size=dp(14),background_normal="",background_color=color_tuple(ENTRY_BG),color=color_tuple(TEXT_DARK)); tk_place(spinner,root,275,165,180,60); root.add_widget(spinner)
        export=make_button(tr("export_btn"),bg=RED,height=dp(65),font_size=FONT_BOLD); tk_place(export,root,15,285,260,65); root.add_widget(export); export.bind(on_release=lambda *_: export_excel())
        desc=make_label(tr("export_section"),bg=BG_SECOND,fg=TEXT_LIGHT,height=dp(70),font_size=dp(14)); desc.halign="left"; tk_place(desc,root,295,285,480,70); root.add_widget(desc)
        def changed(_,value):
            global lang
            if value!=lang:
                lang=value; rebuild_all_ui()
        spinner.bind(text=changed); pages["settings"]=root
    show_page("settings")

def rebuild_all_ui():
    """Kivy replacement for destroying/reconfiguring all Tkinter pages."""
    global pages, stats_labels

    # Keep data; rebuild only widgets.
    for widget in list(pages.values()):
        if widget.parent:
            widget.parent.remove_widget(widget)

    pages.clear()
    stats_labels.clear()

    setup_main_window()
    root_manager.clear_widgets()

    rebuild_filter_bar()
    refresh_listbox()
    show_main()


# ============================================================
# MAIN KIVY APP
# ============================================================

class AttendanceApp(App):
    def build(self):
        load_data()
        load_labels()

        Window.size = (1000, 1000)

        global root_manager
        root_manager = FloatLayout()

        setup_main_window()

        rebuild_filter_bar()
        refresh_listbox()
        show_main()

        return root_manager

    def on_start(self):
        show_main()


if __name__ == "__main__":
    AttendanceApp().run()