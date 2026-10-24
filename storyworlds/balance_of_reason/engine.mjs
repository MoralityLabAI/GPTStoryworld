// Pure deterministic engine for Balance of Reason. No dependencies.
export const clamp=(x)=>Math.max(-1,Math.min(1,Math.round(x*100000)/100000));
export function deltas(source) {
  const out={};
  for(const token of source.trim().split(/\s+/)){
    const m=token.match(/^([A-Z])([+-])(\d*\.?\d+)$/);
    if(!m) throw Error("Invalid delta: "+token);
    out[m[1]]=Number(m[3])*(m[2]==="+"?1:-1);
  }
  return out;
}
export const rows=(source)=>source.acts.flatMap(a=>a.events);
export function validateSource(source){
  if(source.acts.length!==8) throw Error("Eight acts required");
  for(const a of source.acts){
    if(a.events.length!==4||a.crisis.length!==6)throw Error("Malformed act "+a.year);
    for(const e of a.events){
      if(e.length!==4||e[3].length!==3)throw Error("Malformed encounter "+e[0]);
      for(const choice of e[3]) { if(choice.length!==3) throw Error("Malformed choice"); deltas(choice[2]); }
    }
  }
  if(source.endings.length<8)throw Error("Too few endings");
  return true;
}
function apply(state,delta,mode=0,success=true){
  const d=deltas(delta),mult=success?1:.66;
  for(const [k,v] of Object.entries(d))state.stats[k]=clamp(state.stats[k]+v*(v<0&&!success?1.26:mult));
  if(!("V" in d))state.stats.V=clamp(state.stats.V+(mode===1?.065:mode===0?.025:.015));
  if(!("Q" in d))state.stats.Q=clamp(state.stats.Q+(mode===1?-.035:mode===0?.055:.005));
  if(!success){state.stats.B=clamp(state.stats.B+.03);state.stats.U=clamp(state.stats.U-.025);}
}
export function initial(source){
  validateSource(source);
  return {yearIndex:0,sceneIndex:0,phase:"event",stats:Object.fromEntries(Object.keys(source.metrics).map(x=>[x,0])),
    history:[],lastOutcome:"",result:null,turns:0};
}
export function current(source,state){
  if(state.phase==="end"){
    const end=source.endings.find(e=>e[0]===state.result);
    return {year:state.yearIndex<8?source.acts[state.yearIndex].year:2042,title:end[1],body:end[5],choices:[]};
  }
  if(state.phase==="final")return {year:2041,title:"The Fifth Article: Final Consultation",
    body:"The delegates have voted. The Party can claim a permanent mandate, yield to an elected rotating council, or preserve the practical accords. Maryam asks what free will means when a superpower speaks it.",
    choices:[
      ["Recognize a rotating council and the right of dissent.","Delegates reserve the right to reject your interpretation.","U+.16 A+.11 L+.12 S-.08 P-.09 M-.09"],
      ["Proclaim the Party's permanent spiritual presidency.","Governments sign selectively; independent scholars walk out.","S+.17 P+.14 V+.12 M+.13 U-.17 A-.10 B+.06"],
      ["Retain humanitarian and trade agreements; suspend the claim.","Practical institutions survive an unsettled theological debate.","T+.14 W+.11 B-.12 P+.04 S-.08 U+.04"]
    ]};
  const act=source.acts[state.yearIndex];
  if(state.phase==="event"){
    const e=act.events[state.sceneIndex];return {year:act.year,title:e[0],body:e[1],stakes:e[2],choices:e[3]};
  }
  const [name,description,stake,obligation,hurt,fallout]=act.crisis;
  if(state.phase==="crisis")return {year:act.year,title:name+" · First Exchange",
    body:description,stakes:"Stake: "+stake+" | Obligation: "+obligation+" | Harm: "+hurt,
    choices:[
      ["Propose public verification and a face-saving compromise.","A narrow settlement survives the first exchange.","U+.10 A+.07 T+.07 B-.13 S-.06 W+.04"],
      ["Issue an ultimatum backed by visible strategic pressure.","The challenge raises prestige and shipping risk.","S+.15 P+.08 B+.20 T-.09 U-.08 M+.03"],
      ["Concede a limited point publicly and preserve the hotline.","The concession costs prestige and contains the crisis.","B-.18 W+.06 A+.05 S-.12 P-.07 T+.06"]
    ]};
  return {year:act.year,title:name+" · Final Warning",
    body:fallout+" The crisis has reached a brinkmanship ladder. A concession can cost prestige; another ultimatum can cross an irreversible threshold.",
    stakes:"The stakes have already increased. Brinkmanship: "+(state.stats.B*100).toFixed(0)+"%",
    choices:[
      ["Accept third-party arbitration and verified records.","The mediator offers an exit.","U+.10 A+.08 B-.20 S-.09 T+.04"],
      ["Raise the alert and repeat the ultimatum.","The public challenge becomes a military command.","S+.15 P+.07 B+.23 T-.12 W-.10 U-.08"],
      ["Withdraw the threat with a reasoned statement.","The hotline stays open and shipping resumes.","B-.23 W+.11 L+.04 S-.16 P-.07 U+.06"]
    ]};
}
function meets(stats,condition){
  return condition.split(/\s+/).every(term=>{
    const m=term.match(/^([A-Z])(>=|<=)(-?\d*\.?\d+)$/);
    if(!m)throw Error("Invalid condition: "+term);
    return m[2]===">="?stats[m[1]]>=+m[3]:stats[m[1]]<=+m[3];
  });
}
export function scoreEndings(source,state){
  return source.endings.map(e=>{
    let score=0;
    for(const term of e[3].split(/\s+/)){
      const [key,weight]=term.split(":");
      score+=(state.stats[key]??0)*Number(weight);
    }
    score+=meets(state.stats,e[2])?e[4]:0;
    return {key:e[0],name:e[1],score:Number(score.toFixed(4)),eligible:meets(state.stats,e[2])};
  }).sort((a,b)=>b.score-a.score);
}
function finish(source,state){
  state.phase="end";
  state.result=state.stats.B>=.78?"global_fire":scoreEndings(source,state)[0].key;
}
function nextYear(source,state){
  state.yearIndex++;
  state.sceneIndex=0;
  if(state.yearIndex===source.acts.length){state.phase="final";state.yearIndex=source.acts.length-1;}
  else state.phase="event";
}
export function choose(source,state,index){
  const scene=current(source,state);
  if(state.phase==="end")throw Error("Game already ended");
  const c=scene.choices[index];if(!c)throw Error("Invalid choice "+index);
  const oldPhase=state.phase,oldIndex=state.sceneIndex,year=scene.year,pre={...state.stats};
  let success=true;
  if(oldPhase==="event"){
    const test=index===0?(oldIndex%2===0?"U":"A"):index===1?"P":"T";
    const threshold=index===0?(-.25+state.yearIndex*.025):index===1?(.035+state.yearIndex*.01):(-.08+state.yearIndex*.018);
    success=pre[test]>=threshold;
  } else if(oldPhase==="crisis"){
    if(index===0) success=pre.U>=(-.21+state.yearIndex*.026);
    if(index===1) success=pre.S>=(.20+state.yearIndex*.023);
  }
  apply(state,c[2],index,success);
  state.turns++;
  let outcome=c[1];
  if(oldPhase==="event"){
    if(!success)outcome="The proposal meets resistance. "+source.acts[state.yearIndex].events[oldIndex][2];
    if(state.sceneIndex<3)state.sceneIndex++;
    else state.phase="crisis";
  } else if(oldPhase==="crisis"){
    if(index===2||success)nextYear(source,state);
    else {state.phase="standoff";outcome+=" The rival issues a new challenge.";}
  } else if(oldPhase==="standoff"){
    if(index===1&&pre.B>=(.62-state.yearIndex*.009)){
      state.stats.B=1;
      state.phase="end";state.result="global_fire";
      outcome="The renewed alert reaches the catastrophic threshold. The map turns black.";
    } else nextYear(source,state);
  } else if(oldPhase==="final")finish(source,state);
  state.lastOutcome=outcome;
  state.history.push({turn:state.turns,year,phase:oldPhase,title:scene.title,choice:c[0],outcome,stats:{...state.stats}});
  return state;
}
export function autoplay(source,chooser,max=70){
  const st=initial(source);
  for(let t=0;t<max&&st.phase!=="end";t++){
    const scene=current(source,st);
    choose(source,st,chooser(scene,st)%scene.choices.length);
  }
  if(st.phase!=="end")throw Error("Incomplete playthrough");
  return st;
}
