// Policy consequence ledger derived exclusively from the authoritative engine.
const RISK_KEYS=new Set(["B","M","F","G","H"]);
const clampDisplay=value=>Math.round(value*100);
export const METRIC_LABELS={
 U:"Ummah consent",A:"Rationalist credibility",L:"Religious liberty",W:"Civilian welfare",
 P:"Party cohesion",T:"Trade resilience",S:"Strategic prestige",B:"Brinkmanship",
 M:"Mihna coercion",V:"Perceived consent",Q:"Perceived credibility",
 D:"Development equity",F:"Internal fitna",C:"AI command integrity",
 G:"World-war intensity",H:"Displacement"
};

function changes(after,before,descriptors,kind,limit){
  const arr=[];
  for(const [id,value] of Object.entries(after||{})){
    if(!Number.isFinite(value))continue;
    const prior=Number.isFinite(before?.[id])?before[id]:0;
    const delta=value-prior;
    if(Math.abs(delta)<.0005)continue;
    const rounded=clampDisplay(delta);
    const risk=kind==="metric"&&RISK_KEYS.has(id);
    const improvement=(risk?-1:1)*delta>0;
    arr.push({
      id,name:descriptors[id]||id,delta,display:(rounded>0?"+":"")+rounded,
      improvement,kind
    });
  }
  return arr.sort((a,b)=>Math.abs(b.delta)-Math.abs(a.delta)||a.id.localeCompare(b.id)).slice(0,limit);
}

export function latestDecisionImpact(source,game,{national=5,coalitions=4}={}){
  if(!game?.history?.length)return null;
  const current=game.history.at(-1),previous=game.history.at(-2);
  const initialFaction=Object.fromEntries((source?.factions||[]).map(f=>[f.id,f.initial]));
  const factionNames=Object.fromEntries((source?.factions||[]).map(f=>[f.id,f.name]));
  return {
    title:current.title,year:current.year,choice:current.choice,outcome:current.outcome,
    turn:current.turn,
    national:changes(current.stats,previous?.stats||{},METRIC_LABELS,"metric",national),
    coalitions:changes(current.factions,previous?.factions||initialFaction,factionNames,"faction",coalitions)
  };
}
