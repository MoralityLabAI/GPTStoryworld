// Balance of Reason: Red Mihna. Deterministic browser rules, no dependencies.
// All geopolitical and theological weights are authored fiction, never empirical forecasts.
export const clamp=(value)=>Math.max(-1,Math.min(1,Math.round(value*100000)/100000));

export function deltas(source){
  const result={};
  for(const token of source.trim().split(/\s+/)){
    const match=token.match(/^([A-Z])([+-])(\d*\.?\d+)$/);
    if(!match)throw Error("Invalid policy delta "+token);
    result[match[1]]=Number(match[3])*(match[2]==="+"?1:-1);
  }
  return result;
}

export function validateSource(source){
  if(source.version!==3)throw Error("Expected faction-based v3 scenario");
  if(!Array.isArray(source.factions)||source.factions.length!==11)throw Error("Expected eleven institutional factions");
  const actorIds=new Set(source.cast.map(actor=>actor[0]));
  for(const faction of source.factions){
    if(!actorIds.has(faction.id)||Object.keys(faction.weights).some(k=>!source.metrics[k]))throw Error("Bad faction "+faction.id);
    if(typeof faction.initial!=="number"||Math.abs(faction.initial)>1)throw Error("Invalid faction standing "+faction.id);
  }
  if(!source || !source.metrics || source.acts?.length!==8)throw Error("Expected eight annual acts");
  if(!Array.isArray(source.cast)||source.cast.length<5)throw Error("Missing character cast");
  for(const key of ["U","A","L","W","P","T","S","B","M","V","Q","D","F","C","G","H"]){
    if(!source.metrics[key])throw Error("Missing metric "+key);
  }
  for(const act of source.acts){
    if(act.events?.length!==7 || act.crisis?.length!==6)throw Error("Malformed annual act "+act.year);
    const counter=act.countermove;
    if(!counter || !actorIds.has(counter.faction) || counter.options?.length!==3
       || !Array.isArray(counter.options) || counter.options.some(o=>o.length!==3))
      throw Error("Malformed faction countermove "+act.year);
    for(const delta of [counter.allyEffect,counter.defectEffect,...counter.options.map(o=>o[2])]){
      for(const key of Object.keys(deltas(delta)))if(!source.metrics[key])throw Error("Invalid countermove delta "+key);
    }
    for(const event of act.events){
      if(event.length!==4 || event[3].length!==3)throw Error("Malformed encounter "+event[0]);
      for(const choice of event[3]){
        if(choice.length!==3)throw Error("Malformed choice "+event[0]);
        for(const key of Object.keys(deltas(choice[2])))if(!source.metrics[key])throw Error("Unknown metric "+key);
      }
    }
    if(act.year>=2038){
      if(!act.conflict || !["war","peace"].every(k=>act.conflict[k]?.length===4))throw Error("Missing conflict fork "+act.year);
      for(const kind of ["war","peace"]){
        if(act.conflict[kind][3].length!==3)throw Error("Malformed conflict choices");
        for(const choice of act.conflict[kind][3])deltas(choice[2]);
      }
    }
  }
  if(source.endings?.length!==15)throw Error("Expected fifteen distinct endings");
  const endingIds=new Set(source.endings.map(x=>x[0]));
  if(endingIds.size!==15 || !endingIds.has("unsettled_mandate"))throw Error("Missing unique fallback ending");
  return true;
}

export function initial(source){
  validateSource(source);
  return {yearIndex:0,sceneIndex:0,phase:"event",
    stats:Object.fromEntries(Object.keys(source.metrics).map(k=>[k,0])),
    factions:Object.fromEntries(source.factions.map(f=>[f.id,f.initial])),
    history:[],lastOutcome:"",result:null,turns:0,warEpisodes:0,peaceEpisodes:0};
}

export function worldWarActive(state){
  return state.stats.G>=.26 || state.stats.C<=-.24 || state.stats.B>=.58;
}

