#!/usr/bin/env python3
"""方向修订回归：不把工程检查当作透视/品牌视觉验收。"""
import hashlib
import json
import zipfile
from PIL import Image
from build_package import ROOT, RESAMPLE, zero_hidden, write_json

cfg=json.loads((ROOT/'source/artwork.json').read_text())['sheets']
approved=ROOT/'review-samples/upper-right-v2.png'
source=ROOT/'source/revisions/look-v3/002.png'
record=json.loads((ROOT/'source/revision-v3-generation.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==record['approvedSha256']
if approved.exists():
    assert source.read_bytes()==approved.read_bytes(), '已确认样图必须原样保留'
final_record=json.loads((ROOT/'source/final-vertical-generation.json').read_text())
for sample in final_record['samples']:
    adopted=ROOT/sample['file']
    assert hashlib.sha256(adopted.read_bytes()).hexdigest()==sample['sha256'], sample['file']
    review_sample=ROOT/sample.get('approvedSample', sample['file'])
    if review_sample.exists():
        assert adopted.read_bytes()==review_sample.read_bytes(), '上下确认原画必须原样采用'

# 与打包前V1.1相比，只允许这次明确批准的上下两个方向改变。
final_backup=ROOT/'.archive/pre-final-vertical-v3/esign-ai-elephant-complete.zip'
final_changed=[]; final_unchanged=[]; changed_cells=[]
if final_backup.exists():
    with zipfile.ZipFile(final_backup) as z:
        for folder in ('frames','native-frames'):
            for p in sorted((ROOT/folder).glob('*/*.png')):
                rel=p.relative_to(ROOT).as_posix()
                old=z.read('esign-elephant-pet/'+rel)
                (final_changed if old!=p.read_bytes() else final_unchanged).append(rel)
    assert set(final_changed)=={'native-frames/look/000.png','native-frames/look/008.png'}, final_changed
    assert len(final_unchanged)==88, len(final_unchanged)
    old_atlas=Image.open(ROOT/'.archive/pre-final-vertical-v3/spritesheet.webp').convert('RGBA')
    new_atlas=Image.open(ROOT/'spritesheet.webp').convert('RGBA')
    for row in range(11):
        for col in range(8):
            box=(col*192,row*208,(col+1)*192,(row+1)*208)
            if old_atlas.crop(box).tobytes()!=new_atlas.crop(box).tobytes():
                changed_cells.append([row,col])
    assert changed_cells==[[9,0],[10,0]], changed_cells
expected={f'native-frames/look/{i:03}.png' for i in range(16)}
expected.update({'frames/error/002.png','frames/error/003.png','frames/task_received/001.png'})
backup=ROOT/'.archive/pre-v3/esign-ai-elephant-complete.zip'
changed=[]; unchanged=[]
if backup.exists():
    with zipfile.ZipFile(backup) as z:
        for folder in ('frames','native-frames'):
            for p in sorted((ROOT/folder).glob('*/*.png')):
                rel=p.relative_to(ROOT).as_posix()
                old=z.read('esign-elephant-pet/'+rel)
                (changed if old!=p.read_bytes() else unchanged).append(rel)
    assert set(changed)==expected, (set(changed)-expected, expected-set(changed))

frames=[Image.open(ROOT/f'native-frames/look/{i:03}.png').convert('RGBA') for i in range(16)]
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in frames})==16
feet=[]
for im in frames:
    a=im.getchannel('A')
    assert a.getbbox()[3]==468
    # 几何尺度用实心边缘测量，排除LANCZOS低alpha晕边。
    b=a.point([0]*32+[255]*224).crop((0,440,512,468)).getbbox()
    assert abs((b[0]+b[2])/2-256)<=2, b
    assert abs(b[2]-b[0]-170)<=4, b
    feet.append({'width':b[2]-b[0],'center':(b[0]+b[2])/2})

review=[zero_hidden(im.resize((256,256),RESAMPLE)) for im in frames]
review[0].save(ROOT/'previews/look-clockwise.webp',save_all=True,append_images=review[1:],
               duration=[320]*16,loop=0,lossless=True,exact=True,method=6)
report={'ok':True,'approvedSourceUnchanged':True,'changedFrameCount':len(changed),
        'unchangedFrameCount':len(unchanged),'changedFrames':changed,'feet':feet,
        'scope':'16方向 + error002/003 + task_received001',
        'finalChangedFrames':final_changed,'finalUnchangedFrameCount':len(final_unchanged),
        'finalChangedAtlasCells':changed_cells,
        'approvedVerticalSourcesUnchanged':True,
        'visualApproval':'Approved source hashes retained; runtime acceptance is recorded separately in source/client-compatibility.json',
        'runtimeTested':False}
write_json(ROOT/'qa/revision-validation.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
