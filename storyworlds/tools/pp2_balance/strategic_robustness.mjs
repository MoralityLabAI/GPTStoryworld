import * as S from './strategic.mjs';
const api=(function robustFactory(S){
 const ok=(x,m)=>{if(!x)throw Error(m)};
 const Z=[0n,1n],O=[1n,1n],E=[1n,5n];
 function f(a,b=1n){ok(b!==0n,'denominator');if(b<0n){a=-a;b=-b}let x=a<0n?-a:a,y=b;while(y){[x,y]=[y,x%y]}return [a/x,b/x]}
 const q=s=>{ok(typeof s==='string'&&/^-?\d+(\/[1-9]\d*)?$/.test(s),'rational string');const [a,b='1']=s.split('/');return f(BigInt(a),BigInt(b))};
 const st=a=>a[0]+'/'+a[1],a=(x,y)=>f(x[0]*y[1]+y[0]*x[1],x[1]*y[1]),b=(x,y)=>a(x,[-y[0],y[1]]),m=(x,y)=>f(x[0]*y[0],x[1]*y[1]),d=(x,y)=>f(x[0]*y[1],x[1]*y[0]),c=(x,y)=>{const v=x[0]*y[1]-y[0]*x[1];return v<0n?-1:v>0n?1:0},sum=x=>x.reduce(a,Z),max=x=>x.reduce((u,v)=>c(u,v)>=0?u:v),min=x=>x.reduce((u,v)=>c(u,v)<=0?u:v),num=x=>Number(x[0])/Number(x[1]);
 const pure=(n,i)=>Array.from({length:n},(_,j)=>i===j?O:Z),uniform=n=>Array.from({length:n},()=>f(1n,BigInt(n))),mix=(x,y,t)=>x.map((u,i)=>a(m(u,b(O,t)),m(y[i],t))),show=x=>x.map(st);
 function model(g,target){
  const R=g.R.map(row=>row.map(q)),C=g.C.map(row=>row.map(q)),nr=R.length,nc=R[0].length;
  ok(nr*nc<=64&&nr>0&&nc>0,'game cell cap');
  S.certify(g.R,g.C,show(uniform(nr)),show(uniform(nc)));
  ok(g.endings.length===nr&&g.endings.every(r=>r.length===nc&&r.every(k=>typeof k==='string'&&k.length)),'endings shape');
  const ends=[...new Set([...g.endings.flat(),...Object.keys(target)])].sort();ok(ends.length>=2&&ends.length<=6,'2 to 6 ending cap');
  const targetVec=ends.map(k=>q(target[k]??'0'));ok(targetVec.every(x=>c(x,Z)>=0)&&c(sum(targetVec),O)===0,'target simplex');
  const masks=Array.from({length:(1<<ends.length)-2},(_,k)=>k+1);
  const cells=[];
  for(let i=0;i<nr;i++)for(let j=0;j<nc;j++){
   const gaps=[...R.map(row=>b(b(row[j],R[i][j]),E)),...C[i].map(v=>b(b(v,C[i][j]),E))];
   const k=ends.indexOf(g.endings[i][j]);cells.push({gaps,out:masks.map(mask=>mask&(1<<k)?O:Z)});
  }
  const tgt=masks.map(mask=>sum(targetVec.filter((_,i)=>mask&(1<<i))));
  return {nr,nc,ends,masks,cells,tgt};
 }
 // Every gap is a pure deviation minus epsilon; its expectation under
 // an independent root mix equals the corresponding Nash inequality.
 // For any nonnegative multipliers lambda, objective <= max_cell
 // (objective(cell) - lambda dot gap(cell)) on every feasible profile.
 function dual(M,k,sweeps){
  const h=M.nr+M.nc,lambda=Array.from({length:h},()=>Z);
  const residual=(cell,skip)=>b(cell.out[k],sum(cell.gaps.map((v,i)=>i===skip?Z:m(v,lambda[i]))));
  const upper=()=>max(M.cells.map(cell=>residual(cell,-1)));
  let value=upper(),updates=0;
  for(let pass=0;pass<sweeps;pass++){
   let changed=false;
   for(let i=0;i<h;i++){
    const lines=M.cells.map(cell=>({intercept:residual(cell,i),slope:[-cell.gaps[i][0],cell.gaps[i][1]]}));
    const candidates=new Map([['0/1',Z],[st(lambda[i]),lambda[i]]]);
    for(let u=0;u<lines.length;u++)for(let v=u+1;v<lines.length;v++){
     const den=b(lines[u].slope,lines[v].slope);if(c(den,Z)===0)continue;
     const x=d(b(lines[v].intercept,lines[u].intercept),den);if(c(x,Z)>=0)candidates.set(st(x),x);
    }
    let t=lambda[i],best=value;
    for(const x of candidates.values()){
     const y=max(lines.map(l=>a(l.intercept,m(l.slope,x))));
     if(c(y,best)<0||(c(y,best)===0&&c(x,t)<0)){t=x;best=y}
    }
    if(c(t,lambda[i])!==0){lambda[i]=t;changed=true;updates++}value=best;
   }
   if(!changed)break;
  }
  ok(c(upper(),value)===0,'dual internal consistency');
  return {lambda:show(lambda),upper:st(value),updates};
 }
 function verifyDual(M,k,cert){
  const l=cert.lambda.map(q),u=q(cert.upper);
  ok(l.length===M.nr+M.nc&&l.every(x=>c(x,Z)>=0),'invalid dual multipliers');
  for(const cell of M.cells)ok(c(b(cell.out[k],sum(cell.gaps.map((v,i)=>m(v,l[i])))),u)<=0,'dual upper inequality violated');
  return min([O,u]);
 }
 function evaluate(M,x,y){
  const gaps=Array.from({length:M.nr+M.nc},()=>Z),out=M.masks.map(()=>Z);
  for(let i=0;i<M.nr;i++)for(let j=0;j<M.nc;j++){
   const w=m(x[i],y[j]);if(c(w,Z)===0)continue;
   const cell=M.cells[i*M.nc+j];
   for(let k=0;k<gaps.length;k++)gaps[k]=a(gaps[k],m(w,cell.gaps[k]));
   for(let k=0;k<out.length;k++)if(cell.out[k][0])out[k]=a(out[k],w);
  }
  return {gaps,out};
 }
 // Exact one-player line search over pure and uniform endpoints.
 function witnessSearch(g,M,starts,sweeps){
  const best=M.masks.map(()=>null);let tested=0,feasible=0,improved=0;
  function visit(x,y){
   tested++;const v=evaluate(M,x,y);
   if(v.gaps.some(r=>c(r,Z)>0))return;
   feasible++;
   const better=v.out.map((r,k)=>!best[k]||c(r,best[k].value)>0);
   if(!better.some(Boolean))return;
   const cert=S.certify(g.R,g.C,show(x),show(y));ok(cert.certified,'feasible witness failed independent verifier');
   for(let k=0;k<better.length;k++)if(better[k]){best[k]={value:v.out[k],x,y,cert};improved++}
  }
  for(const p of starts){
   const cert=S.certify(g.R,g.C,p.x,p.y);if(cert.certified)visit(cert.x.map(q),cert.y.map(q));
  }
  ok(best.every(Boolean),'no feasible seed');
  for(let k=0;k<best.length;k++)for(let pass=0;pass<sweeps;pass++){
   const before=best[k].value;
   for(let side=0;side<2;side++){
    const n=side===0?M.nr:M.nc;
    for(const z of [...Array.from({length:n},(_,i)=>pure(n,i)),uniform(n)]){
     const {x,y}=best[k],x1=side===0?z:x,y1=side===1?z:y,v0=evaluate(M,x,y),v1=evaluate(M,x1,y1);
     if(c(v1.out[k],v0.out[k])<=0)continue;
     let hi=O;
     for(let i=0;i<v0.gaps.length;i++)if(c(v1.gaps[i],Z)>0)hi=min([hi,d(v0.gaps[i],b(v0.gaps[i],v1.gaps[i]))]);
     if(c(hi,Z)>0)visit(mix(x,x1,hi),mix(y,y1,hi));
    }
   }
   if(c(best[k].value,before)===0)break;
  }
  return {best,visit,stats:()=>({tested,feasible,improved})};
 }
 function geometry(M,depthLimit){
  const D=1n<<BigInt(depthLimit),D2=D*D;
  const vertices=n=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?D:0n));
  const root={X:vertices(M.nr),Y:vertices(M.nc),depth:0};
  let L=1n;
  const gcd=(a,b)=>{while(b){[a,b]=[b,a%b]}return a};
  for(const cell of M.cells)for(const v of cell.gaps)L=L/gcd(L,v[1])*v[1];
  const cells=M.cells.map(cell=>({gap:cell.gaps.map(v=>v[0]*(L/v[1])),out:cell.out.map(v=>v[0])}));
  function split(cell){
   ok(cell.depth<depthLimit,'split depth cap');
   let edge=null;
   for(const side of ['X','Y']){
    const V=cell[side];for(let i=0;i<V.length;i++)for(let j=i+1;j<V.length;j++){
     const size=V[i].reduce((s,v,k)=>s+(v-V[j][k])**2n,0n);
     if(!edge||size>edge.size)edge={side,i,j,size};
    }
   }
   ok(edge&&edge.size>0n,'cannot split point');
   const {side,i,j}=edge,V=cell[side],mid=V[i].map((v,k)=>{ok((v+V[j][k])%2n===0n,'dyadic midpoint');return (v+V[j][k])/2n});
   const child=idx=>({...cell,depth:cell.depth+1,[side]:V.map((v,k)=>k===idx?mid:v)});
   return [child(i),child(j)];
  }
  const cache=new Map();let vertexChecks=0;
  function vertex(x,y){
   const key=x.join(',')+'|'+y.join(',');if(cache.has(key))return cache.get(key);
   const gaps=Array(M.nr+M.nc).fill(0n),out=M.masks.map(()=>0n);
   for(let i=0;i<M.nr;i++)if(x[i])for(let j=0;j<M.nc;j++)if(y[j]){
    const w=x[i]*y[j],cell=cells[i*M.nc+j];
    for(let k=0;k<gaps.length;k++)gaps[k]+=w*cell.gap[k];
    for(let k=0;k<out.length;k++)if(cell.out[k])out[k]+=w;
   }
   const r={gaps,out,feasible:gaps.every(v=>v<=0n)};cache.set(key,r);vertexChecks++;return r;
  }
  function bounds(cell,onFeasible){
   const mins=Array(M.nr+M.nc).fill(null),upper=M.masks.map(()=>0n);
   for(const x of cell.X)for(const y of cell.Y){
    const v=vertex(x,y);
    for(let k=0;k<mins.length;k++)if(mins[k]===null||v.gaps[k]<mins[k])mins[k]=v.gaps[k];
    for(let k=0;k<upper.length;k++)if(v.out[k]>upper[k])upper[k]=v.out[k];
    if(v.feasible&&onFeasible)onFeasible(x.map(w=>f(w,D)),y.map(w=>f(w,D)));
   }
   return {excluded:mins.some(v=>v>0n),upper:upper.map(v=>f(v,D2))};
  }
  return {root,split,bounds,stats:()=>({unique_corner_evaluations:vertexChecks})};
 }
 function verify(g,target,receipt){
  const M=model(g,target),{depthLimit,maxSplits}=receipt.config;
  ok(Number.isSafeInteger(depthLimit)&&depthLimit>=1&&depthLimit<=20&&Number.isSafeInteger(maxSplits)&&maxSplits>=0&&maxSplits<=4096,'cover cap');
  ok(receipt.objectives.length===M.masks.length,'objective count');
  const duals=receipt.objectives.map((r,k)=>{ok(r.mask===M.masks[k],'mask order');return verifyDual(M,k,r.dual)});
  const inner=receipt.objectives.map((r,k)=>{
   const p=r.witness,cert=S.certify(g.R,g.C,p.x,p.y);ok(cert.certified,'witness is not feasible');
   const out=evaluate(M,cert.x.map(q),cert.y.map(q)).out[k];ok(st(out)===r.lower,'witness lower mismatch');return out;
  });
  const G=geometry(M,depthLimit),cover=receipt.cover;ok(typeof cover==='string','cover tree');
  let ptr=0,splits=0,excluded=0,live=0,upper=M.masks.map(()=>Z);
  function walk(cell){
   ok(ptr<cover.length,'truncated cover');const code=cover[ptr++];
   if(code==='s'){ok(++splits<=maxSplits,'split cap');for(const ch of G.split(cell))walk(ch);return}
   const v=G.bounds(cell);
   if(code==='x'){ok(v.excluded,'invalid infeasibility exclusion');excluded++;return}
   ok(code==='l'&&!v.excluded,'invalid leaf');live++;
   for(let k=0;k<upper.length;k++)upper[k]=max([upper[k],v.upper[k]]);
  }
  walk(G.root);ok(ptr===cover.length&&live>0,'invalid cover');
  upper=upper.map((v,k)=>min([v,duals[k]]));
  const objectives=M.masks.map((mask,k)=>{
   ok(c(upper[k],inner[k])>=0,'outer bound below witness');ok(receipt.objectives[k].upper===st(upper[k]),'upper bound mismatch');
   return {mask,lower:st(inner[k]),upper:st(upper[k])};
  });
  const worstLower=max(inner.map((v,k)=>b(v,M.tgt[k]))),worstUpper=max(upper.map((v,k)=>b(v,M.tgt[k])));
  const ranges=M.ends.map((ending,i)=>{
   const k=M.masks.indexOf(1<<i),j=M.masks.indexOf(((1<<M.ends.length)-1)^(1<<i));
   return {ending,min_lower:st(b(O,upper[j])),min_witness:st(b(O,inner[j])),max_witness:st(inner[k]),max_upper:st(upper[k])};
  });
  return {worst_tv:{lower:st(worstLower),upper:st(worstUpper)},ranges,objectives,cover:{splits,excluded,live,...G.stats()}};
 }
 function envelope(g,target,seeds,{maxSplits=256,depthLimit=14,dualSweeps=4,witnessSweeps=4}={}){
  ok(Number.isSafeInteger(maxSplits)&&maxSplits>=0&&maxSplits<=4096&&Number.isSafeInteger(depthLimit)&&depthLimit>=1&&depthLimit<=20&&[dualSweeps,witnessSweeps].every(v=>Number.isSafeInteger(v)&&v>=0&&v<=16),'config cap');
  const M=model(g,target),sol=S.solve(g.R,g.C,{mode:'kite',budget:128,rounds:12});
  const W=witnessSearch(g,M,[sol.certificate,...sol.history,...seeds],witnessSweeps);
  const ds=M.masks.map((_,k)=>dual(M,k,dualSweeps)),du=ds.map((r,k)=>verifyDual(M,k,r));
  const G=geometry(M,depthLimit);
  const seenFeasible=new Set();
  function witness(x,y){const key=show(x).join(',')+'|'+show(y).join(',');if(seenFeasible.has(key))return;seenFeasible.add(key);W.visit(x,y)}
  function node(cell){const v=G.bounds(cell,witness);return {cell,v,children:null}}
  const root=node(G.root),leaves=[root];let splits=0;
  // Heuristic priority affects speed only, never proof validity.
  function priority(n){
   if(n.v.excluded||n.cell.depth>=depthLimit||M.nr+M.nc===2)return 0;
   return Math.max(...n.v.upper.map((v,k)=>num(b(min([v,du[k]]),W.best[k].value))));
  }
  while(splits<maxSplits){
   let idx=-1,score=0;for(let i=0;i<leaves.length;i++){const p=priority(leaves[i]);if(p>score){idx=i;score=p}}
   if(idx<0)break;
   const n=leaves[idx];n.children=G.split(n.cell).map(node);leaves.splice(idx,1,...n.children);splits++;
  }
  const encode=n=>n.children?'s'+n.children.map(encode).join(''):n.v.excluded?'x':'l';
  const cover=encode(root);
  const upper=M.masks.map((_,k)=>min([du[k],max(leaves.filter(n=>!n.v.excluded).map(n=>n.v.upper[k]))]));
  const receipt={config:{maxSplits,depthLimit,dualSweeps,witnessSweeps},cover,objectives:M.masks.map((mask,k)=>({mask,subset:M.ends.filter((_,i)=>mask&(1<<i)),lower:st(W.best[k].value),upper:st(upper[k]),witness:W.best[k].cert,dual:ds[k]})),witness_stats:W.stats(),search_corner_evaluations:G.stats().unique_corner_evaluations};
  receipt.verified=verify(g,target,receipt);
  return receipt;
 }
 return {envelope,verify};
})(S);
export const {envelope,verify}=api;
