// Build a Sweepweave / Storytron storyworld from the authored source cards.
// The browser edition and this export intentionally share decisions, stakes, and outcomes.
export function buildStoryworld(source){
  const P=source.metrics,ts=1792800000,sc=v=>({pointer_type:"String Constant",script_element_type:"Pointer",value:v});
  const num=v=>({pointer_type:"Bounded Number Constant",script_element_type:"Pointer",value:Number(v.toFixed(5))});
  const ptr=(k,c=1,who="char_secretary")=>({pointer_type:"Bounded Number Pointer",script_element_type:"Pointer",character:who,keyring:[P[k]||k],coefficient:c});
  const op=(operator_type,operands)=>({operator_type,script_element_type:"Operator",operands});
  const sum=(...xs)=>op("Addition",xs);
  const cmp=(k,type,v)=>({operator_type:"Arithmetic Comparator",operator_subtype:type,script_element_type:"Operator",operands:[ptr(k),num(v)]});
  const nudge=(k,delta,who="char_secretary")=>({effect_type:"Bounded Number Effect",Set:ptr(k,1,who),to:op("Nudge",[ptr(k,1,who),num(delta)])});
  function parseDelta(s){const d={};for(const token of s.trim().split(/\s+/)){
    const m=token.match(/^([A-Z])([+-])(\d*\.?\d+)$/);
    if(!m||!P[m[1]])throw Error("Invalid delta "+token);d[m[1]]=Number(m[3])*(m[2]==="+"?1:-1);
  }return d;}
  function effects(deltas,i,witness,good){
    const d=parseDelta(deltas),a=[];
    for(const [k,v] of Object.entries(d)){const x=v*(v<0&&!good?1.26:good?1:.66);a.push(nudge(k,Math.max(-.3,Math.min(.3,x))));}
    if(!("V" in d))a.push(nudge("V",i===1?.065:i===0?.025:.015));
    if(!("Q" in d))a.push(nudge("Q",i===1?-.035:i===0?.055:.005));
    if(!good){a.push(nudge("B",.03));a.push(nudge("U",-.025));}
    a.push(nudge(i===0?"U":i===1?"S":"T",good?.04:-.045,witness));
    return a;
  }
  function reaction(id,text,target,deltas,i,witness,good,test,limit){
    return {id,text_script:sc(text),consequence_id:target,
      desirability_script:sum(op("Multiplication",[cmp(test,good?"Greater Than or Equal To":"Less Than",limit),num(20)]),ptr(test,good?.09:-.09)),
      after_effects:effects(deltas,i,witness,good)};
  }
  function choice(id,label,positive,negative,deltas,i,witness,goodTarget,badTarget,test,limit){
    return {id,text_script:sc(label),visibility_script:true,performability_script:true,reactions:[
      reaction(id+"_r_ok",positive,goodTarget,deltas,i,witness,true,test,limit),
      reaction(id+"_r_resist",negative,badTarget,deltas,i,witness,false,test,limit)
    ]};
  }
  const encounters=[],spools=[];let ix=0;
  function encounter(id,title,body,spool,options,acceptability_script=true){
    const e={id,title,connected_spools:[spool],creation_index:ix++,earliest_turn:0,latest_turn:999,
      text_script:sc(body),acceptability_script,desirability_script:sum(num(.8),ptr("U",.03),ptr("B",-.03)),options};
    encounters.push(e);return id;
  }
  const nextYear=yi=>source.acts[yi+1]?"page_"+source.acts[yi+1].year+"_01":"page_final_council";
  for(let yi=0;yi<source.acts.length;yi++){
    const Y=source.acts[yi],sp="spool_"+Y.year,ids=[],next=nextYear(yi);
    for(let j=0;j<4;j++){
      const [title,body,fallout,actions]=Y.events[j],id="page_"+Y.year+"_0"+(j+1),target=j===3?"page_"+Y.year+"_crisis":"page_"+Y.year+"_0"+(j+2);
      const options=actions.map(([label,outcome,delta],i)=>{
        const test=i===0?(j%2===0?"U":"A"):i===1?"P":"T";
        const limit=i===0?(-.25+yi*.025):i===1?(.035+yi*.01):(-.08+yi*.018);
        return choice(id+"_opt_"+i,label,outcome+" The communique records a promise and its cost.",
          "The policy meets resistance. "+fallout,delta,i,Y.witness,target,target,test,limit);
      });
      ids.push(encounter(id,title,body,sp,options));
    }
    const [name,description,stake,obligation,hurt,fallout]=Y.crisis,id1="page_"+Y.year+"_crisis",id2="page_"+Y.year+"_standoff";
    const crisis=[
      choice(id1+"_compromise","Offer verified negotiations and a face-saving compromise.","A settlement survives the first exchange.","The mediation proposal fails, requiring another exchange.",
        "U+.10 A+.07 T+.07 B-.13 S-.06 W+.04",0,Y.witness,next,id2,"U",-.21+yi*.026),
      choice(id1+"_warning","Challenge the rival publicly with strategic pressure.","The other party backs down, but insurance markets remain wary.","The challenge provokes an ultimatum.",
        "S+.15 P+.08 B+.20 T-.09 U-.08 M+.03",1,Y.witness,next,id2,"S",.20+yi*.023),
      choice(id1+"_exit","Concede a limited point publicly and preserve the hotline.","The dispute is contained at a prestige cost.","Domestic criticism rises, and the crisis still closes.",
        "B-.18 W+.06 A+.05 S-.12 P-.07 T+.06",2,Y.witness,next,next,"T",-.14+yi*.015)
    ];
    ids.push(encounter(id1,name+": First Exchange",description+"\n\nCRISIS LEDGER · "+stake+". Obligation: "+obligation+" Anticipated harm: "+hurt,sp,crisis));
    const standoff=[
      choice(id2+"_mediate","Accept third-party arbitration.","An independent mediator offers an honorable exit.","A partial settlement keeps the dialogue alive.",
        "U+.10 A+.08 B-.20 S-.09 T+.04",0,Y.witness,next,next,"A",-.16+yi*.026),
      choice(id2+"_alert","Raise the security alert and refuse the final demand.","The alert crosses the catastrophic threshold; there will be no further negotiation.","The rival pulls back while the higher alert level persists.",
        "S+.15 P+.07 B+.23 T-.12 W-.10 U-.08",1,Y.witness,"page_end_global_fire",next,"B",.62-yi*.009),
      choice(id2+"_recede","Withdraw the threat with a public explanation.","Humanitarian monitors arrive and shipping resumes.","The cabinet loses prestige but averts a wider confrontation.",
        "B-.23 W+.11 L+.04 S-.16 P-.07 U+.06",2,Y.witness,next,next,"U",-.22+yi*.022)
    ];
    ids.push(encounter(id2,name+": Final Warning",fallout+" An escalating crisis can end in withdrawal, arbitration or catastrophe.",sp,standoff));
    spools.push({id:sp,spool_type:"General",spool_name:"Act "+(yi+1)+" · "+Y.name,creation_index:yi,starts_active:yi===0,encounters:ids});
  }
  const finalChoices=[
    choice("page_final_council_equal","Recognize the rotating council and conscience rights.","Delegates reserve the right to contest Chinese doctrine.","The delegates seek binding guarantees.",
      "U+.16 A+.11 L+.12 S-.08 P-.09 M-.09",0,"char_yusuf","page_ending_gate","page_ending_gate","U",-.20),
    choice("page_final_council_supreme","Declare a permanent Chinese presidency.","State signatures arrive; independent councils organize elsewhere.","The final signatures contain important reservations.",
      "S+.17 P+.14 V+.12 M+.13 U-.17 A-.10 B+.06",1,"char_guo","page_ending_gate","page_ending_gate","P",.05),
    choice("page_final_council_practical","Preserve trade and humanitarian agreements while deferring leadership.","The practical accords survive the constitutional disagreement.","The grand claim is unresolved.",
      "T+.14 W+.11 B-.12 P+.04 S-.08 U+.04",2,"char_chen","page_ending_gate","page_ending_gate","T",-.12)
  ];
  encounter("page_final_council","The Fifth Article","Istanbul, 2041. The vote is tied. No delegation is bound to accept the titles you claim, and a naval hotline is still open. Maryam asks what free will means when a superpower speaks it.","spool_final",finalChoices);
  function conditions(text){return text.split(/\s+/).map(x=>{const m=x.match(/^([A-Z])(>=|<=)(-?\d*\.?\d+)$/);if(!m)throw Error("Invalid ending condition "+x);return cmp(m[1],m[2]===">="?"Greater Than or Equal To":"Less Than or Equal To",+m[3]);});}
  function weights(text){return text.split(/\s+/).map(x=>{const m=x.match(/^([A-Z]):(-?\d*\.?\d+)$/);if(!m)throw Error("Invalid weight "+x);return ptr(m[1],+m[2]);});}
  const finalOptions=[1,2].map(v=>({id:"page_ending_gate_opt_"+v,text_script:sc(v===1?"Publish the independent delegate ballots.":"Publish the cabinet's account of the mandate."),
    visibility_script:true,performability_script:true,reactions:source.endings.map(([key,title,cond,coeff,bonus])=>({
      id:"page_gate_"+v+"_"+key,text_script:sc("The final council publishes its eight-year record."),consequence_id:"page_end_"+key,
      desirability_script:sum(...weights(coeff),op("Multiplication",[op("And",conditions(cond)),num(bonus)]),v===1?ptr("U",.2):ptr("S",.2)),
      after_effects:[nudge("U",v===1?.002:-.002),nudge("S",v===2?.002:-.002),nudge("A",.001)]
    }))}));
  encounter("page_ending_gate","The Scales of the Fifth Article","Two tallies compete: geopolitical prestige and religious consent. The assembly's reports include every failed promise, every civil-rights safeguard, and every naval alert.","spool_final",finalOptions);
  spools.push({id:"spool_final",spool_type:"General",spool_name:"The Final Consultation",creation_index:8,starts_active:false,encounters:["page_final_council","page_ending_gate"]});
  const ends=[];for(const [key,title,condition,weights,bonus,body] of source.endings)ends.push(encounter("page_end_"+key,title,body,"spool_endings",[],true));
  spools.push({id:"spool_endings",spool_type:"General",spool_name:"Endings · What the World Remembers",creation_index:9,starts_active:false,encounters:ends});
  const initial={
    char_scholar:{A:.55,L:.4,U:.2,M:-.6},char_nurjan:{L:.5,U:-.4,A:.1,M:-.5},char_chen:{T:.5,P:.4},
    char_guo:{S:.45,P:.4,B:.3},char_yusuf:{U:.35,L:.4,A:.25},char_fardad:{S:.45,B:.3,U:-.1},
    char_amal:{T:.55,B:-.25},char_samira:{W:.5,U:.15},char_ward:{B:-.2,T:.3}
  };
  const characters=source.cast.map(([id,name,pronoun])=>({id,name,pronoun,bnumber_properties:Object.fromEntries(Object.entries(P).map(([k,v])=>[v,initial[id]?.[k]??0]))}));
  const authored_properties=Object.values(P).map((property_name,i)=>({id:property_name,property_name,property_type:"bounded number",default_value:0,
    depth:0,attribution_target:"all cast members",affected_characters:[],creation_index:i,creation_time:ts,modified_time:ts}));
  return {IFID:"SW-BALANCE-OF-REASON-RED-MIHNA-2034",about_text:sc("An alternate history, 2034–2041: the converted Chinese Communist Party attempts to lead the Ummah and must win consent without creating a new Mihna."),
    css_theme:"lilac",debug_mode:false,display_mode:1,creation_time:ts,modified_time:ts,title:source.title,storyworld_title:source.title,
    characters,authored_properties,spools,encounters};
}
