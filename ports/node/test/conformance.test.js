'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
const {lint}=require('../lib/lint.js');
const C=path.join(__dirname,'..','..','conformance');
const V=JSON.parse(fs.readFileSync(path.join(C,'vectors.json'),'utf8'));
const E=JSON.parse(fs.readFileSync(path.join(C,'expected.json'),'utf8')).results;
let n=0;
for(const c of V.cases){const g=lint(c.text||'');const e=E.find(x=>x.name===c.name);
  assert.strictEqual(g.clarity,e.clarity,`${c.name}: clarity`);
  assert.strictEqual(g.defects.length,e.defects.length,`${c.name}: defects`);
  g.defects.forEach((d,i)=>assert.strictEqual(d.rule,e.defects[i].rule,`${c.name}: rule ${i}`));n++;}
console.log(`ok - ${n} conformance cases pass`);