export function current(source,state){
  if(state.phase==="end"){
    const ending=source.endings.find(x=>x[0]===state.result);
    return {year:2042,title:ending[1],body:ending[5],choices:[]};
  }
  if(state.phase==="final"){
    return {year:2041,title:"The Fifth Article: The Final Assembly",
      body:"The World War of the Models has rewritten the summit's agenda. Governments count military obligations, independent jurists count the rights of dissenters, and refugee delegates count the graves. Whether the fighting has ended or not, Beijing must decide what leadership means. An appeal to reason cannot cast a ballot in someone else's name.",
      stakes:"Final mandate. Every previous promise, fitna, development project and AI command failure remains in the ledger.",
      choices:[
        ["Recognize a rotating council of independent scholars and delegate voting.","The delegates gain the right to refuse a Chinese mandate.","U+.16 A+.11 L+.12 S-.08 P-.09 M-.09 F-.09"],
        ["Declare the Party's permanent political and religious presidency.","State representatives endorse the title as scholarly assemblies withdraw.","S+.17 P+.14 V+.12 M+.13 U-.17 A-.10 B+.06 F+.10"],
        ["Save the humanitarian and economic compacts while deferring leadership.","The development institutions survive an unresolved theological claim.","T+.14 W+.11 B-.12 P+.04 S-.08 U+.04 D+.09 H-.05"]
      ]};
  }
  const act=source.acts[state.yearIndex];
  if(state.phase==="countermove"){
    const counter=act.countermove;
    const standing=state.factions[counter.faction]??0;
    const support=standing>=counter.threshold;
    return {year:act.year,title:counter.title,
      body:counter.body+"\n\n"+(support?counter.cooperative:counter.hostile),
      stakes:(support?"INSTITUTIONAL COOPERATION":"INSTITUTIONAL RESISTANCE")
         +" · "+source.factions.find(f=>f.id===counter.faction).name
         +" standing "+Math.round(standing*100)+" · threshold "+Math.round(counter.threshold*100),
      choices:counter.options};
  }
  if(state.phase==="event"){
    const event=act.events[state.sceneIndex];
    return {year:act.year,title:event[0],body:event[1],stakes:event[2],choices:event[3]};
  }
  if(state.phase==="war" || state.phase==="peace"){
    const scene=act.conflict[state.phase];
    const status=state.phase==="war"?"ACTIVE WORLD WAR":"FRAGILE PEACE";
    return {year:act.year,title:scene[0],body:scene[1],
      stakes:status+" · War intensity "+Math.round(state.stats.G*100)+" · AI command integrity "+Math.round(state.stats.C*100)+". "+scene[2],
      choices:scene[3]};
  }
  const [name,description,stake,obligation,hurt,fallout]=act.crisis;
  if(state.phase==="crisis"){
    return {year:act.year,title:name+" · First Exchange",body:description,
      stakes:"Stake: "+stake+" | Obligation: "+obligation+" | Harm: "+hurt,
      choices:[
        ["Offer independent verification and a face-saving settlement.","The proposal opens monitored talks.","U+.10 A+.07 T+.07 B-.13 S-.06 W+.04 D+.03"],
        ["Issue a strategic ultimatum supported by visible pressure.","The ultimatum sharpens the crisis across foreign capitals.","S+.15 P+.08 B+.20 T-.09 U-.08 M+.03 G+.08"],
        ["Concede a limited point publicly and preserve the hotline.","The concession costs prestige and protects future negotiations.","B-.18 W+.06 A+.05 S-.12 P-.07 T+.06 G-.05"]
      ]};
  }
  return {year:act.year,title:name+" · Final Warning",
    body:fallout+" Another ultimatum can turn disputed information into an irreversible military order. Backing down preserves lives while it costs political prestige.",
    stakes:"BRINKMANSHIP LADDER · Risk "+Math.round(state.stats.B*100)+" · War intensity "+Math.round(state.stats.G*100),
    choices:[
      ["Accept third-party arbitration and share verified records.","An independent mediator offers both sides an exit.","U+.10 A+.08 B-.20 S-.09 T+.04 G-.07"],
      ["Raise the security alert and repeat the demand.","The warning may propagate into action faster than commanders can review it.","S+.15 P+.07 B+.23 T-.12 W-.10 U-.08 G+.16 C-.08"],
      ["Withdraw the threat with a reasoned statement.","The hotline remains open and civilian shipping resumes.","B-.23 W+.11 L+.04 S-.16 P-.07 U+.06 G-.08"]
    ]};
}

