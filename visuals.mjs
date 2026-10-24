// Visual production layer for Balance of Reason.
// The original engine.mjs is the sole owner of decisions, state, turns and results.
// This module only presents the current state and dispatches callbacks to the player.

export const ART={
  hero:["assets/hero.webp","assets/hero.svg"],
  warroom:["assets/warroom.webp","assets/warroom.svg"],
  summit:["assets/summit.webp","assets/summit.svg"],
  map:["assets/world.webp","assets/world.svg"],
  diplomacy:["assets/dialogue.webp","assets/summit.svg"],
  crisis:["assets/ceasefire.webp","assets/warroom.svg"],
  portraits:["assets/characters.webp","assets/hero.svg"]
};
const $=id=>document.getElementById(id);
const S=(tag)=>document.createElement(tag);
const regular=(tag,className,text)=>{
  const e=S(tag);
  if(className)e.className=className;
  if(text!==undefined)e.textContent=String(text);
  return e;
};
const MOUNTS=new WeakMap();
const metrics={
  U:"Ummah consent",A:"Rationalist credibility",L:"Religious liberty",
  W:"Civilian welfare",P:"Party cohesion",T:"Trade resilience",
  S:"Strategic prestige",B:"Brinkmanship",M:"Mihna coercion",
  D:"Development equity",F:"Internal fitna",C:"AI command integrity",
  G:"World war intensity",H:"Displacement"
};

export const LOCATIONS=[
  {id:"dakar",name:"Dakar",region:"West Africa",x:14,y:61,year:2034,mission:"Community-owned solar and desalination financing; rural livelihoods depend on tariff and loan terms.",metric:"D"},
  {id:"xinjiang",name:"Xinjiang",region:"Western China",x:78,y:24,year:2035,mission:"Religious liberty, Uyghur and Hui civil representation, transparent records and judicial remedies.",metric:"L"},
  {id:"indus",name:"Indus Basin",region:"South Asia",x:67,y:49,year:2036,mission:"Shared water infrastructure, aquifer rights and development sovereignty.",metric:"D"},
  {id:"samarkand",name:"Samarkand",region:"Central Asia",x:66,y:29,year:2037,mission:"Competing rationalist schools, scholarly autonomy and the question of a single interpretation.",metric:"A"},
  {id:"gaza",name:"Gaza",region:"Levant",x:44,y:49,year:2038,mission:"Palestinian-managed reconstruction, hospitals, food corridors and maritime inspections.",metric:"W"},
  {id:"gulf",name:"Hormuz and Gulf",region:"Arabian Gulf",x:55,y:55,year:2039,mission:"Energy security, ship insurance and the diplomatic danger of autonomous maritime alerts.",metric:"B"},
  {id:"manila",name:"Manila",region:"Philippines",x:88,y:76,year:2041,mission:"Disaster insurance, refugee recovery and the proposed Reconstruction Parliament.",metric:"D"},
  {id:"cairo",name:"Cairo",region:"Egypt",x:39,y:47,year:2037,mission:"The House of Disputation and international theological dissent.",metric:"A"},
  {id:"istanbul",name:"Istanbul",region:"Turkey",x:43,y:30,year:2041,mission:"The final assembly and the legitimacy of an elected, recallable chair.",metric:"U"},
  {id:"beijing",name:"Beijing",region:"China",x:85,y:36,year:2034,mission:"The converted Party congress, national security command and the limits of state theology.",metric:"P"},
  {id:"atlantic",name:"Atlantic Compact",region:"Europe and Atlantic",x:26,y:26,year:2039,mission:"War prevention, independent deterrence and verification of AI-generated intelligence.",metric:"C"}
];
const FACES={
  char_secretary:{skin:"#d6a37f",hair:"#13161d",robe:"#22262a",trim:"#c69d5e",bg:"#642c2b",type:"suit"},
  char_veteran:{skin:"#bc987d",hair:"#57524c",robe:"#303e4a",trim:"#9ba8ac",bg:"#444e5b",type:"suit"},
  char_scholar:{skin:"#bf8e70",hair:"#30221d",robe:"#6b8291",trim:"#d4b98c",bg:"#274457",type:"robes"},
  char_nurjan:{skin:"#d4a785",hair:"#392825",robe:"#376452",trim:"#ddc8a0",bg:"#265046",type:"hijab"},
  char_chen:{skin:"#d3a17e",hair:"#28252a",robe:"#42535c",trim:"#b9b3a5",bg:"#394650",type:"suit"},
  char_guo:{skin:"#cc9778",hair:"#10161d",robe:"#253a47",trim:"#b48f57",bg:"#442c2d",type:"uniform"},
  char_yusuf:{skin:"#a97859",hair:"#2b221f",robe:"#64717a",trim:"#bfc5b7",bg:"#315c54",type:"robes"},
  char_fardad:{skin:"#c18b62",hair:"#211915",robe:"#454b3e",trim:"#cdab6c",bg:"#4c4637",type:"robes"},
  char_amal:{skin:"#d6a17d",hair:"#40291f",robe:"#485a62",trim:"#debd81",bg:"#594735",type:"hijab"},
  char_samira:{skin:"#a8795b",hair:"#271c1a",robe:"#74654e",trim:"#ded4bc",bg:"#62523f",type:"field"},
  char_ward:{skin:"#d9b6a0",hair:"#6b4939",robe:"#2c3c56",trim:"#adc4cf",bg:"#273e5b",type:"suit"},
  char_radical:{skin:"#9b674b",hair:"#231c16",robe:"#1d4433",trim:"#ac9569",bg:"#254334",type:"turban"}
};

