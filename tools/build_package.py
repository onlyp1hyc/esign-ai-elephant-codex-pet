#!/usr/bin/env python3
"""从 AI 原画构建宠物资源。只处理像素/布局，不绘制角色或形变动画。"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RESAMPLE = Image.Resampling.LANCZOS
NATIVE = [
    ('idle', 'idle', list(range(6)), [280,110,110,140,140,320]),
    ('running-right', 'walk_right', list(range(8)), [120]*7+[220]),
    ('running-left', 'walk_left', list(range(8)), [120]*7+[220]),
    ('waving', 'greeting', [0,2,3,5], [140]*3+[280]),
    ('jumping', 'task_received', [1,2,3,4,5], [140]*4+[280]),
    ('failed', 'error', list(range(8)), [140]*7+[240]),
    ('waiting', 'waiting_approval', list(range(6)), [150]*5+[260]),
    ('running', 'working', [0,1,2,3,4,6], [120]*5+[220]),
    ('review', 'thinking', list(range(6)), [150]*5+[280]),
]

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.webp':
        image.save(path, lossless=True, exact=True, method=6)
    else:
        image.save(path)

def zero_hidden(image):
    data = np.array(image.convert('RGBA'))
    data[data[:,:,3] == 0] = 0
    return Image.fromarray(data)

def largest_component(mask):
    """逐行游程并查集；避免依赖 OpenCV/Scipy，保留角色主体连通域。"""
    parent, spans, previous = [], [], []
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for y, row in enumerate(mask):
        changes = np.diff(np.pad(row.astype(np.int8), (1,1)))
        starts, ends = np.flatnonzero(changes == 1), np.flatnonzero(changes == -1)
        current, cursor = [], 0
        for start, end in zip(starts, ends):
            idx = len(parent)
            parent.append(idx)
            current.append((int(start), int(end), idx))
            spans.append((y, int(start), int(end), idx))
            while cursor < len(previous) and previous[cursor][1] < start:
                cursor += 1
            for pstart, pend, pidx in previous[cursor:]:
                if pstart > end:
                    break
                parent[find(idx)] = find(pidx)
        previous = current
    sizes = {}
    for y, start, end, idx in spans:
        root = find(idx)
        sizes[root] = sizes.get(root, 0) + end-start
    if not sizes:
        raise ValueError('无角色像素')
    winner = max(sizes, key=sizes.get)
    result = np.zeros(mask.shape, dtype=np.uint8)
    for y, start, end, idx in spans:
        if find(idx) == winner:
            result[y, start:end] = 255
    return result, len(sizes)

def clean(image):
    data = np.array(image.convert('RGBA'))
    main, count = largest_component(data[:,:,3] >= 32)
    # 仅在主体周围保留原始抗锯齿；移除生成时游离的细小噪点。
    neighborhood = np.asarray(Image.fromarray(main).filter(ImageFilter.MaxFilter(5))) > 0
    alpha = data[:,:,3]
    alpha[(~neighborhood) | (alpha <= 3)] = 0
    alpha[alpha >= 240] = 255
    data[alpha == 0] = 0
    out = Image.fromarray(data)
    bbox = out.getchannel('A').getbbox()
    return out.crop(bbox), {'bbox':list(bbox), 'componentsBefore':count}

def normalize(cutout, spec, offset=0):
    alpha = cutout.getchannel('A')
    if 'feetWidth' in spec:
        # 转头不应改变躯干尺度：用未运动的脚底宽度及中心对齐。
        # 只做整图等比缩放/平移，不改耳朵、五官或局部形体。
        foot = alpha.crop((0, round(cutout.height*.92), cutout.width, cutout.height)).getbbox()
        factor = spec['feetWidth']/(foot[2]-foot[0])
        if cutout.height*factor > 442:
            raise ValueError('脚部标定超出安全高度，需检查原画而非压缩头身')
        sized = cutout.resize((round(cutout.width*factor),round(cutout.height*factor)), RESAMPLE)
        left = round(256-(foot[0]+foot[2])*.5*factor)
        if left < 8 or left+sized.width > 504:
            raise ValueError('脚部标定超出安全宽度，需检查原画')
        out = Image.new('RGBA',(512,512))
        out.alpha_composite(sized,(left,468-sized.height+offset))
        return zero_hidden(out)
    # 旧业务帧保持原有归一化，避免本次方向修订影响无关动作。
    hb = alpha.crop((0,0,cutout.width,round(cutout.height*.58))).getbbox()
    factor = 380/cutout.height if spec.get('sideView') else 422/(hb[2]-hb[0])
    factor = min(factor, 448/cutout.width, 422/cutout.height)
    sized = cutout.resize((round(cutout.width*factor),round(cutout.height*factor)), RESAMPLE)
    out = Image.new('RGBA',(512,512))
    out.alpha_composite(sized, ((512-sized.width)//2,468-sized.height+offset))
    return zero_hidden(out)

def native_cell(frame):
    # 512 工作画布等比变为192，底线统一至约191px；不拉伸头身。
    resized = frame.resize((192,192), RESAMPLE)
    out = Image.new('RGBA',(192,208))
    out.alpha_composite(resized,(0,16))
    return zero_hidden(out)

def font(size):
    for p in ['/System/Library/Fonts/STHeiti Medium.ttc',
              '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(p).exists():
            return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)

def preview(frames, specs):
    out = Image.new('RGB',(1320,1450),'#f7f5f2')
    draw = ImageDraw.Draw(out)
    draw.text((64,46),'eSign AI 小象',font=font(48),fill='#242424')
    draw.text((65,112),'忠于原始设定 · 九种状态 · 透明动画资源',font=font(22),fill='#75716e')
    draw.rounded_rectangle((1058,57,1255,104),radius=22,fill='#d81e06')
    draw.text((1081,69),'ASSET PACK 1.2',font=font(18),fill='white')
    for i,(name,spec) in enumerate(specs.items()):
        if 'label' not in spec:
            continue
        x,y = 52+(i%3)*416,184+(i//3)*402
        draw.rounded_rectangle((x,y,x+392,y+374),radius=24,fill='white')
        thumb=frames[name][spec['representative']].resize((310,310),RESAMPLE)
        out.paste(thumb,(x+41,y+2),thumb)
        draw.text((x+25,y+309),spec['label'],font=font(25),fill='#252525')
        draw.text((x+25,y+345),name,font=font(14),fill='#8a8582')
        draw.text((x+311,y+326),f"{len(frames[name])} 帧",font=font(16),fill='#bd3326')
    draw.text((65,1410),'512px 工作帧 / 64 · 96 · 128px 导出 / Codex V2',font=font(18),fill='#8a8582')
    save(out,ROOT/'preview.png')

def export_manifest():
    value={'id':'esign-ai-elephant','displayName':'eSign AI 小象',
           'description':'亲和、可靠的 eSign AI 小象，陪伴每一次思考与完成。',
           'spriteVersionNumber':2,'spritesheetPath':'spritesheet.webp'}
    write_json(ROOT/'pet.json',value)
    return value

def direction_preview(frames):
    out=Image.new('RGB',(1120,820),'#f7f5f2');d=ImageDraw.Draw(out)
    d.text((40,25),'视线方向 · 头、脸与短鼻保持同向',font=font(30),fill='#292524')
    labels=['向上','右上','向右','右下','向下','左下','向左','左上']
    for k,i in enumerate(range(0,16,2)):
        x,y=30+(k%4)*275,90+(k//4)*350
        d.rounded_rectangle((x,y,x+260,y+320),radius=16,fill='white')
        im=frames[i].resize((255,255),RESAMPLE)
        out.paste(im,(x+2,y+8),im)
        d.text((x+25,y+274),f'{labels[k]}  {i*22.5:g}°',font=font(21),fill='#645951')
    save(out,ROOT/'direction-preview.png')

def build():
    cfg=json.loads((ROOT/'source/artwork.json').read_text())
    specs=cfg['sheets']
    frames, extraction = {}, {}
    for name,spec in specs.items():
        cuts,records=[],[]
        if 'files' in spec:
            for path in spec['files']:
                original=Image.open(ROOT/path).convert('RGBA')
                cut,record=clean(original)
                record.update(source=path,sourceSize=list(original.size))
                cuts.append(cut); records.append(record)
            source_size=None
        else:
            sheet=Image.open(ROOT/f'source/sheets/{name}.png').convert('RGBA')
            source_size=list(sheet.size)
            cols,rows=spec['grid']
            for idx in range(cols*rows):
                x,y=idx%cols,idx//cols
                box=(round(x*sheet.width/cols),round(y*sheet.height/rows),
                     round((x+1)*sheet.width/cols),round((y+1)*sheet.height/rows))
                cut,record=clean(sheet.crop(box))
                record['cell']=list(box)
                cuts.append(cut); records.append(record)
        for key,override in spec.get('overrides',{}).items():
            idx=int(key)
            original=Image.open(ROOT/override['file']).convert('RGBA')
            cuts[idx],records[idx]=clean(original)
            records[idx].update(source=override['file'],sourceSize=list(original.size))
        offsets=spec.get('yOffset',[0]*len(spec['select']))
        frames[name]=[normalize(cuts[idx],{**spec,**spec.get('overrides',{}).get(str(idx),{})},off)
                      for idx,off in zip(spec['select'],offsets)]
        folder=ROOT/('frames' if 'label' in spec else 'native-frames')/name
        for i,frame in enumerate(frames[name]):
            save(frame,folder/f'{i:03}.png')
        if 'label' in spec:
            save(frames[name][spec['representative']],ROOT/f'source/state_{name}.png')
        extraction[name]={'sourceSize':source_size,'cells':records,'selected':spec['select']}
        print(f'{name}: {len(frames[name])} frames',flush=True)
    master,_=clean(Image.open(ROOT/'source/generated/character_master.png'))
    save(normalize(master,{}),ROOT/'source/character_master.png')
    write_json(ROOT/'qa/extraction.json',extraction)

    atlas=Image.new('RGBA',(1536,2288))
    rows=[]
    for row,(name,key,selection,durations) in enumerate(NATIVE):
        for col,idx in enumerate(selection):
            atlas.paste(native_cell(frames[key][idx]),(col*192,row*208))
        rows.append({'row':row,'state':name,'source':key,'frameIndices':selection,'durationMs':durations})
    atlas.paste(native_cell(frames['idle'][0]),(6*192,0))
    for i,frame in enumerate(frames['look']):
        atlas.paste(native_cell(frame),((i%8)*192,(9+i//8)*208))
    save(zero_hidden(atlas),ROOT/'spritesheet.webp')
    native={'spriteVersionNumber':2,'size':[1536,2288],'grid':[8,11],'cell':[192,208],
            'rows':rows,'neutralCell':[0,6],
            'lookDirections':[{'degrees':i*22.5,'row':9+i//8,'column':i%8} for i in range(16)]}
    write_json(ROOT/'spritesheet.json',native)
    export_manifest()

    business={'format':'esign-pet-business-states-v1','cellSize':96,'atlas':'spritesheet_semantic.webp',
              'frameSize':512,'states':{},'events':{}}
    semantic=[(k,v) for k,v in specs.items() if 'label' in v]
    for size in (64,96,128):
        sheet=Image.new('RGBA',(size*8,size*9))
        for row,(name,spec) in enumerate(semantic):
            for col,frame in enumerate(frames[name]):
                small=zero_hidden(frame.resize((size,size),RESAMPLE))
                save(small,ROOT/f'exports/{size}/{name}/{col:03}.png')
                sheet.paste(small,(col*size,row*size))
        save(sheet,ROOT/f'exports/{size}/spritesheet.webp')
        if size==96:
            save(sheet,ROOT/'spritesheet_semantic.webp')
    for row,(name,spec) in enumerate(semantic):
        paths=[f'frames/{name}/{i:03}.png' for i in range(len(frames[name]))]
        business['states'][name]={'label':spec['label'],'frames':paths,'durationMs':spec['duration'],
          'atlasRow':row,'nativeFallback':spec['native'],
          'nativeIsApproximation':spec.get('fallback',name=='thinking')}
        business['events'][spec['event']]=name
        anim=[zero_hidden(im.resize((256,256),RESAMPLE)) for im in frames[name]]
        dest=ROOT/f'previews/{name}.webp'; dest.parent.mkdir(exist_ok=True)
        anim[0].save(dest,save_all=True,append_images=anim[1:],duration=spec['duration'],
                     loop=0,lossless=True,exact=True,method=6)
    write_json(ROOT/'business-states.json',business)
    write_json(ROOT/'spritesheet_semantic.json',business)
    (ROOT/'demo').mkdir(exist_ok=True)
    (ROOT/'demo/data.js').write_text('window.PET_DATA = '+json.dumps({'business':business,'native':native},ensure_ascii=False)+';\n')
    preview(frames,specs)
    direction_preview(frames['look'])
    print('构建完成：58 业务帧、16 移动帧、16 视线帧；V2 atlas 74 有效单元。')

def archive():
    out=ROOT/'dist'; out.mkdir(exist_ok=True)
    installer=out/'esign-ai-elephant-codex-v2.zip'
    runtime=('pet.json','spritesheet.webp')
    unchanged=False
    if installer.exists():
        with zipfile.ZipFile(installer) as z:
            unchanged=(set(z.namelist())=={'esign-ai-elephant/'+name for name in runtime}
                       and all(z.read('esign-ai-elephant/'+name)==(ROOT/name).read_bytes() for name in runtime))
    # Preserve the manually accepted installation ZIP byte-for-byte when current.
    if not unchanged:
        with zipfile.ZipFile(installer,'w',zipfile.ZIP_DEFLATED) as z:
            for name in runtime:
                z.write(ROOT/name,'esign-ai-elephant/'+name)
    folders=['frames','native-frames','exports','source','previews','demo','tools','schemas']
    files=[ROOT/p for p in ['README.md','README.zh-CN.md','LICENSE','BRAND_ASSETS.md','.gitignore','manifest.md','visual-audit.md','release-validation.json','requirements.txt','pet.json','spritesheet.webp',
                            'spritesheet.json','spritesheet_semantic.json','spritesheet_semantic.webp','business-states.json','preview.png','direction-preview.png']]
    for folder in folders:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts
                     and p.suffix in {'.png','.webp','.json','.md','.py','.cjs','.js','.html'}
                     and not any(part.startswith('.') for part in p.relative_to(ROOT).parts))
    with zipfile.ZipFile(out/'esign-ai-elephant-complete.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p,'esign-elephant-pet/'+p.relative_to(ROOT).as_posix())
    checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.zip')}
    write_json(out/'sha256.json',checksums)
    print(json.dumps(checksums,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-only',action='store_true')
    args=parser.parse_args()
    if args.zip_only:
        archive()
    else:
        build()
