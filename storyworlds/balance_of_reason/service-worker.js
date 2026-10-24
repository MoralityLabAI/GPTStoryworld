/* Balance of Reason offline playtest.
   Scope is the hosting directory: GitHub Pages /GPTStoryworld/ or a local
   storyworlds/balance_of_reason/ server. No cross-site fetch interception. */
const CACHE='bor-playtest-20261024-visual-v4';
const CORE=[
 './','./index.html','./engine.mjs','./trace_protocol.mjs','./share_route.mjs',
 './visuals.mjs','./visuals.css','./build_sweepweave.mjs',
 './source_cards.json','./assets/crest.svg','./assets/hero.svg',
 './assets/warroom.svg','./assets/summit.svg','./assets/world.svg',
 './manifest.webmanifest'
];
const home=new URL('./index.html',self.registration.scope).href;
self.addEventListener('install',event=>{
 event.waitUntil((async()=>{
   const cache=await caches.open(CACHE);
   await cache.addAll(CORE.map(p=>new URL(p,self.registration.scope).href));
   await self.skipWaiting();
 })());
});
self.addEventListener('activate',event=>{
 event.waitUntil((async()=>{
   const keys=await caches.keys();
   await Promise.all(keys.filter(k=>k.startsWith('bor-playtest-')&&k!==CACHE)
      .map(k=>caches.delete(k)));
   await self.clients.claim();
 })());
});
self.addEventListener('fetch',event=>{
 const request=event.request;
 if(request.method!=='GET')return;
 const url=new URL(request.url),scope=new URL(self.registration.scope);
 if(url.origin!==scope.origin||!url.pathname.startsWith(scope.pathname))return;
 if(request.mode==='navigate'){
   event.respondWith((async()=>{
     try{
       const response=await fetch(request);
       if(response.ok)await (await caches.open(CACHE)).put(home,response.clone());
       return response;
     }catch{
       const cached=await caches.match(home);
       if(cached)return cached;
       return Response.error();
     }
   })());return;
 }
 event.respondWith((async()=>{
   const cached=await caches.match(request,{ignoreSearch:true});
   if(cached)return cached;
   try{
     const response=await fetch(request);
     if(response.ok && response.type==='basic'){
       const cache=await caches.open(CACHE);
       await cache.put(request,response.clone());
     }
     return response;
   }catch{return Response.error();}
 })());
});
