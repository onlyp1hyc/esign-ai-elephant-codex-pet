#!/usr/bin/env python3
"""仅将已有帧排成编号校样，便于人工核对；不修改角色像素。"""
import json
from PIL import Image, ImageDraw
from build_package import ROOT, font, RESAMPLE

cfg=json.loads((ROOT/'source/artwork.json').read_text())['sheets']
outdir=ROOT/'qa/visual-audit';outdir.mkdir(parents=True,exist_ok=True)
for name,spec in cfg.items():
    folder=ROOT/('frames' if 'label' in spec else 'native-frames')/name
    paths=sorted(folder.glob('*.png'))
    cols=4 if len(paths)>6 else 3
    rows=(len(paths)+cols-1)//cols
    canvas=Image.new('RGB',(cols*340,rows*370+55),'#eeedea');d=ImageDraw.Draw(canvas)
    d.text((20,15),f'{name} / 当前交付帧（编号从0开始）',font=font(21),fill='#333333')
    for i,p in enumerate(paths):
        x,y=(i%cols)*340,(i//cols)*370+55
        im=Image.open(p).convert('RGBA').resize((330,330),RESAMPLE)
        d.rectangle((x+4,y+4,x+336,y+363),fill='white')
        canvas.paste(im,(x+5,y),im)
        source_idx=spec['select'][i]
        origin='AI 单帧修订' if 'files' in spec or str(source_idx) in spec.get('overrides',{}) else f'source cell {source_idx}'
        d.text((x+20,y+336),f'{i:03}  ·  {origin}',font=font(16),fill='#666666')
    canvas.save(outdir/f'{name}.png')
print(outdir)