export function factionShifts(source,delta,success){
  const changes=deltas(delta),factor=success?1:.66;
  const effective=Object.fromEntries(Object.entries(changes).map(([key,value])=>
    [key,value*(value<0&&!success?1.26:factor)]));
  return source.factions.map(faction=>{
    const amount=Object.entries(faction.weights).reduce(
      (total,[key,weight])=>total+(effective[key]||0)*weight,0)*.22;
    return {id:faction.id,amount:clamp(amount)};
  }).filter(x=>Math.abs(x.amount)>=.003).sort((a,b)=>
    Math.abs(b.amount)-Math.abs(a.amount) || a.id.localeCompare(b.id)).slice(0,4);
}

function apply(state,delta,index,success,source){
  const d=deltas(delta),factor=success?1:.66;
  for(const [key,value] of Object.entries(d)){
    const scaled=value*(value<0&&!success?1.26:factor);
    state.stats[key]=clamp(state.stats[key]+scaled);
  }
  if(!Object.hasOwn(d,"V"))state.stats.V=clamp(state.stats.V+(index===1?.065:index===0?.025:.015));
  if(!Object.hasOwn(d,"Q"))state.stats.Q=clamp(state.stats.Q+(index===1?-.035:index===0?.055:.005));
  if(!success){
    state.stats.B=clamp(state.stats.B+.03);
    state.stats.U=clamp(state.stats.U-.025);
  }
  const coercion=Math.max(0,d.M||0)+Math.max(0,-(d.L||0));
  if(coercion>0)state.stats.F=clamp(state.stats.F+coercion*.4*factor);
  if((d.D||0)>0){
    state.stats.W=clamp(state.stats.W+d.D*.15*factor);
    state.stats.H=clamp(state.stats.H-d.D*.14*factor);
  }
  if((d.D||0)<0)state.stats.H=clamp(state.stats.H-d.D*.35*factor);
  if((d.C||0)<0){
    state.stats.G=clamp(state.stats.G-d.C*.28*factor);
    state.stats.B=clamp(state.stats.B-d.C*.15*factor);
  }
  if((d.G||0)>0){
    state.stats.H=clamp(state.stats.H+d.G*.3*factor);
    state.stats.W=clamp(state.stats.W-d.G*.24*factor);
  }
  if((d.F||0)>0)state.stats.U=clamp(state.stats.U-d.F*.2*factor);
  if((d.H||0)>0)state.stats.W=clamp(state.stats.W-d.H*.12*factor);
  for(const shift of factionShifts(source,delta,success)){
    state.factions[shift.id]=clamp((state.factions[shift.id]??0)+shift.amount);
  }
}

function advanceYear(source,state){
  state.yearIndex++;
  state.sceneIndex=0;
  if(state.yearIndex===source.acts.length){
    state.phase="final";state.yearIndex=source.acts.length-1;
  }else state.phase="event";
}
function completeAnnualCrisis(source,state){
  const act=source.acts[state.yearIndex];
  if(act.conflict){
    state.phase=worldWarActive(state)?"war":"peace";
  }else advanceYear(source,state);
}
function meets(stats,condition){
  if(!condition || !condition.trim())return true;
  return condition.trim().split(/\s+/).every(term=>{
    const m=term.match(/^([A-Z])(>=|<=)(-?\d*\.?\d+)$/);
    if(!m)throw Error("Invalid ending gate "+term);
    return m[2]===">="?stats[m[1]]>=Number(m[3]):stats[m[1]]<=Number(m[3]);
  });
}
export function scoreEndings(source,state){
  return source.endings.map(ending=>{
    let score=0;
    for(const token of ending[3].trim().split(/\s+/)){
      const [key,coef]=token.split(":");
      score+=(state.stats[key]??0)*Number(coef);
    }
    const eligible=meets(state.stats,ending[2]);
    score=eligible?score+Number(ending[4]):-1000000000;
    return {key:ending[0],name:ending[1],score:Number(score.toFixed(5)),eligible};
  }).sort((a,b)=>b.score-a.score);
}
function finish(source,state){
  state.phase="end";
  const strategicCollapse=state.stats.G>=.88&&state.stats.C<=-.40&&state.stats.B>=.78;
  state.result=strategicCollapse?"global_fire":scoreEndings(source,state)[0].key;
}

