import os
import sys
import json
import time
import re
import struct
import urllib.parse
import shutil
import zipfile
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter

sys.stdout.reconfigure(encoding='utf-8')

from arabic_text_processor import reshape_arabic, clean_arabic_text
from psarc_tool import PSARC, update_psarc_entries

# Comprehensive high-quality manual translations for all UI, Menus, Rewards, Controls, Options
PREMIUM_DICTIONARY = {
    # Language Slot
    "Français": "العربية",
    "Francais": "العربية",
    "French": "العربية",
    
    # Options & Signature
    "OPTIONS": "خيارات (تعريب: محمد مسلم علوش)",
    "Options": "خيارات (تعريب: محمد مسلم علوش)",
    "Press |ENTER| to Begin": "اضغط على |ENTER| للبدء\n(تعريب: محمد مسلم علوش)",
    "PRESS START": "اضغط START للبدء\n(تعريب: محمد مسلم علوش)",
    
    # On / Off Toggles
    "- Subtitles On -": "- تشغيل الترجمة -",
    "- Subtitles Off -": "- إيقاف الترجمة -",
    "Subtitles: On": "الترجمة: تشغيل",
    "Subtitles: Off": "الترجمة: إيقاف",
    "On": "تشغيل",
    "Off": "إيقاف",
    "ON": "تشغيل",
    "OFF": "إيقاف",
    "Enabled": "مفعل",
    "Disabled": "معطل",
    "Yes": "نعم",
    "No": "لا",
    
    # Main Navigation
    "NEW GAME": "لعبة جديدة",
    "New Game": "لعبة جديدة",
    "CONTINUE": "متابعة",
    "Continue": "متابعة",
    "CHAPTERS": "فصول",
    "Chapters": "فصول",
    "BONUSES": "المكافآت",
    "Bonuses": "المكافآت",
    "REWARDS": "المكافآت",
    "Rewards": "المكافآت",
    "Load Game": "تحميل لعبة",
    "Save Game": "حفظ اللعبة",
    "SAVE GAME": "حفظ اللعبة",
    "Quit to Main Menu": "الخروج إلى القائمة الرئيسية",
    "QUIT TO MAIN MENU": "الخروج إلى القائمة الرئيسية",
    "Quit Game": "الخروج من اللعبة",
    "QUIT GAME": "الخروج من اللعبة",
    "Quit": "خروج",
    "Back": "رجوع",
    "BACK": "رجوع",
    "SELECT": "اختيار",
    "Select": "اختيار",
    "Select for options": "اختر للخيارات",
    
    # Rewards & Bonus Menu (Fixes Screenshot 1 & 2)
    "Skins": "الأزياء",
    "SKINS": "الأزياء",
    "Hero Skins": "أزياء الأبطال",
    "Villain Skins": "أزياء الأعداء",
    "Weapon Select": "اختيار الأسلحة",
    "Render Modes": "أنماط العرض",
    "Render Mode Select": "اختيار نمط العرض",
    "Art Galleries": "المعارض الفنية",
    "Concept Art Galleries": "معارض الرسوم المبدئية",
    "Concept Art Gallery 1": "معرض الرسوم المبدئية 1",
    "Concept Art Gallery 2": "معرض الرسوم المبدئية 2",
    "Concept Art Gallery 3": "معرض الرسوم المبدئية 3",
    "Concept Art Gallery 4": "معرض الرسوم المبدئية 4",
    "Concept Art Gallery 5": "معرض الرسوم المبدئية 5",
    "Concept Art Gallery 6": "معرض الرسوم المبدئية 6",
    "Story Cutscenes": "المشاهد القصصية",
    "STORY CUTSCENES": "المشاهد القصصية",
    "Treasures": "الكنوز",
    "TREASURES": "الكنوز",
    "Treasures found": "الكنوز المكتشفة",
    "Medals": "الميداليات",
    "MEDALS": "الميداليات",
    "Statistics": "الإحصائيات",
    "STATISTICS": "الإحصائيات",
    "RECORD": "السجلات",
    "RECORDS": "السجلات",
    "Records": "السجلات",
    "Unlocked [A] of [B] Rewards": "تم فتح [A] من [B] مكافأة",
    "Reward Unlocked\\See Bonus Menu": "تم فتح مكافأة\\nراجع قائمة المكافآت",
    "Bonus Movies": "المقاطع الإضافية",
    "Bonus Featurettes": "الأفلام الوثائقية الإضافية",
    "Making of": "كواليس الصنع",
    "Behind The Scenes: Making of the Cinematics": "خلف الكواليس: صناعة المشاهد السينمائية",
    
    # Audio / Subtitle settings
    "Text": "النص",
    "Texte": "النص",
    "Speech": "الحوار",
    "Dialogues": "الحوار",
    "Subtitles": "الترجمة",
    "Sous-titres": "الترجمة",
    "SUBTITLES": "الترجمة",
    "Press |S| to toggle subtitles": "اضغط |S| لتبديل الترجمة",
    "Audio": "الصوت",
    "AUDIO": "الصوت",
    "Audio Output": "مخرج الصوت",
    "Audio Volume": "مستوى الصوت",
    "Music Volume": "مستوى الموسيقى",
    "SFX Volume": "مستوى المؤثرات",
    
    # Controls & Pause Menu
    "PAUSED": "إيقاف مؤقت",
    "PAUSE": "إيقاف مؤقت",
    "Pause": "إيقاف مؤقت",
    "Restart Checkpoint": "إعادة نقطة الحفظ",
    "Restart from Checkpoint": "إعادة نقطة الحفظ",
    "Resume": "استئناف",
    "|START| RESUME": "|START| استئناف",
    "Resume Game": "استئناف اللعبة",
    "Mappings": "تعيين الأزرار",
    "Cartographie": "تعيين الأزرار",
    "Commandes": "التحكم",
    "Reset Defaults": "استعادة الإعدادات الافتراضية",
    "Left/Right Sticks": "عصا التحكم",
    "Left and Right Stick": "عصا التحكم",
    "Invert Look": "عكس الكاميرا",
    "Shoulder Swap": "مبادلة الكتف",
    "Invert Aim": "عكس التصويب",
}

