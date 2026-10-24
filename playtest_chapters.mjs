// The preview chapters are legitimate deterministic histories, not patched states.
// Generated with a fixed v3 source and checked at every replay.
import {decodeCampaign} from './share_route.mjs';
import {current} from './engine.mjs';

export const PLAYTEST_CHAPTERS=Object.freeze([
  {
    id:"false-ceasefire",
    year:2038,
    title:"The False Ceasefire",
    subtitle:"An AI mistake threatens the diplomatic order",
    description:"An established reconstruction and diplomatic program approaches a fabricated ceasefire. Test the choice between proof, restraint, and automated retaliation.",
    token:"bor1.a3e68c1b.17.aClopIIgEoYAIQQ.62aec0cf"
  },
  {
    id:"three-fitnas",
    year:2040,
    title:"The Three Fitnas",
    subtitle:"The Party, jurists, and provincial councils split",
    description:"Examine a fragile constitutional settlement where local autonomy and rival doctrines challenge Beijing's religious claims.",
    token:"bor1.a3e68c1b.1r.WJKFkmhRWhkiVqoUgIGKK.bf508b86"
  },
  {
    id:"machine-ultimatum",
    year:2041,
    title:"The Last Machine Ultimatum",
    subtitle:"World-war command authority reaches its final test",
    description:"A wartime cabinet faces a machine-issued ultimatum based on a stale digital credential. Determine whether human authorization can reclaim the process.",
    token:"bor1.a3e68c1b.23.aClopIIgEoYAIQWWEIlAVVCIG.741ababf"
  }
]);

export function loadPlaytestChapter(source,id){
  const chapter=PLAYTEST_CHAPTERS.find(x=>x.id===id);
  if(!chapter)throw Error("Unknown playtest chapter: "+id);
  const game=decodeCampaign(source,chapter.token);
  const scene=current(source,game);
  if(scene.year!==chapter.year||scene.title!==chapter.title||game.phase!=="event")
    throw Error("Chapter preview no longer matches this source revision");
  return game;
}
