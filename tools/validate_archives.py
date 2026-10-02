#!/usr/bin/env python3
"""校验ZIP内容及校验和，确认不携带旧草稿、原始截图或机器日志。"""
from pathlib import Path
import hashlib
import json
import zipfile
ROOT=Path(__file__).resolve().parents[1]
checksums=json.loads((ROOT/'dist/sha256.json').read_text())
for filename,expected in checksums.items():
    p=ROOT/'dist'/filename
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected, filename
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        for entry in z.infolist():
            parts=Path(entry.filename).parts
            assert not any(x in {'.archive','.git','qa','__pycache__','config','secrets','credentials'} for x in parts)
            assert not any(x.startswith('.env') for x in parts)
            assert 'original-design-v1.png' not in parts
            relative=Path(*parts[1:])
            assert (ROOT/relative).is_file(),relative
            assert z.read(entry.filename)==(ROOT/relative).read_bytes(),relative
        if filename.endswith('codex-v2.zip'):
            assert set(z.namelist())=={'esign-ai-elephant/pet.json','esign-ai-elephant/spritesheet.webp'}
        else:
            assert 'esign-elephant-pet/demo/index.html' in z.namelist()
            for notice in ('README.md','LICENSE','BRAND_ASSETS.md'):
                assert 'esign-elephant-pet/'+notice in z.namelist()
            assert len([n for n in z.namelist() if '/frames/' in n and n.endswith('.png')])==58
            assert len([n for n in z.namelist() if '/exports/' in n and n.endswith('.png')])==174
        print(f'PASS {filename}: {len(z.infolist())} files, {p.stat().st_size:,} bytes, SHA-256 matches')
