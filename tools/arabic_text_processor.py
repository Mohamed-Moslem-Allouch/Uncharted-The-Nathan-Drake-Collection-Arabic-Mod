import re
import arabic_reshaper
from bidi.algorithm import get_display

# Strip Tashkeel / Harakat / Tanween to prevent missing font glyphs and disconnected letters
HARAKAT_REGEX = re.compile(r'[\u064B-\u065F\u0670]')

# Audio cues in subtitles that should be removed or cleaned up to prevent punctuation artifacts
AUDIO_CUE_REGEX = re.compile(r'(\s*[\(\[](?:laughs?|groans?|gasps?|sighs?|chuckles?|grunts?|coughs?|screams?|yells?|shouts?|whispers?|snickers?|panting?)[\)\]]\s*|\s*\(يضحك\)\s*|\s*\(ضحكة\)\s*|\s*\(يسعل\)\s*|\s*\(تنهد\)\s*)', re.IGNORECASE)

# Naughty Dog game engine tags and format specifiers
TAG_REGEX = re.compile(r'(\|[^|]+\||%[0-9]*[a-zA-Z]|\[\[TAG\d+\]\])')

# Custom config for arabic_reshaper: Strictly delete harakat and enable all ligatures
RESHAPER_CONFIG = {
    'delete_harakat': True,
    'support_ligatures': True,
    'RIAL SIGN': True,
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=RESHAPER_CONFIG)

def clean_arabic_text(text):
    if not text:
        return ""
    # Punctuation / symbol normalization
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('«', '"').replace('»', '"')
    text = text.replace('…', '...')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('™', '').replace('®', '')
    
    # Remove audio cues like (laughs), [chuckles]
    text = AUDIO_CUE_REGEX.sub(' ', text)
    # Remove all Tashkeel / Harakat / Tanween
    text = HARAKAT_REGEX.sub('', text)
    # Fix Arabic comma and question mark spacing
    text = text.replace(' ،', '،').replace(' ؟', '؟')
    return text.strip()

def reshape_single_line(line):
    if not line or not any('\u0600' <= c <= '\u06FF' for c in line):
        return line

    # 1. Protect tags with unique numeric placeholders
    placeholders = []
    def repl_tag(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__T{idx}T__"

    safe_line = TAG_REGEX.sub(repl_tag, line)
    safe_line = clean_arabic_text(safe_line)
    
    # 2. Reshape letters (connect initial, medial, final, isolated forms)
    reshaped = reshaper.reshape(safe_line)
    # Replace Allah ligature with standard Presentation Form letters (Alef, Lam, Lam, Heh)
    reshaped = reshaped.replace('\uFDF2', '\uFE8D\uFEDF\uFEE0\uFEEA')
    
    # 3. Apply BiDi algorithm to reverse visual order for LTR engine
    bidi_line = get_display(reshaped)
    
    # 4. Restore original tags strictly intact
    for idx, orig_tag in enumerate(placeholders):
        token = f"__T{idx}T__"
        token_rev = token[::-1]
        bidi_line = bidi_line.replace(token, orig_tag)
        bidi_line = bidi_line.replace(token_rev, orig_tag)
        
    return bidi_line

def reshape_arabic(text):
    if not text:
        return ""
    text = clean_arabic_text(text)
    if not any('\u0600' <= c <= '\u06FF' for c in text):
        return text

    # Process each line independently so top-to-bottom line order is preserved
    lines = text.split('\n')
    shaped_lines = [reshape_single_line(l) for l in lines]
    return '\n'.join(shaped_lines)

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    t1 = "وجه |LA| في الاتجاه الذي تريد التأرجح فيه\nواضغط |X| للقفز"
    print("Test 1:")
    print(reshape_arabic(t1))
    
    t2 = "You make it sound so dirty. (laughs)"
    t2_ar = "أنت تجعل الأمر يبدو قذراً جداً (laughs)"
    print("\nTest 2:")
    print(reshape_arabic(t2_ar))
