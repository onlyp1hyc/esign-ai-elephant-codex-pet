#!/usr/bin/env python3
"""验证交付完整性；失败即非零退出，不把缺失资源降级为警告。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
import numpy as np
from PIL import Image, ImageDraw
from build_package import ROOT, NATIVE, native_cell, zero_hidden, write_json, font

def main():
    failures=[]; checks=[]; seen=[]
    def check(condition,message):
        checks.append(message)
        if not condition: failures.append(message)
    def inspect(path,size):
        image=Image.open(path).convert('RGBA'); a=np.array(image)
        check(image.size==size,f'{path.relative_to(ROOT)} 尺寸')
        check(np.count_nonzero(a[:,:,3])>100,f'{path.relative_to(ROOT)} 非空')
        check(np.any(a[:,:,3]==0),f'{path.relative_to(ROOT)} 透明背景')
        check(not np.any(a[a[:,:,3]==0]),f'{path.relative_to(ROOT)} 透明RGB为0')
        check(not np.any(a[[0,-1],:,3]) and not np.any(a[:,[0,-1],3]),f'{path.relative_to(ROOT)} 画布无裁断')
        seen.append(path)
        return image
    pet=json.loads((ROOT/'pet.json').read_text())
    check(set(pet)=={'id','displayName','description','spriteVersionNumber','spritesheetPath'},'manifest 精确五字段')
    check(pet['spriteVersionNumber']==2 and pet['spritesheetPath']=='spritesheet.webp','V2声明及相对图集路径')
    cfg=json.loads((ROOT/'source/artwork.json').read_text())['sheets']
    business=json.loads((ROOT/'business-states.json').read_text())
    check(len(business['states'])==9 and len(business['events'])==9,'九业务状态与事件完整')
    check(set(business['events'].values())==set(business['states']),'全部事件映射到有效状态')
    frames={};counts={};unique={}
    for name,spec in cfg.items():
        folder=ROOT/('frames' if 'label' in spec else 'native-frames')/name
        paths=sorted(folder.glob('*.png'))
        check(len(paths)==len(spec['select']),f'{name} 帧数且无陈旧余帧')
        frames[name]=[inspect(p,(512,512)) for p in paths]
        counts[name]=len(paths)
        unique[name]=len({hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
        if name not in business['states']: continue
        state=business['states'][name]
        check(len(state['durationMs'])==len(paths) and all(n>0 for n in state['durationMs']),f'{name} 时长')
        check([p.relative_to(ROOT).as_posix() for p in paths]==state['frames'],f'{name} 路径')
        for size in (64,96,128):
            exports=sorted((ROOT/f'exports/{size}/{name}').glob('*.png'))
            check(len(exports)==len(paths),f'{name} {size}px 导出数量')
            for p,frame in zip(exports,frames[name]):
                small=inspect(p,(size,size))
                expected=zero_hidden(frame.resize((size,size),Image.Resampling.LANCZOS))
                check(np.array_equal(np.array(small),np.array(expected)),f'{p.relative_to(ROOT)} 等比导出像素')
        with Image.open(ROOT/f'previews/{name}.webp') as anim:
            check(anim.is_animated and anim.n_frames==len(paths),f'{name} 动态WebP完整')
            check(anim.size==(256,256),'动态WebP尺寸')
    inspect(ROOT/'source/character_master.png',(512,512))
    for name in business['states']:
        inspect(ROOT/f'source/state_{name}.png',(512,512))
    atlas=inspect(ROOT/'spritesheet.webp',(1536,2288))
    used=set()
    for row,(name,source,indices,durations) in enumerate(NATIVE):
        for col,idx in enumerate(indices):
            cell=atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
            check(np.array_equal(np.array(cell),np.array(native_cell(frames[source][idx]))),f'原生 {name}/{col} 与源帧相同')
            used.add((row,col))
    expected=native_cell(frames['idle'][0])
    check(np.array_equal(np.array(atlas.crop((1152,0,1344,208))),np.array(expected)),'中性静帧row0 col6')
    used.add((0,6))
    for i,frame in enumerate(frames['look']):
        row,col=9+i//8,i%8;used.add((row,col))
        check(np.array_equal(np.array(atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))),np.array(native_cell(frame))),f'视线 {i*22.5} 度像素')
    for row in range(11):
        for col in range(8):
            if (row,col) not in used:
                check(not np.any(np.array(atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208)))),f'未使用 {row}/{col} 全透明')
    check(len(used)==74,'V2有效单元74')
    for size in (64,96,128):
        sheet=inspect(ROOT/f'exports/{size}/spritesheet.webp',(8*size,9*size))
        for row,(name,state) in enumerate(business['states'].items()):
            for col in range(8):
                cell=sheet.crop((col*size,row*size,(col+1)*size,(row+1)*size))
                expected=Image.open(ROOT/f'exports/{size}/{name}/{col:03}.png') if col<len(state['frames']) else Image.new('RGBA',(size,size))
                check(np.array_equal(np.array(cell),np.array(expected)),f'业务图集{size} {name}/{col}')
    check((ROOT/'spritesheet_semantic.webp').read_bytes()==(ROOT/'exports/96/spritesheet.webp').read_bytes(),'默认图集采用96px导出')

    # 安装正向与重复安装测试只针对临时目录，不触及真实 pets。
    with tempfile.TemporaryDirectory(prefix='esign-pet-install-test-') as temp:
        cmd=[sys.executable,str(ROOT/'tools/install_pet.py'),'--pets-dir',temp]
        first=subprocess.run(cmd,capture_output=True,text=True)
        second=subprocess.run(cmd,capture_output=True,text=True)
        check(first.returncode==0,'临时目录安装成功')
        check(second.returncode!=0,'重复安装拒绝覆盖')
        for name in ('pet.json','spritesheet.webp'):
            p=Path(temp)/'esign-ai-elephant'/name
            check(p.exists() and p.read_bytes()==(ROOT/name).read_bytes(),f'安装后 {name} 一致')

    # 深浅背景与三档尺寸的可视检查，不生成/重画任何角色。
    qa=Image.new('RGB',(1200,730),'#f6f4f0');d=ImageDraw.Draw(qa)
    for r,bg in enumerate(('#ffffff','#27282e')):
        d.rectangle((0,r*365,1200,(r+1)*365),fill=bg)
        for col,name in enumerate(business['states']):
            x=col*132+6
            d.text((x+5,r*365+10),business['states'][name]['label'],font=font(16),fill='#888888')
            for s,y in ((64,45),(96,130),(128,238)):
                im=Image.open(ROOT/f'exports/{s}/{name}/000.png')
                qa.paste(im,(x+(128-s)//2,r*365+y),im)
    qa.save(ROOT/'qa/size-background-check.png')
    report={'ok':not failures,'checkCount':len(checks),'failures':failures,'frameCounts':counts,
            'uniqueFileCounts':unique,'businessFrames':sum(counts[k] for k in business['states']),
            'nativeOccupiedCells':len(used),'runtimeTested':False,'petdexImporterTested':False}
    write_json(ROOT/'qa/package-validation.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if failures: raise SystemExit(1)
if __name__=='__main__':main()
