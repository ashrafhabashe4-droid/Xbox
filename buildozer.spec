
اره بگو چطور اندرویدی بسازمش
بریم مهدی! این بار از صفر و با مسیر درست پیش می‌ریم. 😁

چون فقط گوشی داری، از GitHub Actions برای ساخت APK در فضای ابری استفاده می‌کنیم.

یک نکته مهم: فایل پایتون ترمینالی فعلی مستقیماً APK نمی‌شود. برای اندروید باید یک رابط گرافیکی بسازیم. برای یادگیری، ابتدا یک برنامه آزمایشی ساده با Kivy می‌سازیم.

مرحله اول: آماده‌سازی پروژه
بهتره یک Repository جدید با نام android-python-demo بسازی تا پروژه آزمایشی از فایل قبلی جدا باشد.

ساختار پروژه باید این شکلی باشد:

android-python-demo/
│
├── main.py
├── buildozer.spec
└── .github/
    └── workflows/
        └── android.yml
مرحله دوم: ساخت فایل main.py
در GitHub:

وارد Repository جدید شو.

روی Add file بزن.

گزینه Create new file را انتخاب کن.

اسم فایل را main.py بگذار.

این کد آزمایشی را داخلش قرار بده:


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        title = Label(
            text="My First Android App",
            font_size=24
        )

        button = Button(
            text="سلام مهدی!",
            font_size=22
        )

        layout.add_widget(title)
        layout.add_widget(button)

        return layout

MyApp().run()


روی Commit changes بزن.

مرحله سوم: ساخت فایل تنظیمات
دوباره Create new file را بزن و اسمش را بگذار:

buildozer.spec

محتوای زیر را قرار بده:


[app]

title = My Android App
package.name = myapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv

version = 1.0

requirements = python3,kivy

orientation = portrait

fullscreen = 0

[buildozer]

log_level = 2

warn_on_root = 1

[android]

android.api = 35
android.minapi = 23
