import test from 'node:test';
import assert from 'node:assert/strict';
import {deflateRawSync} from 'node:zlib';
import {extractArtZip,ART_NAMES} from './art_pack.mjs';

const pixel=Buffer.from('UklGRjAAAABXRUJQVlA4ICQAAABQAQCdASoBAAEAAoBCJQBOgCgAAP7qZf1rlatKtwbJFLsAAAA=','base64');
function zipEntry(name,data,{method=8,actualSize=data.length}={}){
  const path=Buffer.from(name,'utf8');
  const zipped=method===8?deflateRawSync(data):data;
  const header=Buffer.alloc(30);
  header.writeUInt32LE(0x04034b50,0);
  header.writeUInt16LE(20,4);
  header.writeUInt16LE(0,6);
  header.writeUInt16LE(method,8);
  header.writeUInt32LE(zipped.length,18);
  header.writeUInt32LE(actualSize,22);
  header.writeUInt16LE(path.length,26);
  return Buffer.concat([header,path,zipped]);
}
function testPack(method=8){
  return new Blob([Buffer.concat([
    ...ART_NAMES.map(x=>zipEntry('assets/'+x+'.webp',pixel,{method})),
    zipEntry('INSTALL.txt',Buffer.from('Install locally.'))
  ])]);
}

test('production ZIP entries contain seven valid WebPs, in order, with deflate',async()=>{
 const result=await extractArtZip(testPack());
 assert.deepEqual(Object.keys(result),ART_NAMES);
 for(const name of ART_NAMES){
  assert.equal(result[name].type,'image/webp');
  assert.deepEqual(Buffer.from(await result[name].arrayBuffer()),pixel);
 }
});
test('uncompressed ZIP method works for all seven assets',async()=>{
 const result=await extractArtZip(testPack(0));
 assert.equal(Object.keys(result).length,7);
});
test('invalid, duplicate, truncated, oversized and unsupported images are rejected',async()=>{
 await assert.rejects(()=>extractArtZip(new Blob([Buffer.alloc(64,33)])),/invalid ZIP/);
 const missing=new Blob([Buffer.concat([zipEntry('assets/hero.webp',pixel)])]);
 await assert.rejects(()=>extractArtZip(missing),/needs all seven/);
 const duplicate=new Blob([Buffer.concat([zipEntry('assets/hero.webp',pixel),zipEntry('assets/hero.webp',pixel)])]);
 await assert.rejects(()=>extractArtZip(duplicate),/duplicate artwork/);
 const invalidWebP=new Blob([Buffer.concat(ART_NAMES.map(name=>zipEntry('assets/'+name+'.webp',Buffer.from('not a webp'))))]);
 await assert.rejects(()=>extractArtZip(invalidWebP),/invalid WebP/);
 const oversized=new Blob([Buffer.concat(ART_NAMES.map(name=>zipEntry('assets/'+name+'.webp',pixel,{actualSize:4*1024*1024+1})))]);
 await assert.rejects(()=>extractArtZip(oversized),/exceeds 4 MB/);
 const truncated=Buffer.concat([zipEntry('assets/hero.webp',pixel)]).subarray(0,45);
 await assert.rejects(()=>extractArtZip(new Blob([truncated])),/truncated ZIP entry/);
 await assert.rejects(()=>extractArtZip(new Blob([Buffer.alloc(17*1024*1024)])),/below 16 MB/);
});
