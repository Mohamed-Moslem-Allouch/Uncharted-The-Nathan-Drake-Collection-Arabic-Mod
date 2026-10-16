import struct
import zlib
import os
import sys
from pathlib import Path

def read_uint40_be(b):
    return (b[0] << 32) | (b[1] << 24) | (b[2] << 16) | (b[3] << 8) | b[4]

class PSARC:
    def __init__(self, filepath):
        self.filepath = filepath
        self.f = open(filepath, 'rb')
        self.header = self.f.read(32)
        (self.magic, self.ver_maj, self.ver_min, self.comp_type,
         self.toc_len, self.toc_entry_size, self.num_entries,
         self.block_size, self.flags) = struct.unpack('>4sHH4sIIIII', self.header)
        
        if self.magic != b'PSAR':
            raise ValueError(f"Invalid magic: {self.magic}")
            
        toc_data = self.f.read(self.toc_len - 32)
        self.entries = []
        for i in range(self.num_entries):
            raw = toc_data[i * self.toc_entry_size : (i + 1) * self.toc_entry_size]
            md5 = raw[:16]
            block_idx = struct.unpack('>I', raw[16:20])[0]
            uncomp_size = read_uint40_be(raw[20:25])
            offset = read_uint40_be(raw[25:30])
            self.entries.append({
                'id': i,
                'md5': md5,
                'block_idx': block_idx,
                'size': uncomp_size,
                'offset': offset,
                'name': None
            })
            
        block_table_start = self.num_entries * self.toc_entry_size
        num_blocks = (len(toc_data) - block_table_start) // 2
        self.block_sizes = struct.unpack(f'>{num_blocks}H', toc_data[block_table_start : block_table_start + num_blocks * 2])
        
        # Read entry 0 which is the manifest
        manifest_data = self.read_entry(0)
        names = manifest_data.decode('utf-8', errors='ignore').splitlines()
        for idx, name in enumerate(names):
            if idx + 1 < len(self.entries):
                self.entries[idx + 1]['name'] = name
        self.entries[0]['name'] = '__MANIFEST__'

    def read_entry(self, entry_idx):
        entry = self.entries[entry_idx]
        size = entry['size']
        if size == 0:
            return b''
        
        self.f.seek(entry['offset'])
        cur_block = entry['block_idx']
        out = bytearray()
        
        while len(out) < size:
            if cur_block >= len(self.block_sizes):
                # Uncompressed direct read
                chunk = self.f.read(size - len(out))
                out.extend(chunk)
                break
            b_size = self.block_sizes[cur_block]
            cur_block += 1
            if b_size == 0:
                # 0 means uncompressed chunk of size block_size or remainder
                chunk_len = min(self.block_size, size - len(out))
                chunk = self.f.read(chunk_len)
                out.extend(chunk)
            else:
                chunk = self.f.read(b_size)
                # Check if it's zlib compressed (usually 0x78)
                if chunk.startswith(b'\x78'):
                    decomp = zlib.decompress(chunk)
                    out.extend(decomp)
                else:
                    out.extend(chunk)
        return bytes(out)

    def list_files(self):
        return [e['name'] for e in self.entries if e['name']]

    def close(self):
        self.f.close()

def write_uint40_be(val):
    return bytes([(val >> 32) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff, (val >> 8) & 0xff, val & 0xff])

def pack_psarc(output_path, files_list, block_size=65536):
    """
    files_list: list of tuples (rel_path_str, data_bytes)
    """
    import hashlib
    manifest_str = '\n'.join([f[0] for f in files_list]) + '\n'
    manifest_bytes = manifest_str.encode('utf-8')
    
    all_files = [('__MANIFEST__', manifest_bytes)] + files_list
    num_entries = len(all_files)
    
    compressed_chunks = []
    block_sizes = []
    file_info = []
    
    cur_block_idx = 0
    for idx, (name, data) in enumerate(all_files):
        uncomp_size = len(data)
        file_block_start = cur_block_idx
        
        if uncomp_size == 0:
            file_info.append((name, file_block_start, 0, 0))
            continue
            
        file_data_bytes = bytearray()
        for i in range(0, uncomp_size, block_size):
            chunk = data[i : i + block_size]
            comp = zlib.compress(chunk, 9)
            if len(comp) < len(chunk):
                block_sizes.append(len(comp))
                file_data_bytes.extend(comp)
            else:
                block_sizes.append(0)
                file_data_bytes.extend(chunk)
            cur_block_idx += 1
            
        compressed_chunks.append(bytes(file_data_bytes))
        file_info.append((name, file_block_start, uncomp_size, len(file_data_bytes)))
        
    toc_entry_size = 30
    toc_length = 32 + num_entries * toc_entry_size + len(block_sizes) * 2
    
    current_data_offset = toc_length
    entries_bytes = bytearray()
    
    for idx, (name, file_block_start, uncomp_size, comp_len) in enumerate(file_info):
        if idx == 0:
            md5 = b'\x00' * 16
        else:
            md5 = hashlib.md5(name.encode('utf-8')).digest()
            
        entry_raw = bytearray(30)
        entry_raw[0:16] = md5
        struct.pack_into('>I', entry_raw, 16, file_block_start)
        entry_raw[20:25] = write_uint40_be(uncomp_size)
        entry_raw[25:30] = write_uint40_be(current_data_offset)
        entries_bytes.extend(entry_raw)
        
        current_data_offset += comp_len
        
    block_table = bytearray()
    for bs in block_sizes:
        block_table.extend(struct.pack('>H', bs))
        
    header = struct.pack('>4sHH4sIIIII', b'PSAR', 1, 4, b'zlib', toc_length, toc_entry_size, num_entries, block_size, 0)
    
    temp_path = str(output_path) + '.tmp'
    with open(temp_path, 'wb') as f:
        f.write(header)
        f.write(entries_bytes)
        f.write(block_table)
        for chunk in compressed_chunks:
            f.write(chunk)
            
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(temp_path, output_path)

def update_psarc_entries(psarc_path, replace_dict):
    """
    replace_dict: dict mapping entry_name -> new_data_bytes
    """
    ps = PSARC(psarc_path)
    files = []
    for e in ps.entries[1:]:
        name = e['name']
        if name in replace_dict:
            files.append((name, replace_dict[name]))
        else:
            files.append((name, ps.read_entry(e['id'])))
    ps.close()
    pack_psarc(psarc_path, files)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', help='Path to PSARC')
    parser.add_argument('--list', action='store_true', help='List all entries')
    parser.add_argument('--extract', help='Directory to extract to')
    parser.add_argument('--dump-entry', type=int, help='Dump specific entry index to stdout/file')
    args = parser.parse_args()

    ps = PSARC(args.archive)
    if args.list:
        print(f"PSARC {args.archive}: {len(ps.entries)} entries")
        for e in ps.entries:
            print(f"  [{e['id']}] {e['name']} ({e['size']} bytes)")
    elif args.extract:
        out_dir = Path(args.extract)
        for e in ps.entries:
            if not e['name'] or e['name'] == '__MANIFEST__':
                continue
            data = ps.read_entry(e['id'])
            target_p = out_dir / e['name']
            target_p.parent.mkdir(parents=True, exist_ok=True)
            with open(target_p, 'wb') as out_f:
                out_f.write(data)
        print(f"Extracted {len(ps.entries)} files to {args.extract}")
    else:
        print(f"PSARC {args.archive}: {len(ps.entries)} entries")
        for e in ps.entries[:30]:
            print(f"  [{e['id']}] {e['name']} ({e['size']} bytes)")
    ps.close()
