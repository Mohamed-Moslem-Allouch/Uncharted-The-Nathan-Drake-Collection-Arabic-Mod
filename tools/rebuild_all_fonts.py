import io
import struct
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from psarc_tool import PSARC, update_psarc_entries

def build_perfect_arabic_font(orig_fnt_bytes, orig_tga_bytes, ttf_path=r'C:\Windows\Fonts\segoeuib.ttf', font_size=36):
    # 1. Load original TGA
    orig_img = Image.open(io.BytesIO(orig_tga_bytes)).convert('RGBA')
    orig_w, orig_h = orig_img.size
    
    # 2. Target 1024x1024 texture atlas
    target_w, target_h = 1024, 1024
    new_img = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    new_img.paste(orig_img, (0, 0))
    
    # 3. Collect all needed Arabic codepoints
    codepoints = []
    # Presentation Forms B (all isolated, initial, medial, final Arabic letters)
    codepoints.extend(range(0xFE70, 0xFEFD))
    # Lam-Alef ligatures
    codepoints.extend([0xFEF5, 0xFEF6, 0xFEF7, 0xFEF8, 0xFEF9, 0xFEFA, 0xFEFB, 0xFEFC])
    # Arabic punctuation & symbols
    codepoints.extend([0x060C, 0x061B, 0x061F, 0x066A, 0x06D4, 0x00AB, 0x00BB, 0x2026])
    # Arabic-Indic and Eastern digits
    codepoints.extend(range(0x0660, 0x066A))
    codepoints.extend(range(0x06F0, 0x06FA))
    # Standard Arabic characters
    codepoints.extend(range(0x0621, 0x064B))
    # Presentation Forms A (ligatures)
    codepoints.extend(range(0xFB50, 0xFB9E))
    codepoints = sorted(list(set(codepoints)))
    
    # 4. Filter against existing IDs in original font
    fnt_text = orig_fnt_bytes.decode('utf-8', errors='ignore')
    fnt_lines = fnt_text.splitlines()
    
    existing_ids = set()
    for line in fnt_lines:
        if line.startswith('char id='):
            cid = int(line.split()[1].split('=')[1])
            existing_ids.add(cid)
            
    needed_codepoints = [cp for cp in codepoints if cp not in existing_ids]
    
    font = ImageFont.truetype(ttf_path, font_size)
    ascent, descent = font.getmetrics()
    draw = ImageDraw.Draw(new_img)
    
    cur_x = 4
    # Start packing below the original texture content
    cur_y = orig_h + 4 if orig_h < 1024 else 260
    row_height = 44
    new_chars = []
    
    # Naughty Dog font baseline
    base = 34
    
    for cp in needed_codepoints:
        ch = chr(cp)
        bbox = font.getbbox(ch)
        if not bbox:
            continue
        left, top, right, bottom = bbox
        gw = right - left
        gh = bottom - top
        if gw <= 0 or gh <= 0:
            continue
            
        adv = int(font.getlength(ch))
        if cur_x + gw + 4 >= target_w:
            cur_x = 4
            cur_y += row_height + 4
            if cur_y + row_height >= target_h:
                print(f"Warning: Font atlas full at codepoint U+{cp:04X}")
                break
                
        # Draw glyph in pure white across all channels (RGBA 255,255,255,255)
        draw_x = cur_x - left
        draw_y = cur_y - top
        draw.text((draw_x, draw_y), ch, font=font, fill=(255, 255, 255, 255))
        
        # Exact mathematical baseline alignment:
        # Distance from baseline to top of glyph is (ascent - top).
        # In BMFont, yoffset is distance from top of line (0) to glyph top:
        yoffset = base - (ascent - top)
        xoffset = left
        
        char_entry = (
            f"char id={cp:<6} "
            f"x={cur_x:<6} "
            f"y={cur_y:<6} "
            f"width={gw:<6} "
            f"height={gh:<6} "
            f"xoffset={xoffset:<6} "
            f"yoffset={yoffset:<6} "
            f"xadvance={adv:<6} "
            f"page=0  chnl=4"
        )
        new_chars.append(char_entry)
        cur_x += gw + 6
        
    print(f"Generated {len(new_chars)} Arabic glyphs with baseline alignment (yoffset ~ {yoffset})")
    
    # 5. Export new TGA
    tga_buf = io.BytesIO()
    new_img.save(tga_buf, format='TGA')
    new_tga_bytes = tga_buf.getvalue()
    
    # 6. Rebuild FNT lines
    out_lines = []
    for line in fnt_lines:
        if line.startswith('common '):
            parts = line.split()
            new_parts = []
            for p in parts:
                if p.startswith('scaleW='):
                    new_parts.append(f'scaleW={target_w}')
                elif p.startswith('scaleH='):
                    new_parts.append(f'scaleH={target_h}')
                else:
                    new_parts.append(p)
            out_lines.append(' '.join(new_parts))
        elif line.startswith('chars count='):
            count = int(line.split('=')[1])
            new_count = count + len(new_chars)
            out_lines.append(f"chars count={new_count}")
        elif line.startswith('char '):
            out_lines.append(line)
        elif line.startswith('kernings'):
            for nc in new_chars:
                out_lines.append(nc)
            new_chars = []
            out_lines.append(line)
        else:
            out_lines.append(line)
            
    if new_chars:
        for nc in new_chars:
            out_lines.append(nc)
            
    new_fnt_bytes = ('\n'.join(out_lines) + '\n').encode('utf-8')
    return new_fnt_bytes, new_tga_bytes

