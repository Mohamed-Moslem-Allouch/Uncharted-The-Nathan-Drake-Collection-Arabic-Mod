# UNCHARTED: The Nathan Drake Collection - Complete PC Arabic Localization Mod
### تعريب ثلاثية أنشارتد الكاملة للكمبيوتر (PC Port)

[![Release](https://img.shields.io/github/v/release/Mohamed-Moslem-Allouch/Uncharted-The-Nathan-Drake-Collection-Arabic-Mod?color=success&style=for-the-badge)](https://github.com/Mohamed-Moslem-Allouch/Uncharted-The-Nathan-Drake-Collection-Arabic-Mod/releases)
[![Platform](https://img.shields.io/badge/Platform-PC%20Windows-blue?style=for-the-badge&logo=windows)](https://github.com/Mohamed-Moslem-Allouch/Uncharted-The-Nathan-Drake-Collection-Arabic-Mod)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Mohamed%20Moslem%20Allouch-gold?style=for-the-badge)](https://github.com/Mohamed-Moslem-Allouch)

---

## 🌟 نبذة عن المشروع (Project Overview)
مود التعريب الكامل والنهائي لثلاثية **أنشارتد (Uncharted: The Nathan Drake Collection)** لنسخة الحاسب الشخصي (PC).
تمت هندسة التعريب عكسياً وبناؤه برمجياً مباشرة داخل ملفات اللعبة الأصلية ليقدم تجربة أصلية متكاملة وسلسة باللغة العربية الفصحى دون أي مشاكل تقنية.

**تعريب وبرمجة:** محمد مسلم علوش (**Mohamed Moslem Allouch**)

---

## 🎮 ميزات التعريب (Key Features)

1. **شامل للثلاثية الكاملة (Complete Trilogy Support):**
   * **Uncharted 1: Drake's Fortune™** (أنشارتد 1: حظ دريك)
   * **Uncharted 2: Among Thieves™** (أنشارتد 2: بين اللصوص)
   * **Uncharted 3: Drake's Deception™** (أنشارتد 3: خداع دريك)
2. **ترجمة الحوارات والنصوص (Subtitles & Story):**
   * ترجمة كاملة بنسبة 100% لكافة المشاهد السينمائية، الحوارات، الملاحظات واليوميات.
   * ضبط المصطلحات والأسماء القصصية لتبقى متطابقة مع سياق القصة وشخصياتها.
3. **تعريب القوائم والإعدادات (UI & Menus):**
   * تعريب كامل وشامل لجميع القوائم الرئيسية، قوائم الإيقاف المؤقت، إعدادات الصوت والصورة، أزرار التحكم وشاشات المكافآت (Skins, Treasures, Medals, Render Modes).
   * إصلاح مفاتيح التبديل (تشغيل / إيقاف) لتكون دقيقة ومثالية.
4. **أطلس خطوط عالي الدقة (Custom BMFont Atlas):**
   * توليد أطلس خط عربي أصلي بدقة **1024×1024** بخط Bold عريض ومحاذاة رأسية دقيقة لخط الأساس (Baseline Alignment).
   * خلو تام من تداخل السطور، الحروف المتقطعة، أو أي رموز هبوط.
5. **معالجة متقدمة لاتجاه النصوص (BiDi & Presentation Forms):**
   * تشكيل وربط الحروف العربية برمجياً وعكس ترتيبها بما يتوافق مع معالجة محرك Naughty Dog لليسار-إلى-اليمين (LTR).
   * حماية تامة لكافة علامات الأزرار والـ Tags مثل `|ENTER|`, `|X|`, `|S|`, `|T|`, `|C|`.
   * خلو تام من الرموز العشوائية أو علامات `@ @`.
6. **الحفاظ على الأصوات الأصلية (Original English Voices):**
   * الإبقاء على الأصوات الإنجليزية الأصلية دون أي مساس، مع إتاحة قراءة النصوص والترجمات بالعربية.

---

## 📥 طريقة التثبيت السريعة (Installation Guide)

### الطريقة الأولى: التثبيت التلقائي (الموصى به)
1. قم بتحميل أرشيف التعريب من صفحة [Releases](../../releases) باسم:
   `Uncharted_The_Nathan_Drake_Collection_Arabic_Mod.zip`.
2. فك الضغط عن الملف بجوار مجلد اللعبة.
3. شغل ملف **`Install_Arabic_Mod.bat`** ليقوم بنسخ واستبدال الملفات تلقائياً.

### الطريقة الثانية: النسخ واللصق اليدوي (Manual Copy & Paste)
1. انسخ مجلد `Game` الموجود داخل هذا المستودع.
2. الصقه داخل مجلد اللعبة الرئيسي:
   `D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\`
3. وافق على استبدال جميع الملفات عند المطالبة.

---

## ⚙️ التفعيل داخل اللعبة (In-Game Activation)
1. شغل اللعبة.
2. من القائمة الرئيسية، توجه إلى **Options (الخيارات)** ثم **Language (اللغة)**:
   * اضبط **Text (النص)**: `العربية`
   * اضبط **Subtitles (الترجمة)**: `تشغيل`
   * اترك **Speech (الحوار)**: `English` للاستمتاع بالأصوات الإنجليزية الأصلية.

---

## 🛠️ البناء والهندسة العكسية (Technical Architecture)
تتوفر جميع أدوات الهندسة العكسية والمعالجة داخل مجلد [`tools/`](tools/):
* `arabic_text_processor.py`: معالج ربط وتشكيل النصوص العربية وعكس BiDi مع حماية وسوم أزرار التحكم.
* `psarc_tool.py`: أداة تفكيك وتعديل وحزم أرشيفات سوني `PSARC` وتحديث جداول النصوص الثنائية.
* `rebuild_all_fonts.py`: مولد خريطة أطلس الخطوط النقطية BMFont بدقة 1024×1024.
* `fix_all_trilogy_arabic.py`: المعالج الرئيسي لبناء جداول النصوص للأجزاء الثلاثة بالكامل.

---

## 👤 حقوق المطور والتعريب (Author & Credits)
* **تعريب وبرمجة:** محمد مسلم علوش (**Mohamed Moslem Allouch**)
* **GitHub Profile:** [@Mohamed-Moslem-Allouch](https://github.com/Mohamed-Moslem-Allouch)
* **Email:** medmoslem11@gmail.com
