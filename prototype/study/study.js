'use strict';
const storageKey='bridgefinder-study-v3';
const studyProtocol='student-interest-v1';
const byId=id=>document.getElementById(id);
const dimensions=['relevance','novelty','actionability'];
const dimensionContainers=['relevanceScale','noveltyScale','actionabilityScale'];
const susItems=[
  'I think that I would like to use this system frequently.',
  'I found the system unnecessarily complex.',
  'I thought the system was easy to use.',
  'I think that I would need the support of a technical person to be able to use this system.',
  'I found the various functions in this system were well integrated.',
  'I thought there was too much inconsistency in this system.',
  'I would imagine that most people would learn to use this system very quickly.',
  'I found the system very cumbersome to use.',
  'I felt very confident using the system.',
  'I needed to learn a lot of things before I could get going with this system.'
];
let allCards=[],cards=[],currentIndex=0,responses={},sus=Array(10).fill(null),participantId=null,seedId=null,datasetId=null,researchInterest='';
const validRating=(value,max)=>Number.isInteger(value)&&value>=1&&value<=max;
const validInterest=value=>typeof value==='string'&&value.trim().length>0&&value.length<=500;
function uuid(){
  if(crypto.randomUUID)return crypto.randomUUID();
  const bytes=crypto.getRandomValues(new Uint8Array(16));bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;
  const hex=[...bytes].map(value=>value.toString(16).padStart(2,'0')).join('');
  return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
}
function validateCards(data){
  const strings=value=>Array.isArray(value)&&value.every(item=>typeof item==='string');
  if(!Array.isArray(data)||!data.length||new Set(data.map(row=>row?.card_id)).size!==data.length)throw new Error('Invalid card identities');
  const revision=data[0].dataset_id;
  if(typeof revision!=='string'||!/^[0-9a-f]{64}$/.test(revision))throw new Error('Missing dataset revision');
  for(const row of data){
    if(!row||row.dataset_id!==revision||!['card_id','seed_id','seed_name','seed_department','candidate_name','introduction_path'].every(key=>typeof row[key]==='string'&&row[key].length>0)||
       ![row.seed_topics,row.candidate_topics,row.sample_papers].every(strings)||
       (row.path_ids!==null&&(!strings(row.path_ids)||row.path_ids.length < 3)))throw new Error('Invalid card data');
  }
  return data;
}
function saveProgress(){
  if(!seedId)return;
  try{
    sessionStorage.setItem(storageKey,JSON.stringify({study_protocol:studyProtocol,research_interest:researchInterest,dataset_id:datasetId,participant_id:participantId,seed_id:seedId,order:cards.map(row=>row.card_id),index:currentIndex,responses,sus}));
    byId('saveStatus').textContent='Progress saved in this browser tab.';
  }catch{byId('saveStatus').textContent='This browser cannot save progress. Keep this tab open until you download your responses.';}
}
function restoreProgress(){
  let draft;
  try{const saved=sessionStorage.getItem(storageKey);if(!saved)return false;draft=JSON.parse(saved);}catch{byId('saveStatus').textContent='Saved progress could not be read. A new session will begin.';return false;}
  try{
    if(!draft||draft.study_protocol!==studyProtocol||!validInterest(draft.research_interest)||draft.dataset_id!==datasetId||typeof draft.participant_id!=='string'||!draft.participant_id.trim())throw new Error('Stale session');
    const expected=allCards.filter(row=>row.seed_id===draft.seed_id);
    if(!expected.length||!Array.isArray(draft.order)||draft.order.length!==expected.length||new Set(draft.order).size!==expected.length||!expected.every(row=>draft.order.includes(row.card_id))||
       !Number.isInteger(draft.index)||draft.index<0||draft.index>expected.length||!draft.responses||typeof draft.responses!=='object'||Array.isArray(draft.responses)||
       !Array.isArray(draft.sus)||draft.sus.length!==10||!draft.sus.every(value=>value===null||validRating(value,5)))throw new Error('Invalid saved session');
    for(const [id,rating] of Object.entries(draft.responses)){
      if(!draft.order.includes(id)||!rating||typeof rating!=='object'||Object.keys(rating).some(key=>!dimensions.includes(key))||!Object.values(rating).every(value=>validRating(value,7)))throw new Error('Invalid saved answer');
    }
    // Never allow restored navigation to bypass unanswered preceding cards.
    for(const id of draft.order.slice(0,draft.index))if(!dimensions.every(key=>validRating(draft.responses[id]?.[key],7)))throw new Error('Incomplete saved navigation');
    seedId=draft.seed_id;participantId=draft.participant_id;researchInterest=draft.research_interest;responses=draft.responses;sus=draft.sus;currentIndex=draft.index;
    byId('researchInterest').value=researchInterest;
    cards=draft.order.map(id=>expected.find(row=>row.card_id===id));
    byId('saveStatus').textContent='Resumed your saved session in this tab.';renderCard(currentIndex,false);return true;
  }catch{
    try{sessionStorage.removeItem(storageKey);}catch{}
    byId('saveStatus').textContent='The saved session does not match these cards or is invalid. Please start a new session.';return false;
  }
}
async function loadCards(){
  byId('startStudy').disabled=true;byId('seedSelect').disabled=true;byId('retryCards').hidden=true;
  byId('loadStatus').textContent='Loading cards…';
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
  try{
    const response=await fetch('study_cards.json',{signal:controller.signal});if(!response.ok)throw new Error('Dataset unavailable');
    allCards=validateCards(await response.json());datasetId=allCards[0].dataset_id;
    byId('seedSelect').replaceChildren();
    for(const [id,row] of new Map(allCards.map(card=>[card.seed_id,card])))byId('seedSelect').add(new Option(`${row.seed_name} (${row.seed_department})`,id));
    byId('startStudy').disabled=false;byId('seedSelect').disabled=false;
    byId('loadStatus').textContent='Ready. Repeated candidates appear once, and recommendation methods stay hidden.';
    restoreProgress();
  }catch{byId('loadStatus').textContent='Cards could not load. Try again or contact the facilitator. No sample answers or substitute cards will be used.';byId('retryCards').hidden=false;}
  finally{clearTimeout(timeout);}
}
function startStudy(){
  const interest=byId('researchInterest').value.trim();
  if(!validInterest(interest)){byId('setupStatus').textContent='Please write a research interest before rating suggestions.';byId('researchInterest').focus();return;}
  seedId=byId('seedSelect').value;cards=allCards.filter(row=>row.seed_id===seedId);
  if(!cards.length)return;
  researchInterest=interest;byId('setupStatus').textContent='';
  responses={};sus=Array(10).fill(null);participantId=uuid();currentIndex=0;
  for(let i=cards.length-1;i>0;i--){const value=crypto.getRandomValues(new Uint32Array(1))[0];const j=Math.floor(value/4294967296*(i+1));[cards[i],cards[j]]=[cards[j],cards[i]];}
  renderCard(0);saveProgress();
}
function renderScale(container,dimension){
  container.replaceChildren();
  for(let value=1;value<=7;value++){
    const label=document.createElement('label');label.className='likert-option';
    const input=document.createElement('input');input.type='radio';input.name=dimension;input.value=value;input.setAttribute('aria-label',`${dimension} ${value}`);
    input.checked=responses[cards[currentIndex].card_id]?.[dimension]===value;
    input.addEventListener('change',()=>{responses[cards[currentIndex].card_id]??={};responses[cards[currentIndex].card_id][dimension]=value;byId('ratingStatus').textContent='';saveProgress();});
    const text=document.createElement('span');text.textContent=value;label.append(input,text);container.append(label);
  }
}
function renderCard(index,focus=true){
  currentIndex=index;
  byId('setupView').hidden=true;byId('sessionControls').hidden=false;
  byId('summaryView').hidden=index<cards.length;byId('cardView').hidden=index>=cards.length;
  if(index>=cards.length){
    byId('cardCounterBadge').textContent='Interface questionnaire';byId('susQuestions').replaceChildren();
    susItems.forEach((text,i)=>{
      const label=document.createElement('label');label.className='sus-question';label.textContent=`${i+1}. ${text}`;
      const select=document.createElement('select');select.id=`sus-${i}`;select.add(new Option('Choose an answer',''));
      for(let value=1;value<=5;value++)select.add(new Option(`${value}${value===1?' — strongly disagree':value===5?' — strongly agree':''}`,value));
      select.value=sus[i]===null?'':String(sus[i]);
      select.addEventListener('change',()=>{sus[i]=select.value?Number(select.value):null;byId('exportStatus').textContent='';saveProgress();});
      label.append(select);byId('susQuestions').append(label);
    });
    if(focus)byId('susHeading').focus();return;
  }
  const card=cards[index];byId('ratingStatus').textContent='';byId('interestContext').textContent=researchInterest;
  byId('cardCounterBadge').textContent=`Card ${index+1} of ${cards.length}`;
  for(const [id,text] of Object.entries({seedName:card.seed_name,seedMeta:`${card.seed_department} · ${card.seed_topics.join(' · ')}`,candidateName:card.candidate_name,introPath:card.introduction_path}))byId(id).textContent=text;
  for(const [id,values] of [['candTopics',card.candidate_topics],['samplePapers',card.sample_papers]]){
    byId(id).replaceChildren();for(const text of values){const item=document.createElement(id==='samplePapers'?'li':'span');item.textContent=text;if(id==='candTopics')item.className='topic-tag';byId(id).append(item);}
  }
  dimensions.forEach((dimension,i)=>renderScale(byId(dimensionContainers[i]),dimension));
  byId('prevBtn').disabled=index===0;byId('nextBtn').textContent=index===cards.length-1?'Continue to interface questions':'Next card';
  if(focus){byId('candidateName').focus();window.scrollTo(0,0);}
}
function nextCard(){
  const rating=responses[cards[currentIndex].card_id];
  if(!dimensions.every(key=>validRating(rating?.[key],7))){byId('ratingStatus').textContent='Please answer all three ratings before continuing.';return;}
  renderCard(currentIndex+1);saveProgress();
}
function buildExport(){
  if(!validInterest(researchInterest))throw new Error('A stated research interest is required.');
  if(!cards.length||!participantId||!cards.every(card=>dimensions.every(key=>validRating(responses[card.card_id]?.[key],7))))throw new Error('Please rate every card. Missing answers are never filled automatically.');
  if(!sus.every(value=>validRating(value,5)))throw new Error('Please answer all ten interface questions.');
  return {schema_version:1,study_protocol:studyProtocol,research_interest:researchInterest,dataset_id:datasetId,participant_id:participantId,seed_id:seedId,sus:[...sus],ratings:cards.map(card=>({card_id:card.card_id,...responses[card.card_id]}))};
}
function exportResponses(){
  try{
    const url=URL.createObjectURL(new Blob([JSON.stringify([buildExport()],null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download='study_responses.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    byId('exportStatus').textContent='Downloaded. Share the file only if you consent to participate.';
  }catch(error){byId('exportStatus').textContent=error.message;}
}
function resetStudy(){
  if(!confirm('Clear all answers in this tab and start a new session? This cannot be undone.'))return;
  try{sessionStorage.removeItem(storageKey);}catch{}
  cards=[];seedId=null;responses={};sus=Array(10).fill(null);participantId=null;currentIndex=0;researchInterest='';byId('researchInterest').value='';byId('setupStatus').textContent='';
  byId('setupView').hidden=false;byId('cardView').hidden=true;byId('summaryView').hidden=true;byId('sessionControls').hidden=true;
  byId('saveStatus').textContent='Session cleared.';byId('cardCounterBadge').textContent='Getting started';byId('startStudy').focus();
}
byId('startStudy').addEventListener('click',startStudy);byId('retryCards').addEventListener('click',loadCards);
byId('nextBtn').addEventListener('click',nextCard);byId('prevBtn').addEventListener('click',()=>{if(currentIndex>0){renderCard(currentIndex-1);saveProgress();}});
byId('backToCards').addEventListener('click',()=>{renderCard(cards.length-1);saveProgress();});
byId('exportResponses').addEventListener('click',exportResponses);byId('resetStudy').addEventListener('click',resetStudy);
loadCards();