def main():
    base_game = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\Game')
    backup_base = Path(r'D:\Uncharted.The.Nathan.Drake.Collection.PC-InsaneRamZes\backup_fr_original')
    
    print("============================================================")
    print("  REBUILDING PERFECT ARABIC FONTS FOR ENTIRE TRILOGY")
    print("============================================================")
    
    # 1. Uncharted 1
    print("\n[Uncharted 1] Rebuilding font from backup...")
    ps_bk1 = PSARC(str(backup_base / 'u1' / 'data.psarc'))
    e_fnt1 = next(e for e in ps_bk1.entries if e['name'] == 'art/general/textures/font/ps4/game3.fnt')
    e_tga1 = next(e for e in ps_bk1.entries if e['name'] == 'art/general/textures/font/ps4/game3_00.tga')
    fnt1_bytes = ps_bk1.read_entry(e_fnt1['id'])
    tga1_bytes = ps_bk1.read_entry(e_tga1['id'])
    ps_bk1.close()
    
    new_fnt1, new_tga1 = build_perfect_arabic_font(fnt1_bytes, tga1_bytes)
    update_psarc_entries(
        str(base_game / 'u1data' / 'data.psarc'),
        {
            'art/general/textures/font/ps4/game3.fnt': new_fnt1,
            'art/general/textures/font/ps4/game3_00.tga': new_tga1
        }
    )
    print("[Uncharted 1] Font atlas successfully updated!")
    
    # 2. Uncharted 2
    print("\n[Uncharted 2] Rebuilding font from backup...")
    ps_bk2 = PSARC(str(backup_base / 'u2' / 'data.psarc'))
    e_fnt2 = next(e for e in ps_bk2.entries if e['name'] == 'data/fonts/ps4/main.fnt')
    e_tga2 = next(e for e in ps_bk2.entries if e['name'] == 'data/fonts/ps4/main_00.tga')
    fnt2_bytes = ps_bk2.read_entry(e_fnt2['id'])
    tga2_bytes = ps_bk2.read_entry(e_tga2['id'])
    ps_bk2.close()
    
    new_fnt2, new_tga2 = build_perfect_arabic_font(fnt2_bytes, tga2_bytes)
    # game3.fnt in UC2 must also point to main_00.tga
    fnt2_str = new_fnt2.decode('utf-8')
    game3_fnt2 = fnt2_str.replace('page id=0 file="main_00.tga"', 'page id=0 file="main_00.tga"').encode('utf-8')
    update_psarc_entries(
        str(base_game / 'u2data' / 'data.psarc'),
        {
            'data/fonts/ps4/main.fnt': new_fnt2,
            'data/fonts/ps4/main_00.tga': new_tga2,
            'data/fonts/ps4/game3.fnt': game3_fnt2
        }
    )
    print("[Uncharted 2] Font atlases successfully updated (main.fnt + game3.fnt)!")
    
    # 3. Uncharted 3
    print("\n[Uncharted 3] Rebuilding font from backup...")
    ps_bk3 = PSARC(str(backup_base / 'u3' / 'data.psarc'))
    e_fnt3 = next(e for e in ps_bk3.entries if e['name'] == 'data/fonts/ps4/main.fnt')
    e_tga3 = next(e for e in ps_bk3.entries if e['name'] == 'data/fonts/ps4/main_00.tga')
    fnt3_bytes = ps_bk3.read_entry(e_fnt3['id'])
    tga3_bytes = ps_bk3.read_entry(e_tga3['id'])
    ps_bk3.close()
    
    new_fnt3, new_tga3 = build_perfect_arabic_font(fnt3_bytes, tga3_bytes)
    # Both game3.fnt and classic.fnt must point to main_00.tga and have all Arabic glyphs!
    fnt3_str = new_fnt3.decode('utf-8')
    game3_fnt3 = fnt3_str.replace('page id=0 file="main_00.tga"', 'page id=0 file="main_00.tga"').encode('utf-8')
    classic_fnt3 = fnt3_str.replace('page id=0 file="main_00.tga"', 'page id=0 file="main_00.tga"').encode('utf-8')
    
    update_psarc_entries(
        str(base_game / 'u3data' / 'data.psarc'),
        {
            'data/fonts/ps4/main.fnt': new_fnt3,
            'data/fonts/ps4/main_00.tga': new_tga3,
            'data/fonts/ps4/game3.fnt': game3_fnt3,
            'data/fonts/ps4/classic.fnt': classic_fnt3
        }
    )
    print("[Uncharted 3] Font atlases successfully updated (main.fnt + game3.fnt + classic.fnt)!")
    print("\nALL TRILOGY FONTS PERFECTLY REBUILT AND INSTALLED!")

if __name__ == '__main__':
    main()
