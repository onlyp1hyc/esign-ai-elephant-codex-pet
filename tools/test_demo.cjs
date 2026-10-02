// 无浏览器、无网络的 DOM 桩单元测试；不代替 UI/布局验收。
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'demo/index.html'),'utf8');
const elements=new Map();
class Element{
  constructor(id=''){this.id=id;this.style={};this.children=[];this.dataset={};this.attributes={};this.value='';this.textContent='';}
  append(child){this.children.push(child);if(!this.value&&child.value)this.value=child.value;}
  setAttribute(k,v){this.attributes[k]=v;}
  getBoundingClientRect(){return {left:0,top:0,width:192,height:208};}
}
for(const [,id] of html.matchAll(/id="([^"]+)"/g))elements.set(id,new Element(id));
elements.get('mode').value='business';
let scheduled=null;
const env={window:{},document:{getElementById:id=>elements.get(id),createElement:()=>new Element()},Image:class{},
  matchMedia:()=>({matches:false}),performance:{now:()=>0},requestAnimationFrame:fn=>{scheduled=fn;},
  setInterval:()=>1,clearInterval:()=>{},console};
vm.createContext(env);
vm.runInContext(fs.readFileSync(path.join(root,'demo/data.js'),'utf8'),env);
const inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
vm.runInContext(inline,env);
assert.equal(elements.get('states').children.length,9);
assert.equal(elements.get('nativeState').children.length,9);
assert.equal(elements.get('title').textContent,'待机');
for(const button of elements.get('states').children){button.onclick();assert.equal(elements.get('subtitle').textContent,button.dataset.state);scheduled(1000);elements.get('next').onclick();assert.ok(elements.get('sprite').style.backgroundPosition);}
elements.get('mode').value='native';elements.get('mode').onchange();
for(const option of elements.get('nativeState').children){elements.get('nativeState').value=option.value;elements.get('nativeState').onchange();assert.equal(elements.get('subtitle').textContent,option.value);}
elements.get('mode').value='look';elements.get('mode').onchange();
for(let i=0;i<16;i++){elements.get('angle').oninput({target:{value:i}});assert.equal(elements.get('readout').textContent,`${i+1} / 16`);}
elements.get('stage').onpointermove({clientX:300,clientY:83.2});
assert.equal(elements.get('readout').textContent,'5 / 16');
elements.get('journey').onclick();assert.equal(elements.get('subtitle').textContent,'greeting');
for(const [,src]of html.matchAll(/(?:src|href)="(\.\.[^"]+|data\.js)"/g))assert.ok(fs.existsSync(path.resolve(root,'demo',src)),src);
console.log('PASS: Demo syntax, 9 business states, 9 native rows, 16 directions, pointer mapping, playback controls and local references. No browser UI tested.');