export function portraitSvg(id,size=96){
  const p=FACES[id]||FACES.char_secretary;
  const turban=p.type==="turban",hijab=p.type==="hijab",suit=p.type==="suit";
  const side=String(size);
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 48" width="'+side+'" height="'+side+'" aria-hidden="true" shape-rendering="crispEdges">'+
   '<rect width="40" height="48" fill="'+p.bg+'"/>'+
   '<path d="M0 43L15 33L26 33L40 43V48H0Z" fill="'+p.trim+'" opacity=".48"/>'+
   '<path d="M3 48L5 35L15 30L25 30L35 35L37 48Z" fill="'+p.robe+'"/>'+
   '<path d="M17 31L17 39L23 39L23 31" fill="'+p.skin+'"/>'+
   (hijab?'<path d="M8 29L10 12L16 5L24 6L31 14L32 42L26 40L27 24L15 25L15 39L7 44Z" fill="'+p.trim+'"/>':'')+
   '<path d="M12 13L14 9L26 9L30 16L29 30L24 34L16 33L11 28Z" fill="'+p.skin+'"/>'+
   '<path d="M11 20L11 11L14 7L19 6L26 7L30 11L30 17L27 15L26 12L15 14L14 18Z" fill="'+p.hair+'"/>'+
   (turban?'<path d="M8 13L13 7L25 4L32 8L31 15L10 17Z" fill="'+p.trim+'"/><path d="M10 15L31 12L32 17L10 20Z" fill="'+p.robe+'"/>':'')+
   '<rect x="15" y="22" width="4" height="2" fill="#241e1b"/><rect x="23" y="22" width="4" height="2" fill="#241e1b"/>'+
   '<rect x="19" y="28" width="5" height="1" fill="#884e3d"/>'+
   ((id==="char_secretary"||id==="char_scholar"||id==="char_veteran")?'<path d="M13 21H20V26H13ZM22 21H29V26H22ZM20 23H22" fill="none" stroke="#bfc4bc" stroke-width="1"/>':'')+
   (suit?'<path d="M16 35L19 39L18 47L21 47L22 39L25 35Z" fill="'+p.trim+'"/>':'')+
   '<path d="M1 3H11M1 3V13M39 35V47H27" stroke="'+p.trim+'" fill="none" opacity=".55"/>'+
   '<path d="M0 0H40V48H0Z" fill="none" stroke="#050c16" stroke-width="2"/></svg>';
}

