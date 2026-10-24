import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {buildStoryworld} from './sweepweave_builder.mjs';
const dir=dirname(fileURLToPath(import.meta.url));
const input=join(dir,'source_cards.json');
const output=join(dir,'storyworld.json');
const built=JSON.stringify(buildStoryworld(JSON.parse(readFileSync(input,'utf8'))));
if(process.argv.includes('--check')){
  const actual=readFileSync(output,'utf8').trimEnd();
  if(actual!==built){console.error('Sweepweave export drift: re-run node export_sweepweave.mjs');process.exit(1);}
  console.log('Sweepweave export reproducible: '+built.length+' bytes');
}else{
  writeFileSync(output,built,'utf8');
  console.log('Wrote '+output+' ('+built.length+' bytes)');
}
