// Sweepweave compiler for the 2034–2041 Balance of Reason campaign.
// Use source_cards.json for authoring. Native JSON is a reproducible derivative.
// Browser and Sweepweave share authored deltas, reactions, and crisis thresholds.
export function buildSweepweave(source){
  if(source?.acts?.length!==8 || source.acts.some(a=>a.events.length!==7))
    throw Error("Expected eight acts with seven policy scenes each");
  if(source.version!==3||!Array.isArray(source.factions)||source.factions.length!==11)throw Error("Expected eleven autonomous factions in v3 source");
  const stamp=1792800000,metrics=source.metrics;
  const text=(value)=>({pointer_type:"String Constant",script_element_type:"Pointer",value});
  const constant=(value)=>({pointer_type:"Bounded Number Constant",script_element_type:"Pointer",value:Number(value.toFixed(6))});
  const pointer=(key,coefficient=1,character="char_secretary")=>({
    pointer_type:"Bounded Number Pointer",script_element_type:"Pointer",
    character,keyring:[metrics[key]||key],coefficient
  });
  const op=(operator_type,operands)=>({operator_type,script_element_type:"Operator",operands});
  const add=(...parts)=>op("Addition",parts);
  const cmp=(key,operator_subtype,value)=>({operator_type:"Arithmetic Comparator",operator_subtype,
    script_element_type:"Operator",operands:[pointer(key),constant(value)]});
  const nudge=(key,amount,character="char_secretary")=>({
    effect_type:"Bounded Number Effect",Set:pointer(key,1,character),
    to:op("Nudge",[pointer(key,1,character),constant(amount)])
  });
  const decode=(value)=>{
    const result={};
    for(const token of value.trim().split(/\s+/)){
      const m=token.match(/^([A-Z])([+-])(\d*\.?\d+)$/);
      if(!m||!metrics[m[1]])throw Error("Unknown delta "+token);
      result[m[1]]=Number(m[3])*(m[2]==="+"?1:-1);
    }
    return result;
  };
  function effects(delta,choiceIndex,witness,success){
    const d=decode(delta),factor=success?1:.66;
    const result=Object.entries(d).map(([k,value])=>nudge(
      k,value*(value<0&&!success?1.26:factor)
    ));
    if(!Object.hasOwn(d,"V"))result.push(nudge("V",choiceIndex===1?.065:choiceIndex===0?.025:.015));
    if(!Object.hasOwn(d,"Q"))result.push(nudge("Q",choiceIndex===1?-.035:choiceIndex===0?.055:.005));
    if(!success)result.push(nudge("B",.03),nudge("U",-.025));
    const coercion=Math.max(0,d.M||0)+Math.max(0,-(d.L||0));
    if(coercion)result.push(nudge("F",coercion*.4*factor));
    if((d.D||0)>0)result.push(nudge("W",d.D*.15*factor),nudge("H",-d.D*.14*factor));
    if((d.D||0)<0)result.push(nudge("H",-d.D*.35*factor));
    if((d.C||0)<0)result.push(nudge("G",-d.C*.28*factor),nudge("B",-d.C*.15*factor));
    if((d.G||0)>0)result.push(nudge("H",d.G*.3*factor),nudge("W",-d.G*.24*factor));
    if((d.F||0)>0)result.push(nudge("U",-d.F*.2*factor));
    if((d.H||0)>0)result.push(nudge("W",-d.H*.12*factor));
    const effective=Object.fromEntries(Object.entries(d).map(([key,value])=>
      [key,value*(value<0&&!success?1.26:factor)]));
    const factionShifts=source.factions.map(faction=>{
      const amount=Object.entries(faction.weights).reduce(
        (total,[key,weight])=>total+(effective[key]||0)*weight,0)*.22;
      const rounded=Math.max(-1,Math.min(1,Math.round(amount*100000)/100000));
      return {id:faction.id,amount:rounded};
    }).filter(x=>Math.abs(x.amount)>=.003).sort((a,b)=>
      Math.abs(b.amount)-Math.abs(a.amount) || a.id.localeCompare(b.id)).slice(0,4);
    for(const change of factionShifts)result.push(nudge("Coalition_Standing",change.amount,change.id));
    result.push(nudge(choiceIndex===0?"U":choiceIndex===1?"S":"T",success?.04:-.045,witness));
    return result;
  }
  function reaction(id,narrative,target,delta,index,witness,success,test,threshold){
    const condition=cmp(test,success?"Greater Than or Equal To":"Less Than",threshold);
    return {
      id,text_script:text(narrative),consequence_id:target,
      desirability_script:add(
        op("Multiplication",[condition,constant(20)]),
        pointer(test,success?.09:-.09),constant(success?.02:.01)
      ),
      after_effects:effects(delta,index,witness,success)
    };
  }
  function choice(id,label,okText,setbackText,delta,index,witness,okNext,setbackNext,test,threshold){
    return {
      id,text_script:text(label),visibility_script:true,performability_script:true,
      reactions:[
        reaction(id+"_ok",okText,okNext,delta,index,witness,true,test,threshold),
        reaction(id+"_setback",setbackText,setbackNext,delta,index,witness,false,test,threshold)
      ]
    };
  }
  const encounters=[],spools=[];let order=0;
  function encounter(id,title,body,spool,options,acceptability_script=true){
    const index=order++;
    encounters.push({
      id,title,prompt_script:text(body),text_script:text(body),
      connected_spools:[spool],creation_index:index,creation_time:stamp,modified_time:stamp,
      graph_position_x:120*(index%8),graph_position_y:75*Math.floor(index/8),
      earliest_turn:0,latest_turn:999,acceptability_script,
      desirability_script:add(constant(.8),pointer("U",.03),pointer("B",-.03)),options
    });
    return id;
  }
  const isAtWar=op("Or",[
    cmp("G","Greater Than or Equal To",.26),
    cmp("C","Less Than or Equal To",-.24),
    cmp("B","Greater Than or Equal To",.58)
  ]);
  const isAtPeace=op("And",[
    cmp("G","Less Than",.26),
    cmp("C","Greater Than",-.24),
    cmp("B","Less Than",.58)
  ]);
  const catastrophic=op("And",[
    cmp("G","Greater Than or Equal To",.90),
    cmp("C","Less Than or Equal To",-.45),
    cmp("B","Greater Than or Equal To",.78)
  ]);
  const survivable=op("Or",[
    cmp("G","Less Than",.90),
    cmp("C","Greater Than",-.45),
    cmp("B","Less Than",.78)
  ]);
  function gatewayChoice(id,label,open,closed,openCondition,closedCondition){
    const stay=[nudge("G",0),nudge("C",0),nudge("B",0)];
    return {id,text_script:text(label),visibility_script:true,performability_script:true,reactions:[
      {id:id+"_trigger",text_script:text("The verification ledger determines which chapter follows."),
        consequence_id:open,desirability_script:add(
          op("Multiplication",[openCondition,constant(20)]),constant(.02)),
        after_effects:stay},
      {id:id+"_hold",text_script:text("The independent ledger reports that the escalation threshold has not been crossed."),
        consequence_id:closed,desirability_script:add(
          op("Multiplication",[closedCondition,constant(20)]),constant(.01)),
        after_effects:stay}
    ]};
  }
  const nextYear=(i)=>source.acts[i+1]?"page_"+source.acts[i+1].year+"_01":"page_final_council";
  for(let ai=0;ai<source.acts.length;ai++){
    const act=source.acts[ai],spool="spool_"+act.year,ids=[];
    const next=nextYear(ai);
    const postCrisis=act.conflict?"page_"+act.year+"_war_check":next;
    for(let j=0;j<act.events.length;j++){
      const [title,body,fallout,choices]=act.events[j];
      const id="page_"+act.year+"_0"+(j+1);
      const successor=j+1===act.events.length?"page_"+act.year+"_countermove":"page_"+act.year+"_0"+(j+2);
      const options=choices.map(([label,outcome,delta],index)=>{
        const test=index===0?(j===4?"D":j===5?"U":j===6?"C":j%2===0?"U":"A"):index===1?"P":"T";
        const threshold=index===0?(-.25+ai*.025):index===1?(.035+ai*.01):(-.08+ai*.018);
        return choice(id+"_opt_"+(index+1),label,
          outcome+" The communiqué preserves the obligation and its cost.",
          "The policy meets resistance. "+fallout,
          delta,index,act.witness,successor,successor,test,threshold);
      });
      ids.push(encounter(id,title,body,spool,options));
    }
    const council=act.countermove;
    if(!council || !source.factions.some(x=>x.id===council.faction))throw Error("Unknown annual countermove "+act.year);
    const councilId="page_"+act.year+"_countermove";
    const coalitionPtr=pointer("Coalition_Standing",1,council.faction);
    const factionGate=(good)=>({
      operator_type:"Arithmetic Comparator",script_element_type:"Operator",
      operator_subtype:good?"Greater Than or Equal To":"Less Than",
      operands:[coalitionPtr,constant(council.threshold)]
    });
    const factionOptions=council.options.map(([label,proposal,delta],index)=>({
      id:councilId+"_opt_"+(index+1),text_script:text(label),visibility_script:true,
      performability_script:true,
      reactions:[true,false].map(good=>({
        id:councilId+"_opt_"+(index+1)+(good?"_cooperate":"_resist"),
        text_script:text((good?council.cooperative:council.hostile)+" "+proposal),
        consequence_id:"page_"+act.year+"_crisis",
        desirability_script:add(
          op("Multiplication",[factionGate(good),constant(20)]),
          pointer("Coalition_Standing",good?.08:-.08,council.faction),
          constant(good?.02:.01)
        ),
        after_effects:[
          ...effects(good?council.allyEffect:council.defectEffect,index,council.faction,good),
          ...effects(delta,index,council.faction,good)
        ]
      }))
    }));
    ids.push(encounter(councilId,council.title,council.body+"\n\nThe delegation has sealed its position. Its response to the next decision depends on the trust accumulated since the opening congress.",spool,factionOptions));
    const [name,description,stake,obligation,hurt,fallout]=act.crisis;
    const crisis="page_"+act.year+"_crisis",standoff="page_"+act.year+"_standoff";
    ids.push(encounter(crisis,name+": First Exchange",
      description+"\n\nStake: "+stake+" | Obligation: "+obligation+" | Expected harm: "+hurt,spool,[
      choice(crisis+"_compromise","Offer independent verification and a face-saving settlement.",
        "The proposal opens monitored talks.","The mediation proposal fails and a second demand arrives.",
        "U+.10 A+.07 T+.07 B-.13 S-.06 W+.04 D+.03",0,act.witness,postCrisis,standoff,"U",-.21+ai*.026),
      choice(crisis+"_warning","Issue a strategic ultimatum supported by visible pressure.",
        "The rival backs down as a heightened alert spreads.","The challenge triggers another ultimatum.",
        "S+.15 P+.08 B+.20 T-.09 U-.08 M+.03 G+.08",1,act.witness,postCrisis,standoff,"S",.20+ai*.023),
      choice(crisis+"_retreat","Concede a limited point and preserve the diplomatic hotline.",
        "The concession costs prestige and protects future negotiations.",
        "Domestic critics gain ground while shipping remains open.",
        "B-.18 W+.06 A+.05 S-.12 P-.07 T+.06 G-.05",2,act.witness,postCrisis,postCrisis,"T",-.14+ai*.015)
    ]));
    ids.push(encounter(standoff,name+": Final Warning",fallout+
      "\n\nAnother ultimatum could turn disputed information into irreversible military action. The crisis now has a meaningful cost for retreat and a potentially catastrophic cost for escalation.",
      spool,[
      choice(standoff+"_arbitrate","Accept third-party arbitration and verified evidence.",
        "The mediator secures an exit for both governments.",
        "The partial settlement preserves the hotline.",
        "U+.10 A+.08 B-.20 S-.09 T+.04 G-.07",0,act.witness,postCrisis,postCrisis,"A",-.16+ai*.026),
      choice(standoff+"_raise","Raise the security alert and repeat the demand.",
        "Strategic automation repeats the order without verified human authorization.",
        "The other navy withdraws; the next crisis inherits a higher alert posture.",
        "S+.15 P+.07 B+.23 T-.12 W-.10 U-.08 G+.16 C-.08",1,act.witness,"page_end_global_fire",postCrisis,"B",.62-ai*.009),
      choice(standoff+"_withdraw","Withdraw the threat with a reasoned statement.",
        "Humanitarian monitors and shipping resume.",
        "The government loses prestige and avoids a wider war.",
        "B-.23 W+.11 L+.04 S-.16 P-.07 U+.06 G-.08",2,act.witness,postCrisis,postCrisis,"U",-.22+ai*.022)
    ]));
    // The irreversible brinkmanship ending sets the same maximum risk that
    // the browser records when a final ultimatum triggers catastrophe.
    const fatalStandoff=encounters[encounters.length-1].options[1].reactions[0];
    if(fatalStandoff.consequence_id!=="page_end_global_fire")throw Error("Unexpected standoff routing");
    fatalStandoff.after_effects.push({
      effect_type:"Bounded Number Effect",Set:pointer("B"),to:constant(1)
    });
    if(act.conflict){
      const warCheck="page_"+act.year+"_war_check";
      const war="page_"+act.year+"_world_war",peace="page_"+act.year+"_fragile_peace";
      const warEnd="page_"+act.year+"_war_outcome";
      const gateOptions=[
        gatewayChoice(warCheck+"_public","Publish the international monitors' incident ledger.",war,peace,isAtWar,isAtPeace),
        gatewayChoice(warCheck+"_cabinet","Read the cabinet's classified war assessment.",war,peace,isAtWar,isAtPeace)
      ];
      ids.push(encounter(warCheck,"The Model War Threshold",
        "The Chinese cabinet compares foreign naval orders, autonomous AI alerts and verified civilian losses. The next chapter depends on accumulated world-war intensity, command integrity and brinkmanship. The reports are already in the archive.",
        spool,gateOptions));
      for(const kind of ["war","peace"]){
        const [title,body,stakes,choices]=act.conflict[kind];
        const id=kind==="war"?war:peace;
        const options=choices.map(([label,goodResult,delta],index)=>{
          const test=index===0?"C":index===1?(kind==="war"?"P":"S"):"D";
          const threshold=index===0?(kind==="war"?-.2:-.16):index===1?(kind==="war"?.12:0):(kind==="war"?-.15:-.14);
          return choice(id+"_opt_"+(index+1),label,
            goodResult,"The proposal encounters resistance. "+stakes,
            delta,index,act.witness,kind==="war"?warEnd:next,kind==="war"?warEnd:next,test,threshold);
        });
        ids.push(encounter(id,title,body+"\n\n"+stakes,spool,options,kind==="war"?isAtWar:isAtPeace));
      }
      ids.push(encounter(warEnd,"The Postwar Authorization Check",
        "Investigators compare surviving human authorization records to the strategic alerts. A single uncontrolled exchange may destroy every remaining negotiation.",
        spool,[
          gatewayChoice(warEnd+"_joint","Submit the warning record to independent civilian investigators.",
            "page_end_global_fire",next,catastrophic,survivable),
          gatewayChoice(warEnd+"_cabinet","Ask the cabinet to verify the command chain.",
            "page_end_global_fire",next,catastrophic,survivable)
        ]));
    }
    spools.push({id:spool,spool_type:"General",spool_name:"Act "+(ai+1)+" · "+act.name,
      creation_index:ai,creation_time:stamp,modified_time:stamp,
      starts_active:ai===0,encounters:ids});
  }
  const final="page_final_council",endingGate="page_ending_gate";
  encounter(final,"The Fifth Article: Final Consultation",
      "Istanbul, 2041. The World War of the Models has rewritten the summit agenda. Governments count obligations, jurists count freedoms, and displaced delegates count empty homes. Beijing must decide what leadership means.",
      "spool_final",[
        choice(final+"_equal","Recognize a rotating council with independent scholarly votes.",
          "Independent delegates may reject Chinese doctrine.",
          "Delegates demand stronger protections for their freedom.",
          "U+.16 A+.11 L+.12 S-.08 P-.09 M-.09 F-.09",0,"char_yusuf",endingGate,endingGate,"U",-.2),
        choice(final+"_mandate","Declare the Party's permanent presidency.",
          "Governments sign while scholars organize independent councils.",
          "The final signatures include reservations.",
          "S+.17 P+.14 V+.12 M+.13 U-.17 A-.10 B+.06 F+.10",1,"char_guo",endingGate,endingGate,"P",.05),
        choice(final+"_accords","Keep practical aid agreements and defer leadership.",
          "The development banks continue their work.",
          "The theological claim remains unresolved.",
          "T+.14 W+.11 B-.12 P+.04 S-.08 U+.04 D+.09 H-.05",2,"char_chen",endingGate,endingGate,"T",-.12)
      ]);
  const conds=(textCondition)=>{
    if(!textCondition || !textCondition.trim())return [];
    return textCondition.trim().split(/\s+/).map(term=>{
      const match=term.match(/^([A-Z])(>=|<=)(-?\d*\.?\d+)$/);
      if(!match)throw Error("Invalid ending condition "+term);
      return [match[1],match[2],Number(match[3])];
    });
  };
  const condition=(key,opName,value)=>cmp(key,opName===">="?"Greater Than or Equal To":"Less Than or Equal To",value);
  const opposite=(key,opName,value)=>cmp(key,opName===">="?"Less Than":"Greater Than",value);
  function scoreEnding(ending){
    const [key,title,gate,weights,bonus]=ending;
    const terms=[constant(.05)];
    for(const token of weights.trim().split(/\s+/)){
      const [key,value]=token.split(":");
      terms.push(pointer(key,Number(value)));
    }
    const gates=conds(gate);
    if(gates.length){
      const matches=op("And",gates.map(([key,sign,value])=>condition(key,sign,value)));
      const fails=op("Or",gates.map(([key,sign,value])=>opposite(key,sign,value)));
      terms.push(op("Multiplication",[matches,constant(bonus)]));
      terms.push(op("Multiplication",[fails,constant(-1000)]));
    }else terms.push(constant(bonus));
    return add(...terms);
  }
  const endingOptions=[1,2].map(ballot=>({
    id:endingGate+"_opt_"+ballot,
    text_script:text(ballot===1?"Publish the independent delegates' ballots.":"Publish the cabinet's parallel ledger."),
    visibility_script:true,performability_script:true,
    reactions:source.endings.map(ending=>({
      id:endingGate+"_vote_"+ballot+"_r_"+ending[0],
      text_script:text("Every promise and contested obligation enters the public archive."),
      consequence_id:"page_end_"+ending[0],
      desirability_script:scoreEnding(ending),
      after_effects:[nudge("G",0),nudge("C",0),nudge("F",0)]
    }))
  }));
  encounter(endingGate,"The Scales of the Fifth Article",
    "The assembly counts power, consent, AI authorization, internal fitna and development. The same history produces different claims; the final outcome must satisfy its stated conditions.",
    "spool_final",endingOptions);
  spools.push({id:"spool_final",spool_type:"General",spool_name:"The Final Consultation",
    creation_index:8,creation_time:stamp,modified_time:stamp,starts_active:false,
    encounters:[final,endingGate]});
  const endingIds=[];
  for(const [key,title,gate,weights,bonus,body] of source.endings){
    const id="page_end_"+key,cs=conds(gate).map(([k,sign,v])=>condition(k,sign,v));
    encounter(id,title,body,"spool_endings",[],cs.length?op("And",cs):true);
    endingIds.push(id);
  }
  spools.push({id:"spool_endings",spool_type:"General",spool_name:"Endings · The World After Reason",
    creation_index:9,creation_time:stamp,modified_time:stamp,starts_active:false,encounters:endingIds});
  const initialValues={
    char_scholar:{A:.55,L:.4,U:.2,M:-.6},char_nurjan:{L:.5,U:-.4,A:.1,M:-.5},
    char_chen:{T:.5,P:.4},char_guo:{S:.45,P:.4,B:.3},
    char_yusuf:{U:.35,L:.4,A:.25},char_fardad:{S:.45,B:.3,U:-.1},
    char_amal:{T:.55,B:-.25},char_samira:{W:.5,U:.15},char_ward:{B:-.2,T:.3}
  };
  const factionInitial=Object.fromEntries(source.factions.map(f=>[f.id,f.initial]));
  const characters=source.cast.map(([id,name,pronoun])=>({
    id,name,pronoun,bnumber_properties:{
      ...Object.fromEntries(Object.entries(metrics).map(([k,value])=>[value,initialValues[id]?.[k]??0])),
      Coalition_Standing:factionInitial[id]??0
    }
  }));
  const authored_properties=[...Object.values(metrics),"Coalition_Standing"].map((property_name,i)=>({
    id:property_name,property_name,property_type:"bounded number",
    default_value:0,depth:0,attribution_target:"all cast members",affected_characters:[],
    creation_index:i,creation_time:stamp,modified_time:stamp
  }));
  return {
    IFID:"SW-BALANCE-OF-REASON-RED-MIHNA-2034-V3",
    title:source.title,storyworld_title:source.title,storyworld_author:"MoralityLabAI / GPTStoryworld",
    sweepweave_version:"0.1.9",creation_time:stamp,modified_time:stamp,debug_mode:false,
    display_mode:1,css_theme:"lilac",font_size:"16",language:"en",rating:"mature",
    about_text:text("Alternate history 2034–2041. The converted Chinese Communist Party claims to lead the Ummah as international development, internal fitnas and an AI-driven world war test the meaning of reason and divine justice."),
    characters,authored_properties,spools,encounters
  };
}

