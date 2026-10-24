
export function buildSweepweave(source) {
  if(!source?.acts || source.acts.length!==8) throw Error("Expected eight annual acts");
  const stamp=1792800000, metrics=source.metrics;
  const str=(value)=>({pointer_type:"String Constant",script_element_type:"Pointer",value});
  const number=(value)=>({pointer_type:"Bounded Number Constant",script_element_type:"Pointer",value:Number(value.toFixed(5))});
  const pointer=(key,coefficient=1,character="char_secretary")=>({pointer_type:"Bounded Number Pointer",script_element_type:"Pointer",character,keyring:[metrics[key]||key],coefficient});
  const op=(operator_type,operands)=>({operator_type,script_element_type:"Operator",operands});
  const add=(...parts)=>op("Addition",parts);
  const cmp=(key,subtype,value)=>({operator_type:"Arithmetic Comparator",operator_subtype:subtype,script_element_type:"Operator",operands:[pointer(key),number(value)]});
  const delta=(s)=>Object.fromEntries(s.trim().split(/\s+/).map(t=>{
    const m=t.match(/^([A-Z])([+-])(\d*\.?\d+)$/);
    if(!m || !metrics[m[1]]) throw Error("Bad delta: "+t);
    return [m[1],Number(m[3])*(m[2]==="+"?1:-1)];
  }));
  const effect=(key,value,character="char_secretary")=>({effect_type:"Bounded Number Effect",Set:pointer(key,1,character),to:op("Nudge",[pointer(key,1,character),number(value)])});
  const fx=(d,i,witness,good)=>{
    const changes=delta(d),factor=good?1:.66;
    const all=Object.entries(changes).map(([k,v])=>effect(k,Math.max(-.3,Math.min(.3,v*(v<0&&!good?1.26:factor)))));
    if(!Object.hasOwn(changes,"V"))all.push(effect("V",i===1?.065:i===0?.025:.015));
    if(!Object.hasOwn(changes,"Q"))all.push(effect("Q",i===1?-.035:i===0?.055:.005));
    if(!good){all.push(effect("B",.03));all.push(effect("U",-.025));}
    all.push(effect(i===0?"U":i===1?"S":"T",good?.04:-.045,witness));
    return all;
  };
  const reaction=(id,text,next,d,i,witness,good,test,limit)=>({
    id,text_script:str(text),consequence_id:next,
    desirability_script:add(op("Multiplication",[cmp(test,good?"Greater Than or Equal To":"Less Than",limit),number(20)]),pointer(test,good?.09:-.09),number(good?.02:.01)),
    after_effects:fx(d,i,witness,good)
  });
  const choice=(id,label,goodText,badText,d,i,witness,win,loss,test,threshold)=>({
    id,text_script:str(label),visibility_script:true,performability_script:true,
    reactions:[
      reaction(id+"_success",goodText,win,d,i,witness,true,test,threshold),
      reaction(id+"_setback",badText,loss,d,i,witness,false,test,threshold)
    ]
  });
  const encounter=(id,title,body,spool,idx,options,acceptability_script=true)=>({
    id,title,prompt_script:str(body),text_script:str(body),connected_spools:[spool],
    creation_index:idx,creation_time:stamp,modified_time:stamp,
    graph_position_x:(idx%8)*130,graph_position_y:Math.floor(idx/8)*80,
    earliest_turn:0,latest_turn:999,acceptability_script,
    desirability_script:add(number(.75),pointer("U",.05),pointer("B",-.05)),options
  });
  let ix=0;const spools=[],encounters=[];
  for(let ai=0;ai<source.acts.length;ai++){
    const act=source.acts[ai],spool="spool_"+act.year,ids=[];
    const next=source.acts[ai+1]?"page_"+source.acts[ai+1].year+"_01":"page_final_council";
    for(let j=0;j<4;j++){
      const [title,body,fallout,options]=act.events[j];
      const id="page_"+act.year+"_0"+(j+1),after=j===3?"page_"+act.year+"_crisis":"page_"+act.year+"_0"+(j+2);
      const opts=options.map(([label,outcome,d],i)=>{
        const test=i===0?(j%2===0?"U":"A"):i===1?"P":"T";
        const limit=i===0?(-.25+ai*.025):i===1?(.035+ai*.01):(-.08+ai*.018);
        return choice(id+"_opt_"+(i+1),label,outcome+" The communiqué records the choice and its cost.",
          "The proposal meets resistance. "+fallout,d,i,act.witness,after,after,test,limit);
      });
      encounters.push(encounter(id,title,body,spool,ix++,opts));ids.push(id);
    }
    const [name,description,stake,obligation,harm,fallout]=act.crisis;
    const first="page_"+act.year+"_crisis",stand="page_"+act.year+"_standoff";
    const normal=[
      choice(first+"_compromise","Offer monitored talks and publish mutually verifiable evidence.",
        "A narrow settlement survives the first exchange.","The monitoring agreement stalls. "+fallout,
        "U+.10 A+.07 T+.07 B-.13 S-.06 W+.04",0,act.witness,next,stand,"U",-.21+ai*.026),
      choice(first+"_warning","Issue a public ultimatum supported by strategic pressure.",
        "The other side backs down while insurers remain anxious.","A new confrontation follows. "+fallout,
        "S+.15 P+.08 B+.20 T-.09 U-.08 M+.03",1,act.witness,next,stand,"S",.20+ai*.023),
      choice(first+"_exit","Concede a limited point while preserving the hotline.",
        "A reasoned concession ends the dispute.","The concession angers the press and leaves the hotline open.",
        "B-.18 W+.06 A+.05 S-.12 P-.07 T+.06",2,act.witness,next,next,"T",-.14+ai*.015)
    ];
    encounters.push(encounter(first,name+": First Exchange",
      description+"\n\nCRISIS LEDGER. Stake: "+stake+". Obligation: "+obligation+". Expected harm: "+harm,spool,ix++,normal));ids.push(first);
    const risk=choice(stand+"_alert","Raise the alert and repeat the ultimatum.",
      "A warning propagates into action before the diplomats can respond.",
      "The other navy yields and the next year's crisis inherits a higher risk level.",
      "S+.15 P+.07 B+.23 T-.12 W-.10 U-.08",1,act.witness,"page_end_global_fire",next,"B",.62-ai*.009);
    const standoff=[
      choice(stand+"_arbitrate","Accept third-party arbitration with an evidence-sharing protocol.",
        "Mediation offers both governments a route home.","The agreement remains incomplete, but the confrontation ends.",
        "U+.10 A+.08 B-.20 S-.09 T+.04",0,act.witness,next,next,"A",-.16+ai*.026),
      risk,
      choice(stand+"_recede","Withdraw the ultimatum and explain the decision publicly.",
        "The concession prevents the next escalation.","Shipping resumes despite domestic criticism.",
        "B-.23 W+.11 L+.04 S-.16 P-.07 U+.06",2,act.witness,next,next,"U",-.22+ai*.022)
    ];
    encounters.push(encounter(stand,name+": Final Warning",fallout+
      "\n\nThe diplomatic crisis has reached its last rung. Withdrawal costs prestige; escalation can destroy the entire system.",
      spool,ix++,standoff));ids.push(stand);
    spools.push({id:spool,spool_type:"General",spool_name:"Act "+(ai+1)+" · "+act.name,
      starts_active:ai===0,creation_index:ai,creation_time:stamp,modified_time:stamp,encounters:ids});
  }
  const final="page_final_council";
  const finalOptions=[
    choice(final+"_equals","Recognize a rotating council with independent scholars.",
      "Independent delegates accept open rules.","The autonomy clause passes amid demands for stronger guarantees.",
      "U+.16 A+.11 L+.12 S-.08 P-.09 M-.09",0,"char_yusuf","page_ending_gate","page_ending_gate","U",-.20),
    choice(final+"_mandate","Declare Beijing's permanent spiritual presidency.",
      "State delegates sign while independent scholars walk out.","The signatures are ambiguous and a rival congress forms.",
      "S+.17 P+.14 V+.12 M+.13 U-.17 A-.10 B+.06",1,"char_guo","page_ending_gate","page_ending_gate","P",.05),
    choice(final+"_accords","Keep practical humanitarian accords and postpone leadership claims.",
      "Practical institutions endure an unfinished debate.","The compromise preserves trade while leaving grand questions unresolved.",
      "T+.14 W+.11 B-.12 P+.04 S-.08 U+.04",2,"char_chen","page_ending_gate","page_ending_gate","T",-.12)
  ];
  encounters.push(encounter(final,"The Fifth Article: Final Consultation",
    "Istanbul, 2041. The vote is tied. No delegation is obliged to accept the titles you claim. A naval hotline remains open outside the city. Maryam asks what free will means when spoken by a superpower.",
    "spool_final",ix++,finalOptions));
  const conditionTokens=(condition)=>condition?condition.trim().split(/\s+/).map(term=>{
      const m=term.match(/^([A-Z])(>=|<=)(-?\d*\.?\d+)$/);
      if(!m)throw Error("Invalid ending condition "+term);
      return [m[1],m[2],Number(m[3])];
    }):[];
  const score=(end,ballot)=>{
    const [id,title,conditions,weights,bonus]=end;
    const terms=[number(.05)];
    for(const t of weights.trim().split(/\s+/)){
      const [k,w]=t.split(":");terms.push(pointer(k,Number(w)));
    }
    const gates=conditionTokens(conditions);
    if(gates.length){
      const all=op("And",gates.map(([k,sign,v])=>cmp(k,sign===">="?"Greater Than or Equal To":"Less Than or Equal To",v)));
      const fails=op("Or",gates.map(([k,sign,v])=>cmp(k,sign===">="?"Less Than":"Greater Than",v)));
      // Ineligible endings must rank below the fallback no matter how high their weighted score.
      terms.push(op("Multiplication",[all,number(bonus)]));
      terms.push(op("Multiplication",[fails,number(-1000)]));
    }else terms.push(number(bonus));
    if(ballot===1&&["fifth_article","council_of_equals","free_cities"].includes(id))terms.push(pointer("L",.45));
    if(ballot===2&&["paper_caliphate","red_mihna","mandarin_crescent"].includes(id))terms.push(pointer("S",.4));
    return add(...terms);
  };
  const finalGateOptions=[1,2].map(ballot=>({
    id:"page_ending_gate_opt_"+ballot,
    text_script:str(ballot===1?"Read the independent delegates' ballots in public.":"Publish the cabinet and state-delegation tally."),
    visibility_script:true,performability_script:true,reactions:source.endings.map(end=>({
      id:"page_ending_gate_"+ballot+"_r_"+end[0],
      text_script:str("The final record enters the public archive."),
      consequence_id:"page_end_"+end[0],desirability_script:score(end,ballot),
      // Terminal choice records the vote without changing the state that was just adjudicated.
      after_effects:[effect("U",0),effect("S",0),effect("A",0)]
    }))
  }));
  encounters.push(encounter("page_ending_gate","The Scales of the Fifth Article",
    "Independent delegates and Party officials publish competing accounts of legitimate leadership. The tally is reconciled using your actions across eight years. Choose which ledger to read in public.",
    "spool_final",ix++,finalGateOptions));
  spools.push({id:"spool_final",spool_type:"General",spool_name:"The Final Consultation",
    starts_active:false,creation_index:8,creation_time:stamp,modified_time:stamp,
    encounters:["page_final_council","page_ending_gate"]});
  const endIds=[];
  for(const e of source.endings){
    const id="page_end_"+e[0];
    const gates=conditionTokens(e[2]).map(([k,sign,v])=>cmp(k,sign===">="?"Greater Than or Equal To":"Less Than or Equal To",v));
    encounters.push(encounter(id,e[1],e[5],"spool_endings",ix++,[],gates.length?op("And",gates):true));
    endIds.push(id);
  }
  spools.push({id:"spool_endings",spool_type:"General",spool_name:"Endings · What the World Remembers",
    starts_active:false,creation_index:9,creation_time:stamp,modified_time:stamp,encounters:endIds});
  const characters=source.cast.map(([id,name,pronoun])=>({id,name,pronoun,
    bnumber_properties:Object.fromEntries(Object.values(metrics).map(key=>[key,0]))}));
  const authored_properties=Object.values(metrics).map((name,i)=>({
    id:name,property_name:name,property_type:"bounded number",default_value:0,
    depth:0,attribution_target:"all cast members",affected_characters:[],
    creation_index:i,creation_time:stamp,modified_time:stamp
  }));
  return {
    IFID:"SW-BALANCE-OF-REASON-RED-MIHNA-2034",title:source.title,
    storyworld_title:source.title,storyworld_author:"MoralityLabAI / GPTStoryworld",
    sweepweave_version:"0.1.9",creation_time:stamp,modified_time:stamp,
    debug_mode:false,display_mode:1,css_theme:"lilac",font_size:"16",language:"en",rating:"mature",
    about_text:str("Alternate history, 2034–2041. A converted Chinese Communist Party adopts Muʿtazilī doctrine and seeks leadership of the Ummah. Eight years of diplomacy, theological dissent, civil rights, humanitarian relief and nuclear-era brinkmanship determine its fate."),
    characters,authored_properties,spools,encounters
  };
}
export function validateSweepweave(data){
  const errors=[];
  for(const key of ["IFID","about_text","css_theme","debug_mode","display_mode","creation_time","modified_time","characters","authored_properties","spools","encounters"])if(!(key in data))errors.push("missing "+key);
  const ids=new Set(data.encounters.map(e=>e.id));
  if(ids.size!==data.encounters.length)errors.push("duplicate encounter IDs");
  if(!data.spools.some(s=>s.starts_active))errors.push("no active starting spool");
  for(const s of data.spools){if(!s.encounters.length)errors.push("empty spool: "+s.id);for(const eid of s.encounters)if(!ids.has(eid))errors.push("bad spool target "+eid);}
  for(const e of data.encounters){
    if(!e.id.startsWith("page_end_")&&e.options.length<2)errors.push("few options "+e.id);
    for(const o of e.options){
      if(o.reactions.length<2)errors.push("few reactions "+o.id);
      for(const r of o.reactions){
        if(!ids.has(r.consequence_id))errors.push("bad consequence "+r.consequence_id);
        if(r.after_effects.length<3)errors.push("few state effects "+r.id);
      }
    }
  }
  return errors;
}


// Run from repo root: node storyworlds/balance_of_reason/build_sweepweave.mjs
import {readFileSync,writeFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join,resolve} from "node:path";
const moduleFile=fileURLToPath(import.meta.url),folder=dirname(moduleFile);
if(process.argv[1] && resolve(process.argv[1])===moduleFile){
  const src=JSON.parse(readFileSync(join(folder,"source_cards.json"),"utf8"));
  const storyworld=buildSweepweave(src),errors=validateSweepweave(storyworld);
  if(errors.length)throw Error(errors.join("; "));
  const out=join(folder,"storyworld.json");
  writeFileSync(out,JSON.stringify(storyworld,null,2)+"\n","utf8");
  console.log("Wrote "+out+" · "+storyworld.encounters.length+" encounters; "+storyworld.spools.length+" spools.");
}