function fallbackImage(key,element){
  const [raster,vector]=ART[key]||ART.warroom;
  element.src=vector;
  const candidate=new Image();
  candidate.onload=()=>{if(element.isConnected)element.src=raster;};
  candidate.onerror=()=>{};
  candidate.src=raster;
}
function createButton(label,callback,cls=""){
  const b=regular("button",cls,label);
  b.type="button";b.addEventListener("click",callback);
  return b;
}
function h(tag,txt){return regular(tag,"",txt);}
function heading(textValue){
  const top=regular("div","top");
  top.append(h("h2",textValue));
  return top;
}
function note(str){return regular("p","",str);}
function metricPill(key,value){
  return regular("span","",metrics[key]+" "+((value*100>=0)?"+":"")+Math.round(value*100));
}
function renderArtImage(key,alt,className=""){
  const image=S("img");
  image.className=className;image.alt=alt;image.loading="lazy";
  fallbackImage(key,image);
  return image;
}

export function mountVisualPlayer(config){
  const {getSource,getGame,newGame,resumeSaved,exportSaved,shareCampaign}=config;
  const shell=document.querySelector(".shell");
  if(!shell||MOUNTS.has(shell))throw Error("Visual player already mounted or shell missing");
  let activeModal=null,selectedLocation=LOCATIONS[0],chosenFaction=null,selectedResearch=0;
  let lastFocus=null;
  const nav=regular("nav","pixel-nav");nav.setAttribute("aria-label","Game sections");
  const modal=regular("div","art-overlay");modal.hidden=true;modal.id="visual-modal";
  const panel=regular("div","art-window pixel-frame");panel.tabIndex=-1;
  panel.setAttribute("role","dialog");panel.setAttribute("aria-modal","true");panel.setAttribute("aria-label","Storyworld information");
  modal.append(panel);
  const intro=regular("div","art-intro");intro.id="visual-intro";intro.setAttribute("role","dialog");intro.setAttribute("aria-modal","true");
  const stage=regular("div","intro-stage no-raster");
  const badge=regular("div","intro-badge","AN ALTERNATE HISTORY · 2034–2041");
  stage.append(badge);
  const introPanel=regular("div","intro-panel");
  const mainTitle=S("h1");mainTitle.innerHTML='BALANCE OF REASON<span>THE RED MIHNA</span>';
  const sub=regular("p","","REASON · POWER · FREE WILL · THE UMMAH");
  introPanel.append(mainTitle,sub);stage.append(introPanel);
  const menuButtons=regular("div","intro-actions");
  const play=createButton("New campaign",()=>{
    const ok=newGame();
    if(ok!==false){hideIntro();sync();}
  },"primary");
  const resume=createButton("Resume campaign",()=>{
    if(resumeSaved()) {hideIntro();sync();}
  });
  const how=createButton("How to play",()=>openModal("guide"));
  const share=createButton("Copy playtest link",()=>shareCampaign?.());
  menuButtons.append(play,resume,how,share);stage.append(menuButtons);
  stage.append(regular("div","intro-foot","11 FACTIONS · 15 ENDINGS · 16 NATIONAL VARIABLES"));
  intro.append(stage);
  document.body.append(modal,intro);

  // When art assets are installed, their artwork replaces the faithful SVG
  // fallbacks without affecting layout or any state calculation.
  const preloader=new Image();
  preloader.onload=()=>stage.classList.remove("no-raster");
  preloader.src=ART.hero[0];

  const theater=$("theaters");
  theater.parentElement.insertBefore(nav,theater);
  const main=document.querySelector(".layout main.panel");
  const illustration=regular("div","");illustration.id="game-visual";
  const visualImg=renderArtImage("warroom","Pixel-art crisis chamber");
  visualImg.loading="eager";
  const tint=regular("div","visual-tint");
  const visualLabel=regular("div","visual-label");
  illustration.append(visualImg,tint,visualLabel);
  const speaker=regular("div","");speaker.id="visual-speaker";
  main.insertBefore(illustration,$("narrative"));
  main.insertBefore(speaker,$("narrative"));

  const navItems=[
    ["Campaign",()=>closeModal()],
    ["World atlas",()=>openModal("map")],
    ["Diplomacy",()=>openModal("factions")],
    ["Institutions",()=>openModal("research")],
    ["Chronicle",()=>openModal("chronicle")],
    ["Gallery",()=>openModal("gallery")],
    ["Feedback",()=>openModal("feedback")]
  ];
  for(const [label,action] of navItems)nav.append(createButton(label,action));
  const menuBtn=createButton("Main menu",()=>{closeModal();showIntro();},"right");
  nav.append(menuBtn);

  function showIntro(){intro.hidden=false;document.body.dataset.uiMenuOpen="true";resume.disabled=!canResume();setTimeout(()=>play.focus(),0);}
  function hideIntro(){intro.hidden=true;delete document.body.dataset.uiMenuOpen;}
  function canResume(){try{return !!localStorage.getItem("balance-of-reason/autosave-v1");}catch{return false;}}
  function openModal(type){
    if(!getSource())return;
    activeModal=type;modal.hidden=false;
    document.body.dataset.uiModalOpen="true";
    renderModal(type);panel.focus();
  }
  function closeModal(){
    activeModal=null;modal.hidden=true;delete document.body.dataset.uiModalOpen;
  }
  function panelLayout(title){
    panel.replaceChildren();
    const bar=heading(title);
    bar.append(createButton("Close ×",closeModal,"close"));
    panel.append(bar);
  }
  function metricPanel(title,description){
    const c=regular("div","map-caption");const left=regular("div");
    left.append(h("strong",title),note(description));c.append(left);
    return c;
  }

  function renderMap(){
    panelLayout("The living world · campaign atlas");
    const st=getGame();
    const stage=regular("div","map-stage");
    const img=renderArtImage("map","Pixel-art strategy map of Africa, Eurasia and Asia","map-art");
    img.loading="eager";stage.append(img);
    const route=S("svg");route.classList.add("map-overlay");
    route.setAttribute("viewBox","0 0 100 100");route.setAttribute("preserveAspectRatio","none");
    route.innerHTML=LOCATIONS.slice(0,7).map((pt,i)=>{
      if(i===0)return "";
      const prior=LOCATIONS[i-1];
      const dash=i%2?"1.6 1.1":"0.8 1.4";
      return '<path d="M'+prior.x+' '+prior.y+' Q'+(prior.x+pt.x)/2+' '+((prior.y+pt.y)/2-7)+' '+pt.x+' '+pt.y+'" fill="none" stroke="'+(i%3===0?"#db9169":"#82b9a2")+'" stroke-width=".3" stroke-dasharray="'+dash+'" opacity=".8"/>';
    }).join("");
    stage.append(route);
    LOCATIONS.forEach(pt=>{
      const pin=createButton("",()=>{
        selectedLocation=pt;renderMap();
      },"map-pin");
      pin.style.left=pt.x+"%";pin.style.top=pt.y+"%";
      pin.setAttribute("aria-label","Inspect "+pt.name);
      pin.setAttribute("aria-pressed",String(selectedLocation.id===pt.id));
      pin.title=pt.name;
      stage.append(pin);
    });
    panel.append(stage);
    const cap=metricPanel(selectedLocation.name+" · "+selectedLocation.region,selectedLocation.mission);
    cap.append(metricPill(selectedLocation.metric,st.stats[selectedLocation.metric]??0));
    panel.append(cap);
    const legend=regular("div","map-pins-labels");
    LOCATIONS.forEach(pt=>legend.append(createButton(pt.name,()=>{selectedLocation=pt;renderMap();})));
    panel.append(legend);
    panel.append(note("Route lines illustrate the game's competing development and diplomatic corridors. They carry no modeled troop movements or navigation data."));
  }
  function renderFactions(){
    panelLayout("Diplomacy · independent factions");
    const source=getSource(),game=getGame();
    if(!chosenFaction)chosenFaction=source.factions[0].id;
    const list=regular("div","faction-list");
    const ranked=source.factions.slice().sort((a,b)=>(game.factions[b.id]??0)-(game.factions[a.id]??0));
    ranked.forEach(f=>{
      const b=createButton("",()=>{chosenFaction=f.id;renderFactions();});
      b.append(document.createRange().createContextualFragment(portraitSvg(f.id,56)));
      const info=regular("span","ftext");
      info.append(h("strong",f.name),h("small","Support "+Math.round((game.factions[f.id]||0)*100)+" · "+(game.factions[f.id]>=0?"cooperative":"skeptical")));
      b.append(info);b.setAttribute("aria-pressed",String(chosenFaction===f.id));
      list.append(b);
    });panel.append(list);
    const target=source.factions.find(f=>f.id===chosenFaction);
    const score=game.factions[target.id]??0;
    const info=metricPanel(target.name+" · "+(score>=0?"support":"resistance"),target.mandate);
    info.append(regular("span","",Math.round(score*100)+" / 100"));
    panel.append(info);
    const thisYear=source.acts[game.yearIndex]?.countermove;
    if(thisYear?.faction===target.id)panel.append(note("Current institutional demand: "+thisYear.title+". Its response follows its accumulated standing and its mandate."));
    panel.append(note("These coalitions independently support or resist decisions through the campaign engine. Their current positions are reported here for inspection."));
  }
  const research=[
    ["Rational theology",[
      ["Five Muʿtazilī principles","Tawḥīd, justice, promise and threat, the intermediate position, and commanding right while forbidding wrong."],
      ["Created Qurʾān","The controversial doctrinal question becomes a constitutional risk if the Party enforces assent."],
      ["Pluralist education","Independent scholarly authority increases credibility when scholars may refuse government doctrine."]]],
    ["Society and development",[
      ["Dakar solar waqf","Community-owned infrastructure responds to debt sovereignty and utility pricing."],
      ["Refugee microgrids","Local power and water systems reduce displacement and help civilian recovery."],
      ["Reconstruction parliament","Affected communities receive a voice in the institutions built in their names."]]],
    ["Geopolitical economy",[
      ["Indus water treaty","Sharing aquifer rights can strengthen a corridor without coercive dependence."],
      ["Hormuz insurance","Trade stability can be strained by maritime escalation or defended through negotiation."],
      ["Palestinian procurement","Civil reconstruction legitimacy depends on local oversight and medical access."]]],
    ["AI and accountability",[
      ["Delegated strategic command","A model's advice becomes dangerous when institutions accept unverified authorization as binding."],
      ["Human Command Tribunal","Revocable mandates and independent evidence can restore accountable crisis control."],
      ["False ceasefire","A fictional fabricated diplomatic record can trigger the World War of the Models."]]]
  ];
  function renderResearch(){
    panelLayout("Institutions · research and policy codex");
    panel.append(note("An illustrated guide to the policies already present in the campaign. Research dossiers explain consequences; policy choices occur through the active scenes."));
    const cols=regular("div","research-grid");
    let counter=0;
    for(const [name,arr] of research){
      const col=regular("section");
      col.append(h("h3",name));
      for(const [item,body] of arr){
        const current=counter++;
        const b=createButton(item,()=>{selectedResearch=current;renderResearch();});
        b.setAttribute("aria-pressed",String(selectedResearch===current));
        col.append(b);
      }cols.append(col);
    }
    panel.append(cols);
    const all=research.flatMap(x=>x[1]);
    const chosen=all[selectedResearch]||all[0];
    panel.append(metricPanel(chosen[0],chosen[1]));
  }
  function renderChronicle(){
    panelLayout("The chronicle · your decisions");
    const game=getGame(),source=getSource();
    panel.append(metricPanel("2034–2041",game.turns+" decisions recorded · "+game.warEpisodes+" wartime chapters · "+game.peaceEpisodes+" peace chapters."));
    if(!game.history.length){panel.append(note("The chronicle begins with your first policy choice."));return;}
    const list=regular("ol","history-archive");
    game.history.slice().reverse().forEach(entry=>{
      const li=S("li");
      const title=h("strong",entry.year+" · "+entry.title);
      const p=note(entry.choice+" "+entry.outcome);
      p.style.fontSize="14px";li.append(title,p);
      list.append(li);
    });panel.append(list);
    panel.append(createButton("Save this campaign record",()=>exportSaved()));
  }
  function renderGallery(){
    panelLayout("Art bible · pixel strategy world");
    panel.append(note("The art direction draws on the generated concept boards: ink-black diplomatic chambers, carved brass frames, brick-red and jade factions, and an atlas of development and crisis routes."));
    const gallery=regular("div","faction-list");
    for(const [key,title] of [["hero","Title and characters"],["map","The campaign map"],["warroom","Beijing's strategy chamber"],["summit","The final assembly"],["diplomacy","Diplomatic encounter"],["crisis","The False Ceasefire"]]){
      const card=regular("div","menu-card");const im=renderArtImage(key,title);
      im.style.width="100%";im.style.aspectRatio="16 / 9";im.style.objectFit="cover";
      card.append(im,h("strong",title));gallery.append(card);
    }
    panel.append(gallery);
  }
  function renderGuide(){
    panelLayout("How to play · a cabinet of reason");
    const content=regular("div","codex-columns");
    const cards=[
      ["You are the Secretary","Your choices change the real standings of China, scholarly councils, Muslim civic movements, development partners and strategic rivals. Each year one institution also acts for itself."],
      ["Read the risk ledger","The 16 national gauges show how close the Party is to fracture, economic distress, loss of consent or an AI war. Red gauges indicate risks."],
      ["Three choices, lasting effects","Select one policy each scene. Other factions may accept, resist or defect. Some outcomes differ even when you repeat the same choice."],
      ["Escalate carefully","Crisis warnings can cost prestige to withdraw. Continuing a war alert can destroy the entire campaign."],
      ["Use the atlas and diplomacy","Explore locations, inspect independent faction mandates, and review your own political chronicle at any time."],
      ["Save and send feedback","Use Copy playtest link to share your campaign choices across devices. The link contains decisions only. Download full traces for audit and fill in the local feedback sheet for playtest notes."]
    ];
    for(const [title,body] of cards){
      const c=regular("section","card");c.append(h("h3",title),note(body));content.append(c);
    }
    panel.append(content);
    panel.append(createButton("Return to the game",()=>{closeModal();hideIntro();}));
  }
  function renderFeedback(){
    panelLayout("Playtest field report");
    panel.append(note("Share your experience of the art, readability, story and the choices. Your notes and an optional exported decision trace remain on your own device."));
    const form=regular("form","feedback-form");
    const prompts=[
      ["Enjoyment","What made you want to keep playing?"],
      ["Confusion","Where did the world, controls or decisions become confusing?"],
      ["Characters","Which character or faction was most memorable?"],
      ["Visuals","Did the map, portraits and background scenes help you follow the story?"],
      ["Next improvements","What would make another session more enjoyable?"]
    ];
    const inputs=[];
    prompts.forEach(([labelText,placeholder])=>{
      const label=S("label");label.textContent=labelText;
      const box=S("textarea");box.placeholder=placeholder;box.rows=2;
      label.append(box);inputs.push({label:labelText,box});form.append(label);
    });
    const include=S("label");include.style.display="flex";include.style.gap="10px";include.style.alignItems="center";
    const check=S("input");check.type="checkbox";check.checked=true;include.append(check,document.createTextNode("Include campaign metrics and choices with my feedback"));
    form.append(include);
    const row=regular("div","feedback-row");
    row.append(createButton("Download feedback",()=>{
      const data={
        game:"Balance of Reason: The Red Mihna",
        edition:getSource()?.version,
        timestamp:new Date().toISOString(),
        responses:Object.fromEntries(inputs.map(x=>[x.label,x.box.value])),
        trace:check.checked?getGame()?.history:null
      };
      const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
      const url=URL.createObjectURL(blob);
      const a=S("a");a.href=url;a.download="balance-of-reason-playtest.json";a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1500);
    }));
    row.append(createButton("Copy notes",()=>{
      const notes=inputs.map(x=>x.label+": "+x.box.value).join("\n\n");
      if(navigator.clipboard?.writeText)navigator.clipboard.writeText(notes).then(()=>{row.lastChild.textContent="Copied notes";}).catch(()=>{row.lastChild.textContent="Select and copy your notes";});
      else row.lastChild.textContent="Select and copy your notes";
    }));
    form.append(row);panel.append(form);
    panel.append(regular("p","feedback-tip","For a personal playtest, download this file and send it together with your saved trace. No feedback is sent to a server by this form."));
  }
  function renderModal(type){
    if(type==="map")renderMap();
    else if(type==="factions")renderFactions();
    else if(type==="research")renderResearch();
    else if(type==="chronicle")renderChronicle();
    else if(type==="gallery")renderGallery();
    else if(type==="feedback")renderFeedback();
    else renderGuide();
  }
  function artFor(scene,game){
    if(game.phase==="final"||game.phase==="end")return "summit";
    if(game.phase==="war"||game.phase==="standoff"||scene.title.match(/false ceasefire|war of/i))return "crisis";
    if(game.phase==="peace"||game.phase==="countermove"||scene.title.match(/council|shura|treaty|conference|summit|cairo/i))return "diplomacy";
    if(scene.title.match(/map|maritime|corridor|dakar|indus|monsoon|aquifer|bank|gulf|energy|port/i))return "map";
    return "warroom";
  }
  function getSpeaker(source,game){
    const year=source.acts[game.yearIndex];
    if(game.phase==="countermove")return year.countermove.faction;
    if(game.phase==="final"||game.phase==="end")return "char_yusuf";
    if(game.phase==="war")return "char_ward";
    if(game.phase==="peace")return "char_scholar";
    return year.witness||"char_secretary";
  }
  function sync(){
    const source=getSource(),game=getGame();
    if(!source||!game)return;
    resume.disabled=!canResume();
    const scene=game.phase==="end"
      ?{year:2042,title:source.endings.find(e=>e[0]===game.result)?.[1]||"Ending"}
      :game.phase==="event"
      ?{title:source.acts[game.yearIndex].events[game.sceneIndex][0],year:source.acts[game.yearIndex].year}
      :{title:game.phase==="countermove"?source.acts[game.yearIndex].countermove.title:game.phase,year:source.acts[game.yearIndex].year};
    const key=artFor(scene,game);
    if(visualImg.dataset.asset!==key){
      visualImg.dataset.asset=key;
      fallbackImage(key,visualImg);
    }
    visualLabel.replaceChildren();
    visualLabel.append(h("span","CHRONICLE "+scene.year+" · "+game.phase.toUpperCase()),h("span","BALANCE OF REASON"));
    const focus=getSpeaker(source,game);
    const actor=source.cast.find(c=>c[0]===focus);
    const f=source.factions.find(c=>c.id===focus);
    if(lastFocus!==focus){
      speaker.replaceChildren();
      const portrait=regular("div","portrait");portrait.innerHTML=portraitSvg(focus,75);
      const caption=regular("div");
      caption.append(h("b",actor?.[1]||"Secretary Lin Wenqi"),h("p",f?.mandate||"The Party weighs the claims of justice, diplomacy and political authority."));
      caption.append(regular("small","◆ THE STORYWORLD'S INDEPENDENT VOICES"));
      speaker.append(portrait,caption);
      lastFocus=focus;
    }
    for(const card of document.querySelectorAll("#coalitions>.stat")){
      const label=card.querySelector(".statname span");
      if(label && !label.querySelector("svg")){
        const name=label.textContent.replace(/^◆ /,"");
        const faction=source.factions.find(f=>f.name===name);
        if(faction){
          const chip=regular("span","portrait-chip");
          chip.innerHTML=portraitSvg(faction.id,26);
          label.prepend(chip);
        }
      }
    }
    if(activeModal)renderModal(activeModal);
  }
  modal.addEventListener("click",event=>{if(event.target===modal)closeModal();});
  document.addEventListener("keydown",event=>{
    if(event.key==="Escape"&&activeModal){closeModal();}
    if(event.key==="Escape"&&!activeModal&&!intro.hidden){event.preventDefault();}
  });
  MOUNTS.set(shell,{sync,showIntro,hideIntro});
  showIntro();
  return {sync,showIntro,hideIntro,openModal,closeModal,hasModal:()=>!!activeModal,showSavedAvailable:()=>{resume.disabled=!canResume();}};
}
