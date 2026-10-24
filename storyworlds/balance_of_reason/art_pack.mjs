// Local-only production-art ZIP importer. No remote service is contacted.
// The provided archive is 917 KB and contains seven named WebP images.
// Keep GIF/HTML/script files out; accept only the seven exact paths below.
export const ART_NAMES=["hero","warroom","summit","world","dialogue","ceasefire","characters"];
const NAME_SET=new Set(ART_NAMES.map(name=>"assets/"+name+".webp"));
const DB="balance-of-reason-art-v1",STORE="packs",KEY="selected-art";
const LIMIT=16*1024*1024;
function check(condition,message){if(!condition)throw Error("Art pack: "+message);}
function isWebP(bytes){
  const t=(i)=>String.fromCharCode(...bytes.subarray(i,i+4));
  return bytes.length>=20&&t(0)==="RIFF"&&t(8)==="WEBP";
}
export async function extractArtZip(archive){
  check(archive instanceof Blob,"choose a ZIP archive");
  check(archive.size>30&&archive.size<=LIMIT,"ZIP file must be below 16 MB");
  const bytes=new Uint8Array(await archive.arrayBuffer()),view=new DataView(bytes.buffer);
  const names=new Map(),decoder=new TextDecoder("utf-8",{fatal:true});
  let pos=0;
  while(pos+4<=bytes.length){
    const signature=view.getUint32(pos,true);
    if(signature===0x02014b50||signature===0x06054b50)break;
    check(signature===0x04034b50&&pos+30<=bytes.length,"invalid ZIP entry");
    const flags=view.getUint16(pos+6,true),method=view.getUint16(pos+8,true);
    const compressedSize=view.getUint32(pos+18,true),actualSize=view.getUint32(pos+22,true);
    const nameLength=view.getUint16(pos+26,true),extraLength=view.getUint16(pos+28,true);
    check(!(flags&1)&&!(flags&8),"encrypted or streamed ZIP entries are unsupported");
    check(method===0||method===8,"unsupported ZIP compression");
    check(actualSize<=4*1024*1024,"image exceeds 4 MB");
    const start=pos+30,endName=start+nameLength,startData=endName+extraLength;
    const endData=startData+compressedSize;
    check(endData<=bytes.length,"truncated ZIP entry");
    const name=decoder.decode(bytes.subarray(start,endName));
    if(NAME_SET.has(name)){
      check(!names.has(name),"duplicate artwork file "+name);
      let content;
      if(method===0)content=bytes.slice(startData,endData);
      else{
        check(typeof DecompressionStream==="function","this browser cannot unpack deflated ZIP archives");
        const deflated=new Blob([bytes.slice(startData,endData)]);
        const reader=deflated.stream().pipeThrough(new DecompressionStream("deflate-raw")).getReader();
        const pieces=[];let total=0;
        try{
          while(true){
            const {done,value}=await reader.read();
            if(done)break;
            total+=value.byteLength;
            if(total>4*1024*1024){await reader.cancel();throw Error("Image expansion exceeds 4 MB");}
            pieces.push(value);
          }
        }finally{reader.releaseLock();}
        content=new Uint8Array(total);
        let pointer=0;for(const piece of pieces){content.set(piece,pointer);pointer+=piece.length;}
      }
      check(content.length===actualSize,"corrupt image size "+name);
      check(isWebP(content),"invalid WebP image "+name);
      names.set(name.slice(7,-5),new Blob([content],{type:"image/webp"}));
    }
    pos=endData;
  }
  check(names.size===ART_NAMES.length,"archive needs all seven game images");
  return Object.fromEntries(names);
}
function openDB(){
  return new Promise((resolve,reject)=>{
    if(!("indexedDB" in globalThis)){reject(Error("Browser image storage unavailable"));return;}
    const request=indexedDB.open(DB,1);
    request.onupgradeneeded=()=>{
      if(!request.result.objectStoreNames.contains(STORE))request.result.createObjectStore(STORE);
    };
    request.onsuccess=()=>resolve(request.result);
    request.onerror=()=>reject(request.error||Error("Image storage could not open"));
  });
}
function opDB(mode,operation){
  return openDB().then(db=>new Promise((resolve,reject)=>{
    const transaction=db.transaction(STORE,mode);
    const query=operation(transaction.objectStore(STORE));
    let answer;
    if(query){
      query.onsuccess=()=>answer=query.result;
      query.onerror=()=>reject(query.error||Error("Art storage request failed"));
    }
    transaction.oncomplete=()=>{db.close();resolve(answer)};
    transaction.onerror=()=>{db.close();reject(transaction.error||Error("Art storage failed"))};
    transaction.onabort=()=>{db.close();reject(transaction.error||Error("Art storage aborted"))};
  }));
}
export async function installArtPack(file){
  const art=await extractArtZip(file);
  await opDB("readwrite",store=>store.put(art,KEY));
  return art;
}
export async function readArtPack(){
  return (await opDB("readonly",store=>store.get(KEY)))||null;
}
export async function clearArtPack(){
  await opDB("readwrite",store=>store.delete(KEY));
}