export function choose(source,state,index){
  if(state.phase==="end")throw Error("Campaign already ended");
  const scene=current(source,state);
  const choice=scene.choices[index];
  if(!choice)throw Error("Invalid policy choice "+index);
  const previousPhase=state.phase,previousIndex=state.sceneIndex;
  const pre={...state.stats},preFaction={...state.factions};let success=true;
  if(previousPhase==="event"){
    const prior=previousIndex;
    const test=index===0?(prior===4?"D":prior===5?"U":prior===6?"C":(prior%2===0?"U":"A")):index===1?"P":"T";
    const threshold=index===0?(-.25+state.yearIndex*.025):index===1?(.035+state.yearIndex*.01):(-.08+state.yearIndex*.018);
    success=pre[test]>=threshold;
  }else if(previousPhase==="crisis"){
    if(index===0)success=pre.U>=(-.21+state.yearIndex*.026);
    if(index===1)success=pre.S>=(.20+state.yearIndex*.023);
    if(index===2)success=pre.T>=(-.14+state.yearIndex*.015);
  }else if(previousPhase==="standoff"){
    if(index===0)success=pre.A>=(-.16+state.yearIndex*.026);
    if(index===1)success=pre.B>=(.62-state.yearIndex*.009);
    if(index===2)success=pre.U>=(-.22+state.yearIndex*.022);
  }else if(previousPhase==="final"){
    if(index===0)success=pre.U>=-.2;
    if(index===1)success=pre.P>=.05;
    if(index===2)success=pre.T>=-.12;
  }else if(previousPhase==="war"){
    if(index===0)success=pre.C>=-.2;
    if(index===1)success=pre.P>=.12;
    if(index===2)success=pre.D>=-.15;
  }else if(previousPhase==="peace"){
    if(index===0)success=pre.C>=-.16;
    if(index===1)success=pre.S>=0;
    if(index===2)success=pre.D>=-.14;
  }
  if(previousPhase==="countermove"){
    const counter=source.acts[state.yearIndex].countermove;
    success=(preFaction[counter.faction]??0)>=counter.threshold;
    apply(state,success?counter.allyEffect:counter.defectEffect,index,success,source);
  }
  apply(state,choice[2],index,success,source);
  state.turns++;
  let outcome=choice[1];
  if(previousPhase==="countermove"){
    const actor=source.acts[state.yearIndex].countermove;
    outcome=(success?actor.cooperative:actor.hostile)+" "+outcome;
  }
  if(!success){
    if(previousPhase==="event")outcome="The policy meets resistance. "+source.acts[state.yearIndex].events[previousIndex][2];
    if(previousPhase==="war")outcome+=" Military and civilian institutions contest the implementation.";
    if(previousPhase==="peace")outcome+=" The provisional agreement meets resistance.";
  }
  if(previousPhase==="event"){
    if(state.sceneIndex+1<source.acts[state.yearIndex].events.length)state.sceneIndex++;
    else state.phase="countermove";
  }else if(previousPhase==="countermove"){
    state.phase="crisis";
  }else if(previousPhase==="crisis"){
    if(index===2||success)completeAnnualCrisis(source,state);
    else {state.phase="standoff";outcome+=" A second demand arrives.";}
  }else if(previousPhase==="standoff"){
    const fatal=index===1&&pre.B>=(.62-state.yearIndex*.009);
    if(fatal){state.stats.B=1;state.phase="end";state.result="global_fire";outcome="Strategic automation repeats the order without a verified human authorization. The map turns black.";}
    else completeAnnualCrisis(source,state);
  }else if(previousPhase==="war"||previousPhase==="peace"){
    if(previousPhase==="war")state.warEpisodes++;
    else state.peaceEpisodes++;
    const fatal=state.stats.G>=.9&&state.stats.C<=-.45&&state.stats.B>=.78;
    if(fatal){state.phase="end";state.result="global_fire";outcome="A machine-authorized strategic exchange outruns every ceasefire channel.";}
    else advanceYear(source,state);
  }else if(previousPhase==="final")finish(source,state);
  state.lastOutcome=outcome;
  state.history.push({turn:state.turns,year:scene.year,phase:previousPhase,title:scene.title,
    choice:choice[0],outcome,stats:{...state.stats},factions:{...state.factions}});
  return state;
}

export function autoplay(source,chooser,max=95){
  const state=initial(source);
  for(let t=0;t<max&&state.phase!=="end";t++){
    const scene=current(source,state);
    const index=chooser(scene,state);
    choose(source,state,((index%scene.choices.length)+scene.choices.length)%scene.choices.length);
  }
  if(state.phase!=="end")throw Error("Incomplete playthrough after "+max+" choices");
  return state;
}
