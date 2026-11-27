import * as S from './strategic.mjs';
const api=(function targetFactory(S){
 const check=(x,m)=>{if(!x)throw Error(m)};
 const Z=[0n,1n],O=[1n,1n],EPS=[1n,5n];
 function f(a,b=1n){check(b!==0n,'denominator');if(b<0n){a=-a;b=-b}let x=a<0n?-a:a,y=b;while(y){[x,y]=[y,x%y]}return [a/x,b/x]}
 const q=s=>{check(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational required');const [a,b='1']=s.split('/');return f(BigInt(a),BigInt(b))};
 const str=a=>a[0]+'/'+a[1],add=(a,b)=>f(a[0]*b[1]+b[0]*a[1],a[1]*b[1]),sub=(a,b)=>add(a,[-b[0],b[1]]),mul=(a,b)=>f(a[0]*b[0],a[1]*b[1]),div=(a,b)=>f(a[0]*b[1],a[1]*b[0]),cmp=(a,b)=>{const d=a[0]*b[1]-b[0]*a[1];return d<0n?-1:d>0n?1:0},sum=a=>a.reduce(add,Z),dot=(a,b)=>sum(a.map((v,i)=>mul(v,b[i]))),mix=(a,b,t)=>a.map((v,i)=>add(mul(v,sub(O,t)),mul(b[i],t))),pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?O:Z),uniform=n=>Array.from({length:n},()=>f(1n,BigInt(n))),show=a=>a.map(str);
 function selectTarget(g,solver,target,{maxLines=24}={}){
  check(Number.isSafeInteger(maxLines)&&maxLines>=0&&maxLines<=256,'line cap');
  const R=g.R.map(r=>r.map(q)),C=g.C.map(r=>r.map(q)),m=R.length,n=R[0].length;
  const keys=[...new Set([...g.endings.flat(),...Object.keys(target)])].sort(),tgt=keys.map(k=>q(target[k]||'0'));
  check(cmp(sum(tgt),O)===0&&tgt.every(v=>cmp(v,Z)>=0),'invalid target');
  let best=null,lines=0,feasibleLines=0,checked=0,seedChecked=0,improvedLines=0;const seen=new Set();
  function constraints(x,y){
   const a=R.map(row=>dot(row,y)),b=Array.from({length:n},(_,j)=>dot(x,C.map(row=>row[j])));
   const u=dot(x,a),v=dot(y,b);
   return [...a.map(z=>sub(sub(z,u),EPS)),...b.map(z=>sub(sub(z,v),EPS))];
  }
  function law(x,y){
   const d=new Map(keys.map(k=>[k,Z]));
   for(let i=0;i<m;i++)for(let j=0;j<n;j++){const k=g.endings[i][j];d.set(k,add(d.get(k),mul(x[i],y[j])))}
   return keys.map(k=>d.get(k));
  }
  function consider(x,y,source){
   const xs=show(x),ys=show(y),key=xs.join(',')+'|'+ys.join(',');
   if(seen.has(key))return;seen.add(key);checked++;
   const cert=S.certify(g.R,g.C,xs,ys);
   if(!cert.certified)return;
   const dist=S.endingLaw(g,cert),tv=S.targetTV(dist,target);
   const r={certificate:cert,ending_law:dist,target_tv:tv,source,key};
   if(!best||cmp(q(tv),q(best.target_tv))<0||(tv===best.target_tv&&(cmp(q(cert.max_regret),q(best.certificate.max_regret))<0||(cert.max_regret===best.certificate.max_regret&&key<best.key))))best=r;
  }
  // All previous strategy candidates are rechecked; the solver's reported
  // objective is never used as a certificate.
  for(const h of [solver.certificate,...solver.history])consider(h.x.map(q),h.y.map(q),'solver_seed');
  seedChecked=checked;
  if(!best)return {status:'unresolved',selected:null,lines,feasibleLines,checked,seedChecked,improvedLines};
  const seedBest=best;
  function line(side,z){
   if(lines>=maxLines)return;
   lines++;
   const x=best.certificate.x.map(q),y=best.certificate.y.map(q),x1=side===0?z:x,y1=side===1?z:y;
   const a=constraints(x,y),b=constraints(x1,y1);
   let lo=Z,hi=O;
   for(let i=0;i<a.length;i++){
    const p=a[i],r=b[i],sp=cmp(p,Z),sr=cmp(r,Z);
    if(sp>0&&sr>0)return;
    if(sp>0||sr>0){const t=div(p,sub(p,r));if(sp>0&&cmp(t,lo)>0)lo=t;if(sr>0&&cmp(t,hi)<0)hi=t}
   }
   if(cmp(lo,hi)>0)return;feasibleLines++;
   const d0=law(x,y),d1=law(x1,y1),breaks=[lo,hi];
   for(let i=0;i<keys.length;i++){
    const delta=sub(d1[i],d0[i]);if(cmp(delta,Z)===0)continue;
    const t=div(sub(tgt[i],d0[i]),delta);
    if(cmp(t,lo)>=0&&cmp(t,hi)<=0)breaks.push(t);
   }
   const old=best.target_tv;
   for(const t of breaks){
    const xx=mix(x,x1,t),yy=mix(y,y1,t);
    check(constraints(xx,yy).every(v=>cmp(v,Z)<=0),'line feasibility inconsistency');
    consider(xx,yy,'exact_line_'+side);
   }
   if(cmp(q(best.target_tv),q(old))<0)improvedLines++;
  }
  while(lines<maxLines){
   const before=best.key;
   for(let side=0;side<2&&lines<maxLines;side++){const n0=side===0?m:n;for(const z of [...Array.from({length:n0},(_,i)=>pure(n0,i)),uniform(n0)]){if(lines>=maxLines)break;line(side,z)}}
   if(best.key===before)break;
  }
  check(cmp(q(best.target_tv),q(seedBest.target_tv))<=0,'target incumbent degraded');
  return {status:'certified',selected:best,seed_best:seedBest,lines,feasibleLines,checked,seedChecked,improvedLines};
 }
 function choose(rows,authorBest,allow='0'){
  const slack=q(allow);check(cmp(slack,Z)>=0,'negative slack');
  const limit=add(q(authorBest.author_loss),slack);
  const candidates=rows.filter(r=>r.selection.selected&&cmp(q(r.author_loss),limit)<=0);
  const rank=(a,b)=>cmp(q(a.selection.selected.target_tv),q(b.selection.selected.target_tv))||cmp(q(a.author_loss),q(b.author_loss))||cmp(q(a.selection.selected.certificate.max_regret),q(b.selection.selected.certificate.max_regret))||a.key.localeCompare(b.key);
  candidates.sort(rank);
  return {status:candidates.length?'certified':'unresolved',author_loss_limit:str(limit),selected:candidates[0]||null,eligible:candidates.length};
 }
 return {selectTarget,choose};
})(S);
export const {selectTarget,choose}=api;