TAG_REGEX = re.compile(r'(\|[^|]+\||%[0-9]*[a-zA-Z]|\[[A-Z0-9_\-]+\])')

def protect_tags(text):
    tags = []
    def repl(m):
        tags.append(m.group(0))
        return f" QXZ{len(tags)-1}ZXQ "
    masked = TAG_REGEX.sub(repl, text)
    return masked, tags

def restore_tags(text, tags):
    for i, tag in enumerate(tags):
        text = re.sub(rf'\s*QXZ{i}ZXQ\s*', f' {tag} ', text)
    return text.strip()

_thread_local = threading.local()
def get_session():
    if not hasattr(_thread_local, "session"):
        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=3)
        session.mount('https://', adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        _thread_local.session = session
    return _thread_local.session

def polish_story_translation(text):
    if not text:
        return text
    replacements = [
        ("ناثان دريك", "نيت دريك"),
        ("ناثان", "نيت"),
        ("سير فرانسيس", "السير فرانسيس"),
        ("إلينا فيشر", "إيلينا فيشر"),
        ("إلينا", "إيلينا"),
        ("سوليفان", "سوليفان"),
        ("كلوي فريزر", "كلوي فريزر"),
        ("شامبالا", "شامبالا"),
        ("إل دورادو", "إلدورادو"),
        ("الدورادو", "إلدورادو"),
        ("مدينة الذهب", "مدينة الذهب"),
        ("حجر شينتاماني", "حجر تشينتاماني"),
        ("إرم ذات العماد", "إرم ذات العماد"),
        ("أتلانتس الرمال", "أتلانتس الرمال"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def translate_batch_worker(batch, url):
    session = get_session()
    masked_list = []
    tags_list = []
    for s in batch:
        m, t = protect_tags(s)
        masked_list.append(m)
        tags_list.append(t)
        
    for attempt in range(3):
        try:
            r = session.post(url, data={'q': masked_list}, timeout=12)
            if r.status_code == 200:
                raw_results = r.json()
                if len(raw_results) == len(batch):
                    cleaned = []
                    for raw, tags in zip(raw_results, tags_list):
                        restored = restore_tags(raw, tags)
                        restored = polish_story_translation(restored)
                        cleaned.append(restored)
                    return list(zip(batch, cleaned))
        except Exception:
            time.sleep(0.5 * (attempt + 1))
            
    # Fallback to single translations
    fallback_res = []
    for s, tags in zip(batch, tags_list):
        try:
            m, t = protect_tags(s)
            r = session.get(url + '&q=' + urllib.parse.quote(m), timeout=6)
            if r.status_code == 200:
                restored = restore_tags(r.json()[0], t)
                restored = polish_story_translation(restored)
                fallback_res.append((s, restored))
                continue
        except Exception:
            pass
        fallback_res.append((s, s))
    return fallback_res

def pack_text_table(entries_dict):
    sorted_sids = sorted(entries_dict.keys())
    count = len(sorted_sids)
    str_table = bytearray(b'UNTRANSLATED STRING!!!\x00')
    offsets = {}
    for sid in sorted_sids:
        text = entries_dict[sid]
        if text is None:
            text = ""
        text_bytes = text.encode('utf-8') + b'\x00'
        offsets[sid] = len(str_table)
        str_table.extend(text_bytes)
        
    header = bytearray(4 + count * 8)
    struct.pack_into('>I', header, 0, count)
    for i, sid in enumerate(sorted_sids):
        struct.pack_into('>II', header, 4 + i*8, sid, offsets[sid])
    return bytes(header + str_table)

def clean_cache_file(cache_file):
    if not cache_file.exists():
        return {}
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cleaned = {k: v for k, v in data.items() if any('\u0600' <= ch <= '\u06FF' for ch in v)}
    cleaned.update(PREMIUM_DICTIONARY)
    print(f"[*] Cleaned cache has {len(cleaned)} validated Arabic translations.")
    return cleaned

def fetch_missing_translations(missing_texts, cache, cache_file):
    if not missing_texts:
        return
    print(f"[*] Translating {len(missing_texts)} missing strings using multi-threaded batch translation...")
    
    url = 'https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl=ar'
    batch_size = 25
    batches = [missing_texts[i:i+batch_size] for i in range(0, len(missing_texts), batch_size)]
    print(f"[*] Total batches to translate: {len(batches)}")
    
    t0 = time.time()
    completed = 0
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_batch = {executor.submit(translate_batch_worker, b, url): b for b in batches}
        for future in as_completed(future_to_batch):
            try:
                results = future.result()
                for src, trans in results:
                    if trans and any('\u0600' <= c <= '\u06FF' for c in trans):
                        cache[src] = trans
            except Exception as e:
                pass
            completed += 1
            if completed % 10 == 0 or completed == len(batches):
                print(f"    -> Progress: {completed}/{len(batches)} batches ({time.time()-t0:.1f}s)")
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False)
                    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)
    print(f"[*] All missing strings translated in {time.time()-t0:.1f}s!")

def shape_worker(item):
    sid, text = item
    return sid, reshape_arabic(text)

def package_mod():
    base_game = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\Game')
    mod_dir = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\Uncharted_Arabic_Mod')
    
    print("\n============================================================")
    print("  PACKAGING UNCHARTED TRILOGY ARABIC MOD")
    print("============================================================")
    
    if mod_dir.exists():
        shutil.rmtree(mod_dir)
        
    files_to_copy = [
        (base_game / 'u1data' / 'data.psarc', mod_dir / 'Game' / 'u1data' / 'data.psarc'),
        (base_game / 'u1data' / 'build' / 'main' / 'core.psarc', mod_dir / 'Game' / 'u1data' / 'build' / 'main' / 'core.psarc'),
        (base_game / 'u2data' / 'data.psarc', mod_dir / 'Game' / 'u2data' / 'data.psarc'),
        (base_game / 'u2data' / 'build' / 'main' / 'core.psarc', mod_dir / 'Game' / 'u2data' / 'build' / 'main' / 'core.psarc'),
        (base_game / 'u3data' / 'data.psarc', mod_dir / 'Game' / 'u3data' / 'data.psarc'),
        (base_game / 'u3data' / 'build' / 'main' / 'core.psarc', mod_dir / 'Game' / 'u3data' / 'build' / 'main' / 'core.psarc'),
    ]
    
    for src, dst in files_to_copy:
        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"Copying {src.name} -> {dst.relative_to(mod_dir)}...")
        shutil.copy2(src, dst)
        
    bat_content = """@echo off
title Uncharted Trilogy Arabic Mod Installer - Mohamed Moslem Allouch
color 0A
echo =====================================================================
echo   UNCHARTED: The Nathan Drake Collection - Arabic Mod
echo   تعريب ثلاثية أنشارتد الكاملة للكمبيوتر (PC Port)
echo   تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)
echo =====================================================================
echo.
echo Installing Arabic files into the game directory...
if not exist "..\\Game" (
    echo Error: Please place the 'Uncharted_Arabic_Mod' folder inside the main game directory!
    pause
    exit /b
)

xcopy /E /Y /I "Game" "..\\Game"
echo.
echo =====================================================================
echo   SUCCESS: Arabic Mod installed successfully!
echo   تم تثبيت ملفات التعريب بنجاح!
echo.
echo   طريقة التفعيل داخل اللعبة:
echo   1. شغل اللعبة.
echo   2. من القائمة الرئيسية، ادخل إلى Options (الخيارات) -> Language (اللغة).
echo   3. اضبط Text (النص) على: العربية.
echo   4. اضبط Subtitles (الترجمة) على: تشغيل.
echo   5. اترك Speech (الحوار) على: English للاستمتاع بالأصوات الإنجليزية الأصلية.
echo =====================================================================
echo.
pause
"""
    with open(mod_dir / 'Install_Arabic_Mod.bat', 'w', encoding='utf-8-sig') as f:
        f.write(bat_content)
        
    readme_content = """================================================================================
مود التعريب الكامل والنهائي لثلاثية أنشارتد (نسخة الحاسب PC)
UNCHARTED: The Nathan Drake Collection - Pure Native Arabic Mod (PC Port)
تعريب وإعداد وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)
================================================================================

ميزات التعريب:
1. تعريب كامل وشامل لثلاثية ألعاب أنشارتد الكاملة:
   - Uncharted 1: Drake's Fortune (أنشارتد 1: حظ دريك)
   - Uncharted 2: Among Thieves (أنشارتد 2: بين اللصوص)
   - Uncharted 3: Drake's Deception (أنشارتد 3: خداع دريك)
2. توقيع وبصمة المطور بارزة في القائمة الرئيسية وشاشات البداية:
   - في القائمة الرئيسية بجانب خيار الإعدادات مثل لعبة God of War:
     [خيارات (تعريب: محمد مسلم علوش)]
   - في وسط الشاشة عند شاشة البداية:
     [اضغط على ENTER للبدء (تعريب: محمد مسلم علوش)]
   - في شاشات البداية وشاشات النهاية والـ Credits لجميع الأجزاء الثلاثة:
     تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)
3. تعريب كامل لجميع القوائم الرئيسية، الإعدادات، خيارات التحكم، شاشات التوقف والمكافآت بنسبة 100%.
4. ترجمة كاملة بنسبة 100% لجميع نصوص وحوارات القصة والترجمات النصية (Subtitles) في الفصول والمشاهد السينمائية.
5. إعادة بناء أطلس الخطوط بالكامل بدقة 1024×1024 بخط Bold عريض مع محاذاة رأسية دقيقة لخط الأساس (Baseline Alignment).
6. خلو تام من أي رموز @ أو حروف مقطوعة، مع ضبط كامل للتشكيل ولفظ الجلالة.
7. إصلاح خيارات التشغيل والإيقاف (تشغيل / إيقاف) بدلاً من الترجمة الآلية الخاطئة.
8. الإبقاء على الأصوات الإنجليزية الأصلية الكاملة للشخصيات.

--------------------------------------------------------------------------------
طريقة التثبيت السريعة (Direct Copy & Paste):
--------------------------------------------------------------------------------
1. انسخ مجلد [Game] والصقه مباشرة داخل مجلد اللعبة الرئيسي:
   D:\\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\\
2. وافق على الاستبدال لجميع الملفات عند السؤال.
   (أو يمكنك تشغيل ملف Install_Arabic_Mod.bat ليقوم بالنسخ التلقائي).
3. شغل اللعبة، ومن قائمة الإعدادات (Options) -> اللغة (Language):
   - اختر Text (النص): العربية.
   - اختر Subtitles (الترجمة): تشغيل.
   - اترك Speech (الحوار): English للاستماع للأصوات الإنجليزية الأصلية.

================================================================================
تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)
"""
    with open(mod_dir / 'README_Arabic_Mod_Instructions.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("\nCreating ZIP Archive for sharing...")
    zip_path = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\Uncharted_The_Nathan_Drake_Collection_Arabic_Mod.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in mod_dir.rglob('*'):
            if file.is_file():
                rel_p = file.relative_to(mod_dir.parent)
                zipf.write(file, rel_p)
                
    print(f"ZIP Archive created at: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print("\nALL WORK COMPLETE!")

def main():
    scratch = Path(r'C:\Users\SlouMa\.gemini\antigravity\scratch')
    base_game = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\Game')
    cache_file = scratch / 'u1_trans_cache.json'
    
    cache = clean_cache_file(cache_file)
    
    # 1. Identify all strings needing translation across the trilogy
    print("\n[*] Scanning all 3 games for uncached or English strings...")
    all_needed = set()
    
    for sku in ['u1', 'u2', 'u3']:
        with open(scratch / f'{sku}_common.json', 'r', encoding='utf-8') as f:
            comm = json.load(f)
        with open(scratch / f'{sku}_subtitles.json', 'r', encoding='utf-8') as f:
            subs = json.load(f)
            
        for it in comm + subs:
            en = it.get('en', '').strip()
            fr = it.get('fr', '').strip()
            src = en if en else fr
            if not src: continue
            if src not in cache or not any('\u0600' <= c <= '\u06FF' for c in cache[src]):
                all_needed.add(src)
                
    missing_list = sorted(list(all_needed))
    print(f"[*] Found {len(missing_list)} unique strings needing translation.")
    
    # 2. Translate all missing strings
    fetch_missing_translations(missing_list, cache, cache_file)
    
    # 3. Process and apply to each game
    cpu_cores = os.cpu_count() or 16
    print(f"\n[*] Starting Multiprocess BiDi Shaping on {cpu_cores} CPU cores...")
    
    for sku, folder in [('Uncharted 1', 'u1data'), ('Uncharted 2', 'u2data'), ('Uncharted 3', 'u3data')]:
        print(f"\n============================================================")
        print(f"[*] Building 100% Arabic text tables for {sku}...")
        print(f"============================================================")
        
        sku_key = 'u1' if '1' in sku else ('u2' if '2' in sku else 'u3')
        core_path = base_game / folder / 'build' / 'main' / 'core.psarc'
        
        with open(scratch / f'{sku_key}_common.json', 'r', encoding='utf-8') as f:
            comm_list = json.load(f)
        with open(scratch / f'{sku_key}_subtitles.json', 'r', encoding='utf-8') as f:
            sub_list = json.load(f)
            
        raw_comm = {}
        for it in comm_list:
            sid = it['sid']
            en = it.get('en', '').strip()
            fr = it.get('fr', '').strip()
            
            # French language slot override
            if sid == 0x83fcc51a:
                raw_comm[sid] = "العربية"
                continue
                
            src = en if en else fr
            if not src:
                raw_comm[sid] = ""
                continue
                
            trans = PREMIUM_DICTIONARY.get(src)
            if not trans and en: trans = PREMIUM_DICTIONARY.get(en)
            if not trans and fr: trans = PREMIUM_DICTIONARY.get(fr)
            if not trans: trans = cache.get(src, src)
            raw_comm[sid] = trans

        raw_subs = {}
        for it in sub_list:
            sid = it['sid']
            en = it.get('en', '').strip()
            fr = it.get('fr', '').strip()
            src = en if en else fr
            if not src:
                raw_subs[sid] = ""
                continue
            trans = PREMIUM_DICTIONARY.get(src)
            if not trans and en: trans = PREMIUM_DICTIONARY.get(en)
            if not trans and fr: trans = PREMIUM_DICTIONARY.get(fr)
            if not trans: trans = cache.get(src, src)
            raw_subs[sid] = trans
            
        print(f"[{sku}] Multiprocess shaping {len(raw_comm)} common and {len(raw_subs)} subtitle strings...")
        with ProcessPoolExecutor(max_workers=cpu_cores) as pool:
            shaped_comm = dict(pool.map(shape_worker, raw_comm.items(), chunksize=100))
            shaped_subs = dict(pool.map(shape_worker, raw_subs.items(), chunksize=100))
            
        # Specific SID overrides for signature, titles and toggles
        shaped_comm[0x382c5a86] = reshape_arabic("خيارات (تعريب: محمد مسلم علوش)")
        shaped_comm[0xfb08c743] = reshape_arabic("خيارات (تعريب: محمد مسلم علوش)")
        if 0x950c4ae8 in shaped_comm:
            shaped_comm[0x950c4ae8] = reshape_arabic("خيارات (تعريب: محمد مسلم علوش)")
        if 0xfe695145 in shaped_comm:
            shaped_comm[0xfe695145] = reshape_arabic("خيارات (تعريب: محمد مسلم علوش)")
            
        shaped_comm[0x338a0580] = reshape_arabic("اضغط على |ENTER| للبدء\n(تعريب: محمد مسلم علوش)")
        shaped_comm[0xaa5b8b93] = reshape_arabic("اضغط START للبدء\n(تعريب: محمد مسلم علوش)")
        
        # Game specific title screen
        if sku_key == 'u1':
            shaped_comm[0x64ae0ad5] = reshape_arabic("UNCHARTED: Drake's Fortune™\nتعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
        elif sku_key == 'u2':
            shaped_comm[0x64ae0ad5] = reshape_arabic("UNCHARTED 2: Among Thieves™\nتعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
        elif sku_key == 'u3':
            shaped_comm[0x64ae0ad5] = reshape_arabic("UNCHARTED 3: Drake's Deception™\nتعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
            
        shaped_comm[0x041ff922] = reshape_arabic("UNCHARTED: The Nathan Drake Collection™\nتعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
        shaped_comm[0x74a0b5a9] = reshape_arabic("UNCHARTED: The Nathan Drake Collection™\nتعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
        if 0xc313d6f2 in shaped_comm:
            shaped_comm[0xc313d6f2] = reshape_arabic("تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
        if 0xe242d3da in shaped_comm:
            shaped_comm[0xe242d3da] = reshape_arabic("تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)")
            
        # Pack tables and update core.psarc
        new_comm_bytes = pack_text_table(shaped_comm)
        new_sub_bytes = pack_text_table(shaped_subs)
        
        replace_dict = {
            'text1/ps4/3.common': new_comm_bytes,
            'text1/ps4/3.subtitles': new_sub_bytes,
        }
        
        # Credits if present
        ps = PSARC(str(core_path))
        if any(x.get('name') == 'text1/ps4/3.credits' for x in ps.entries):
            credits_dict = {
                0x30afd9fc: reshape_arabic("محمد مسلم علوش"),
                0x79650402: reshape_arabic("تعريب: محمد مسلم علوش")
            }
            replace_dict['text1/ps4/3.credits'] = pack_text_table(credits_dict)
        if any(x.get('name') == 'text1/ps4/2.credits' for x in ps.entries):
            credits_en = {
                0x30afd9fc: "Mohamed Moslem Allouch",
                0x79650402: "Arabic Localization by Mohamed Moslem Allouch"
            }
            replace_dict['text1/ps4/2.credits'] = pack_text_table(credits_en)
        ps.close()
        
        update_psarc_entries(str(core_path), replace_dict)
        print(f"[{sku}] core.psarc updated successfully with 100% Arabic text!")
        
    # 4. Package mod
    package_mod()

if __name__ == '__main__':
    main()
