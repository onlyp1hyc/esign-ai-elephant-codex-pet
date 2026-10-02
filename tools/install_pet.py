#!/usr/bin/env python3
"""安装最小 Codex V2 包；默认拒绝覆盖已存在目标，无网络访问。"""
from pathlib import Path
import argparse
import json
import os
import shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pets-dir',type=Path,default=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'pets')
    args=parser.parse_args()
    pet=json.loads((ROOT/'pet.json').read_text())
    assert pet['id']=='esign-ai-elephant' and pet['spriteVersionNumber']==2
    with Image.open(ROOT/'spritesheet.webp') as image:
        assert image.size==(1536,2288) and image.mode=='RGBA'
    target=args.pets_dir.resolve()/pet['id']
    if target.exists():
        parser.error(f'目标已存在，未覆盖：{target}。请先手动备份并重命名旧目录。')
    target.mkdir(parents=True)
    for name in ('pet.json','spritesheet.webp'):
        shutil.copy2(ROOT/name,target/name)
    print(f'已安装到 {target}\n请在桌面应用 设置 > 宠物 中刷新并选择 eSign AI 小象。')
if __name__=='__main__':
    main()