export function validateSweepweave(world){
  const errors=[];
  const req=["IFID","about_text","css_theme","debug_mode","display_mode",
    "creation_time","modified_time","characters","authored_properties","spools","encounters"];
  for(const key of req)if(!(key in world))errors.push("missing "+key);
  const ids=new Set(world.encounters.map(e=>e.id));
  if(ids.size!==world.encounters.length)errors.push("duplicate encounter IDs");
  if(!world.spools.some(s=>s.starts_active))errors.push("no starting spool");
  for(const s of world.spools){
    if(!s.encounters.length)errors.push("empty spool "+s.id);
    for(const id of s.encounters)if(!ids.has(id))errors.push("unknown spool target "+id);
  }
  for(const e of world.encounters){
    if(!e.id.startsWith("page_end_")&&e.options.length<2)errors.push("inert encounter "+e.id);
    for(const o of e.options){
      if(o.reactions.length<2)errors.push("missing reactions "+o.id);
      for(const r of o.reactions){
        if(!ids.has(r.consequence_id))errors.push("dangling consequence "+r.id);
        if(r.after_effects.length<3)errors.push("missing bounded effects "+r.id);
      }
    }
  }
  return errors;
}

// Rebuild: node storyworlds/balance_of_reason/build_sweepweave.mjs
import {readFileSync,writeFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join,resolve} from "node:path";
const moduleFile=fileURLToPath(import.meta.url),folder=dirname(moduleFile);
if(process.argv[1] && resolve(process.argv[1])===moduleFile){
  const source=JSON.parse(readFileSync(join(folder,"source_cards.json"),"utf8"));
  const world=buildSweepweave(source),errors=validateSweepweave(world);
  if(errors.length)throw Error(errors.join("; "));
  const file=join(folder,"storyworld.json");
  writeFileSync(file,JSON.stringify(world),"utf8");
  console.log("Wrote "+file+" · "+world.encounters.length+" encounters");
}
