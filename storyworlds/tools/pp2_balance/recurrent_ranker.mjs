const api=(function modelFactory(){
 const ok=(x,m)=>{if(!x)throw Error(m)};
 const rng=seed=>{let s=seed>>>0||1;return n=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)%n}};
 const zeros=n=>new Float64Array(n),dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 function layout(dim,h){
  let n=0;const block=(r,c)=>{const o=n;n+=r*c;return {o,r,c}};
  const W=block(h,dim),be=block(h,1),A=block(h,h),B=block(h,h),bz=block(h,1),C=block(h,h),D=block(h,h),by=block(h,1),O=block(2,h),bo=block(2,1);
  return {dim,h,n,W,be,A,B,bz,C,D,by,O,bo};
 }
 function init(dim,h,seed){
  const L=layout(dim,h),random=rng(seed),w=zeros(L.n);
  for(const M of [L.W,L.A,L.B,L.C,L.D,L.O])for(let i=0;i<M.r*M.c;i++)w[M.o+i]=(random(2000001)/1000000-1)*Math.sqrt(1/M.c);
  return {L,w};
 }
 function mv(w,M,v){
  const a=zeros(M.r);for(let i=0;i<M.r;i++)for(let j=0;j<M.c;j++)a[i]+=w[M.o+i*M.c+j]*v[j];return a;
 }
 function forward(model,x,passes,intervention=null){
  const {L,w}=model,{h}=L;
  const e=mv(w,L.W,x);for(let i=0;i<h;i++)e[i]=Math.tanh(e[i]+w[L.be.o+i]);
  let z=e,y=e;const trace=[];
  for(let t=0;t<passes;t++){
   const az=mv(w,L.A,z),by=mv(w,L.B,y),zn=zeros(h);
   for(let i=0;i<h;i++)zn[i]=Math.tanh(az[i]+by[i]+e[i]+w[L.bz.o+i]);
   const cz=mv(w,L.C,zn),dy=mv(w,L.D,y),yn=zeros(h);
   let inj=null;
   if(intervention&&(intervention.pass===t||intervention.pass===-1)){
    const k=intervention.column,delta=intervention.means[t][k]-y[k];
    inj=Array.from({length:h},(_,i)=>w[L.D.o+i*h+k]*delta);
    if(intervention.kind==='null'){
     const norm=Math.sqrt(dot(inj,inj)),random=rng((intervention.seed^((t+1)*7919))>>>0);
     inj=inj.map(()=> (random(2)?1:-1)*norm/Math.sqrt(h));
    }
   }
   for(let i=0;i<h;i++)yn[i]=Math.tanh(cz[i]+dy[i]+e[i]+w[L.by.o+i]+(inj?inj[i]:0));
   const pred=mv(w,L.O,yn);for(let i=0;i<2;i++)pred[i]+=w[L.bo.o+i];
   trace.push({z,y,zn,yn,pred});z=zn;y=yn;
  }
  return {e,trace,pred:trace.at(-1).pred};
 }
 function lossGrad(model,row,passes,grad=true){
  const {L,w}=model,{h}=L,{e,trace}=forward(model,row.x,passes),g=zeros(L.n);
  const back=(M,src,err)=>{const r=zeros(M.c);for(let i=0;i<M.r;i++)for(let j=0;j<M.c;j++){g[M.o+i*M.c+j]+=err[i]*src[j];r[j]+=w[M.o+i*M.c+j]*err[i]}return r};
  const bias=(M,err)=>{for(let i=0;i<M.r;i++)g[M.o+i]+=err[i]};
  let dy=zeros(h),dz=zeros(h),de=zeros(h),loss=0;
  for(let t=passes-1;t>=0;t--){
   const v=trace[t],err=zeros(2);
   for(let j=0;j<2;j++)if(row.y[j]!==null){
    const weight=(j===0?.25:2)/passes,d=v.pred[j]-row.y[j];loss+=weight*d*d/2;err[j]=weight*d;
   }
   if(!grad)continue;
   const dyOut=back(L.O,v.yn,err);bias(L.bo,err);
   const dpreY=zeros(h);for(let i=0;i<h;i++){dpreY[i]=(dy[i]+dyOut[i])*(1-v.yn[i]**2);de[i]+=dpreY[i]}bias(L.by,dpreY);
   const dzOut=back(L.C,v.zn,dpreY),prevY=back(L.D,v.y,dpreY);
   const dpreZ=zeros(h);for(let i=0;i<h;i++){dpreZ[i]=(dz[i]+dzOut[i])*(1-v.zn[i]**2);de[i]+=dpreZ[i]}bias(L.bz,dpreZ);
   const prevZ=back(L.A,v.z,dpreZ),prevY2=back(L.B,v.y,dpreZ);
   for(let i=0;i<h;i++)prevY[i]+=prevY2[i];
   dz=prevZ;dy=prevY;
  }
  if(grad){
   for(let i=0;i<h;i++)de[i]=(de[i]+dz[i]+dy[i])*(1-e[i]**2);
   bias(L.be,de);back(L.W,row.x,de);
  }
  return {loss,g};
 }
 function gradientCheck(){
  const row={x:[.2,-.4,1],y:[1,-.2]},model=init(3,3,716),base=lossGrad(model,row,3);
  let max=0;
  for(let i=0;i<model.w.length;i++){
   const w=model.w[i],eps=1e-5;model.w[i]=w+eps;const a=lossGrad(model,row,3,false).loss;model.w[i]=w-eps;const b=lossGrad(model,row,3,false).loss;model.w[i]=w;
   max=Math.max(max,Math.abs((a-b)/(2*eps)-base.g[i]));
  }
  ok(max<1e-7,'BPTT gradient mismatch: '+max);return {parameters:model.w.length,max_abs_error:max};
 }
 function shuffleLabels(rows,seed){
  const random=rng(seed),out=rows.map(r=>({...r,y:r.y.slice()}));
  for(const root of new Set(out.map(r=>r.root)))for(let k=0;k<8;k++){
   const xs=out.filter(r=>r.root===root&&r.block===k),ys=xs.map(r=>r.y);
   for(let i=ys.length-1;i>0;i--){const j=random(i+1);[ys[i],ys[j]]=[ys[j],ys[i]]}
   xs.forEach((r,i)=>r.y=ys[i]);
  }
  return out;
 }
 function train(rows,{passes=3,seed=41921,epochs=12,h=8,shuffle=false}={}){
  ok(rows.length>0&&[1,3].includes(passes),'training config');
  const data=shuffle?shuffleLabels(rows,19873):rows,model=init(data[0].x.length,h,seed),random=rng(seed^81283),idx=Array.from({length:data.length},(_,i)=>i),losses=[];
  for(let epoch=0;epoch<epochs;epoch++){
   for(let i=idx.length-1;i>0;i--){const j=random(i+1);[idx[i],idx[j]]=[idx[j],idx[i]]}
   let loss=0;const lr=.012/(1+epoch/8);
   for(const i of idx){
    const r=lossGrad(model,data[i],passes);loss+=r.loss;
    const norm=Math.sqrt(dot(r.g,r.g)),scale=Math.min(1,2/Math.max(1e-12,norm));
    for(let j=0;j<model.w.length;j++)model.w[j]-=lr*(scale*r.g[j]+1e-4*model.w[j]);
   }
   losses.push(loss/data.length);
  }
  ok(Array.from(model.w).every(Number.isFinite),'nonfinite weights');
  const means=Array.from({length:passes},()=>Array(h).fill(0)),seconds=Array.from({length:passes},()=>Array(h).fill(0));
  for(const r of rows){const trace=forward(model,r.x,passes).trace;for(let t=0;t<passes;t++)for(let k=0;k<h;k++){means[t][k]+=trace[t].y[k]/rows.length;seconds[t][k]+=trace[t].y[k]**2/rows.length}}
  const strength=Array.from({length:h},(_,k)=>{let n=0;for(let i=0;i<h;i++)n+=model.w[model.L.D.o+i*h+k]**2;return n*means.reduce((s,m,t)=>s+Math.max(0,seconds[t][k]-m[k]**2),0)/passes});
  const column=strength.indexOf(Math.max(...strength));
  return {L:model.L,w:Array.from(model.w),passes,seed,epochs,shuffle,losses,means,column,strength,examples:rows.length,exact_delta_examples:rows.filter(r=>r.y[1]!==null).length};
 }
 function predict(model,x,intervention=null){const p=forward(model,x,model.passes,intervention).pred;return [clamp((p[0]+1)/2,0,1),clamp(p[1],-2,2)]}
 function diagnostics(model,rows){
  const arm=(pass,kind)=>{
   let gate=0,delta=0,n=0,shift=0;
   for(let i=0;i<rows.length;i++){
    const r=rows[i],base=predict(model,r.x),p=kind==='clean'?base:predict(model,r.x,{pass,kind,column:model.column,means:model.means,seed:31981+i*31});
    gate+=Number((p[0]>=.5)===(r.y[0]>0));shift+=Math.abs(p[0]-base[0])+Math.abs(p[1]-base[1]);
    if(r.y[1]!==null){delta+=(p[1]-r.y[1])**2;n++}
   }
   return {pass,kind,gate_accuracy:gate/rows.length,delta_mse:n?delta/n:null,mean_output_shift:shift/rows.length,exact_delta_examples:n};
  };
  return {column:model.column,clean:arm(-1,'clean'),interventions:[...Array.from({length:model.passes},(_,i)=>i),-1].flatMap(t=>[arm(t,'mean'),arm(t,'null')])};
 }
 return {gradientCheck,train,predict,diagnostics};
})();
export const {gradientCheck,train,predict,diagnostics}=api;
