'use strict';

// Public JSON remains unmodified. Publication strings are inserted as text,
// never markup, so search, labels, and drafts all use the same real names.
let appData = null;
let selectedSeedId = null;
let candidateFilter = null;
let activeScreen = 'researchers';
let mapState = null;
let returnFocus = null;
const byId = id => document.getElementById(id);
const validColor = value => /^#[0-9a-f]{6}$/i.test(value) ? value : '#2563eb';
const number = value => Number(value).toFixed(3);
const element = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const button = (text, action, className = '') => {
  const node = element('button', className, text);
  node.type = 'button'; node.addEventListener('click', action); return node;
};
const selectedSeed = () => appData.seeds.find(row => row.id === selectedSeedId);
const recommendations = () => appData.recommendations[selectedSeedId] || [];

function validateBundle(data) {
  const strings = values => Array.isArray(values) && values.every(value => typeof value === 'string');
  const profile = row => row && typeof row.id === 'string' && typeof row.name === 'string' &&
    typeof row.community_name === 'string' && strings(row.topics) && Number.isFinite(row.burt_autonomy) &&
    row.burt_autonomy >= 0 && row.burt_autonomy <= 1;
  if (!data || !Array.isArray(data.seeds) || !data.seeds.length || !data.seeds.every(profile) ||
      new Set(data.seeds.map(row => row.id)).size !== data.seeds.length ||
      !data.recommendations || !data.graph || !Array.isArray(data.graph.nodes) || !data.graph.nodes.every(profile) ||
      !Array.isArray(data.graph.links)) throw new Error('The research dataset has an invalid format.');
  const nodes = new Map(data.graph.nodes.map(row => [row.id, row]));
  if (nodes.size !== data.graph.nodes.length || !data.seeds.every(row => nodes.has(row.id))) throw new Error('Invalid graph identities.');
  const edges = new Set();
  for (const link of data.graph.links) {
    if (!nodes.has(link.source) || !nodes.has(link.target) || !['intra','structural_hole'].includes(link.type)) throw new Error('Invalid map edge.');
    if (link.type === 'intra') { edges.add(JSON.stringify([link.source,link.target])); edges.add(JSON.stringify([link.target,link.source])); }
  }
  for (const seed of data.seeds) {
    const rows = data.recommendations[seed.id];
    if (!Array.isArray(rows) || new Set(rows.map(row => row.candidate_id)).size !== rows.length) throw new Error('Invalid candidate list.');
    for (const [index,row] of rows.entries()) {
      if (!profile(row) || row.candidate_id !== row.id || !nodes.has(row.id) || row.id === seed.id || row.rank !== index+1 ||
          !(Number.isFinite(row.score) && row.score >= 0 && row.score <= 1.5) ||
          ![row.topic_similarity,row.boundary_spanning].every(value => Number.isFinite(value) && value >= 0 && value <= 1) ||
          !strings(row.sample_papers) || row.community_id === seed.community_id || edges.has(JSON.stringify([seed.id,row.id]))) throw new Error('Invalid recommendation.');
      if (row.path_ids !== null && (!strings(row.path_ids) || row.path_ids.length < 4 ||
          row.path_ids[0] !== seed.id || row.path_ids.at(-1) !== row.id || new Set(row.path_ids).size !== row.path_ids.length ||
          !row.path_ids.every((id,i,path) => nodes.has(id) && (!i || edges.has(JSON.stringify([path[i-1],id])))))) throw new Error('Invalid collaboration route.');
    }
  }
  return data;
}

async function loadData() {
  appData = null;
  byId('loadState').hidden = false; byId('loadState').textContent = 'Loading the research network…';
  byId('retryLoad').hidden = true;
  document.querySelectorAll('.screen').forEach(screen => screen.hidden = true);
  document.querySelectorAll('.nav-tab').forEach(tab => tab.disabled = true);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('data.json', {signal:controller.signal});
    if (!response.ok) throw new Error(`Dataset request failed (${response.status}).`);
    appData = validateBundle(await response.json());
    renderFilters();
    byId('loadState').hidden = true;
    document.querySelectorAll('.nav-tab').forEach(tab => tab.disabled = false);
    restoreLocation();
  } catch (error) {
    byId('loadState').textContent = 'The research network could not load. Check your connection and try again. If this file was opened directly, serve the prototype with an HTTP server.';
    byId('retryLoad').hidden = false;
  } finally { clearTimeout(timeout); }
}

function renderFilters() {
  const community = byId('communityFilter');
  community.replaceChildren(new Option('All communities','all'));
  for (const [id,name] of new Map(appData.seeds.map(row => [row.community_id,row.community_name]))) community.add(new Option(name,String(id)));
  const topic = byId('topicFilter'); topic.replaceChildren(new Option('All research areas','all'));
  for (const name of [...new Set(appData.seeds.map(row => row.topic_group || 'Other topics'))].sort()) topic.add(new Option(name,name));
}

function communityTag(row) {
  const tag = element('span','community-tag');
  const dot = element('span','dot'); dot.style.background = validColor(row.color); dot.setAttribute('aria-hidden','true');
  tag.append(dot, document.createTextNode(row.community_name)); return tag;
}
function topicTags(topics) {
  const list = element('div','seed-topics');
  for (const topic of topics) list.append(element('span','topic-tag',topic));
  if (!topics.length) list.append(element('span','muted','No training-period topics available.'));
  return list;
}
function renderSeedGrid() {
  if (!appData) return;
  const search = byId('seedSearchInput').value.trim().toLocaleLowerCase();
  const community = byId('communityFilter').value, topic = byId('topicFilter').value;
  const filtered = appData.seeds.filter(row => (community === 'all' || String(row.community_id) === community) &&
    (topic === 'all' || row.topic_group === topic) &&
    [row.name,row.community_name,row.topic_group || '',...row.topics].some(text => text.toLocaleLowerCase().includes(search)));
  byId('seedCount').textContent = `${filtered.length} of ${appData.seeds.length} starting researchers`;
  byId('emptySearch').hidden = filtered.length > 0;
  byId('seedGrid').replaceChildren();
  for (const row of filtered) {
    const card = element('article','seed-card'+(row.id === selectedSeedId ? ' selected' : ''));
    card.dataset.seedId = row.id;
    card.append(element('h2','seed-name',row.name),communityTag(row));
    if (row.topic_group) card.append(element('p','muted',row.topic_group));
    card.append(topicTags(row.topics));
    const choose = button('Explore →',() => { selectedSeedId=row.id;candidateFilter=null;showScreen('map'); },'select-seed-btn');
    choose.setAttribute('aria-label',`Explore ${row.name}`);
    card.append(choose); byId('seedGrid').append(card);
  }
}
function syncLocation(replace = false) {
  const url = new URL(location.href);
  url.hash = activeScreen;
  url.searchParams.set('seed',selectedSeedId);
  if (candidateFilter) url.searchParams.set('candidate',candidateFilter); else url.searchParams.delete('candidate');
  if (url.href !== location.href) history[replace ? 'replaceState':'pushState'](null,'',url);
}
function restoreLocation() {
  if (!appData) return;
  const url = new URL(location.href), seed = url.searchParams.get('seed');
  selectedSeedId = appData.seeds.some(row => row.id === seed) ? seed : appData.seeds[0].id;
  const candidate = url.searchParams.get('candidate');
  candidateFilter = recommendations().some(row => row.id === candidate) ? candidate : null;
  showScreen(['researchers','map','recommendations'].includes(url.hash.slice(1)) ? url.hash.slice(1) : 'researchers',false);
  syncLocation(true);
}
function showScreen(screen, record = true) {
  if (!appData) return;
  activeScreen = screen;
  const ids = {researchers:'screenSeeds',map:'screenMap',recommendations:'screenRecs'};
  document.querySelectorAll('.screen').forEach(node => { node.hidden = node.id !== ids[screen]; node.classList.toggle('active',!node.hidden); });
  document.querySelectorAll('.nav-tab').forEach(tab => {
    const selected = tab.dataset.screen === screen;
    tab.classList.toggle('active',selected);
    if (selected) tab.setAttribute('aria-current','page'); else tab.removeAttribute('aria-current');
  });
  renderSeedGrid();
  if (screen === 'map') { renderSidebar(); renderMap(); }
  if (screen === 'recommendations') renderRecCards();
  if (record) { syncLocation(); byId('main').focus({preventScroll:true}); window.scrollTo(0,0); }
}
function inspectRecommendation(seedId,candidateId) {
  if (!appData.seeds.some(row => row.id === seedId)) return;
  selectedSeedId=seedId;
  candidateFilter=recommendations().some(row => row.id === candidateId) ? candidateId : null;
  showScreen('recommendations');
}
function showAllRecommendations() { candidateFilter=null;showScreen('recommendations'); }
function renderSidebar() {
  const seed=selectedSeed();
  byId('mapContext').textContent = `Starting with ${seed.name}. Inspect an orange link or choose a suggestion from the list.`;
  byId('sidebarSeedName').textContent=seed.name;
  byId('sidebarSeedDept').textContent=seed.community_name;
  byId('sidebarRecMiniList').replaceChildren();
  for (const row of recommendations()) {
    const choose=button(`#${row.rank} ${row.name}`,() => inspectRecommendation(seed.id,row.id),'mini-rec');
    choose.dataset.candidateId=row.id;
    choose.append(element('span','',`${row.community_name} · ${row.path_ids ? row.path_ids.length-1+' co-authorship hops':'No short route'}`));
    byId('sidebarRecMiniList').append(choose);
  }
  if (!recommendations().length) byId('sidebarRecMiniList').append(element('p','notice','No eligible suggestions for this researcher. Choose another starting researcher.'));
}
function renderRecCards() {
  const seed=selectedSeed();
  byId('recsSeedHeaderName').textContent=seed.name;
  byId('recsSeedHeaderMeta').textContent=`${seed.community_name}. Based on publications up to 2019.`;
  byId('showAllCards').hidden=!candidateFilter;
  byId('recCardList').replaceChildren();
  const rows=recommendations().filter(row => !candidateFilter || row.id === candidateFilter);
  if (!rows.length) byId('recCardList').append(element('p','notice','No suggestions are available. Choose another starting researcher.'));
  for (const row of rows) {
    const card=element('article','rec-card'); card.dataset.candidateId=row.id;
    const top=element('div','rec-top-row'), intro=element('div');
    intro.append(element('span','rank-number',String(row.rank).padStart(2,'0')),element('h2','rec-name',row.name),communityTag(row));
    top.append(intro);
    if (/^https:\/\/openalex\.org\/A[0-9]+$/.test(row.id)) { const source=element('a','profile-source','OpenAlex profile');source.href=row.id;source.target='_blank';source.rel='noopener';source.setAttribute('aria-label','OpenAlex profile (opens in a new tab)');top.append(source); }
    card.append(top);
    const route=element('section','path-flow'); route.append(element('h3','',row.path_ids ? 'Possible introduction':'No observed route within three hops'));
    if(row.path_ids) route.append(element('p','route-distance',`${row.path_ids.length-1} co-authorship steps from ${seed.name}`));
    if (row.path_ids) {
      const steps=element('ol','path-steps-row');
      row.path_ids.forEach((id,index) => {
        const person=appData.graph.nodes.find(node => node.id === id);
        const step=element('li','path-step-node');
        step.append(element('small','',index===0 ? 'Starting researcher' : index===row.path_ids.length-1 ? 'Suggested researcher' : 'Co-author intermediary'),document.createTextNode(person.name));
        steps.append(step);
      });route.append(steps);
    } else route.append(element('p','','Consider direct outreach. No intermediary is verified; longer paths may exist.'));
    route.append(element('p','path-note','This route comes from shared publications. Check that the intermediary knows them and can help.'));card.append(route);
    const metrics=element('dl','metrics-bar');
    for (const [label,value] of [['Topic overlap',row.topic_similarity],['Three-step routes',row.three_hop_paths],['Route bonus',row.path_bonus]]) {
      const item=element('div','metric-item');item.append(element('dt','',label),element('dd','',label === 'Three-step routes' ? String(value) : number(value)));metrics.append(item);
    }
    const relationship=`These researchers have no shared co-author in the graph. This route uses ${row.path_ids.length-2} intermediaries. The score combines topic overlap with a bonus for three-step introduction routes.`;
    const explanation=element('details','ranking-details');explanation.append(element('summary','','How this suggestion was ranked'),element('p','muted',relationship),element('p','muted',`Combined ranking score: ${number(row.score)}. These are research-network measures, not probabilities.`),metrics);
    card.append(element('h3','','Research topics'),topicTags(row.topics),element('h3','','Example publications'));
    const papers=element('ul','paper-list');for (const title of row.sample_papers) papers.append(element('li','',title));
    if (!row.sample_papers.length) papers.append(element('li','','No example publications available.'));
    card.append(papers,explanation);
    const footer=element('div','card-footer');footer.append(element('p','muted','Verify current research interests and availability before reaching out.'),button('Draft an email',event => openIntroModal(seed,row,event.currentTarget),'outreach-button'));
    card.append(footer);byId('recCardList').append(card);
  }
}

function renderMap() {
  byId('mapUnavailable').hidden=typeof window.d3 !== 'undefined';
  if (typeof window.d3 === 'undefined') return;
  const seed=selectedSeed(), visible=new Set([seed.id]);
  for (const row of recommendations()) { visible.add(row.id);for (const id of row.path_ids || []) visible.add(id); }
  const nodes=appData.graph.nodes.filter(row => visible.has(row.id)).map(row => ({...row}));
  const links=appData.graph.links.filter(link => visible.has(link.source) && visible.has(link.target) && (link.type === 'intra' || link.seed_id === seed.id)).map(link => ({...link}));
  const wrap=byId('topoMapSvg').parentElement;
  const width=Math.max(250,wrap.clientWidth),height=wrap.clientHeight;
  const svg=d3.select('#topoMapSvg').attr('viewBox',`0 0 ${width} ${height}`);svg.selectAll('*').remove();
  const g=svg.append('g');
  const zoom=d3.zoom().scaleExtent([.2,5]).on('zoom',event => g.attr('transform',event.transform));svg.call(zoom);
  const simulation=d3.forceSimulation(nodes).randomSource(d3.randomLcg(42))
    .force('link',d3.forceLink(links).id(row=>row.id).distance(row=>row.type==='structural_hole'?155:90))
    .force('charge',d3.forceManyBody().strength(-450)).force('center',d3.forceCenter(width/2,height/2)).force('collision',d3.forceCollide(28)).stop();
  simulation.tick(200);
  const line=g.append('g').selectAll('line').data(links).join('line').attr('class','map-link')
    .attr('stroke',row=>row.type==='structural_hole'?'#c63d1d':'#91a4bc').attr('stroke-width',row=>row.type==='structural_hole'?2.5:1.5)
    .attr('stroke-dasharray',row=>row.type==='structural_hole'?'7 5':null).attr('data-kind',row=>row.type)
    .attr('tabindex',row=>row.type==='structural_hole'?0:null).attr('role',row=>row.type==='structural_hole'?'button':null)
    .attr('aria-label',row=>row.type==='structural_hole'?`Inspect ${appData.graph.nodes.find(n=>n.id===row.candidate_id).name}`:null)
    .attr('cursor',row=>row.type==='structural_hole'?'pointer':null)
    .on('click',(event,row)=>{ if(row.type==='structural_hole') inspectRecommendation(seed.id,row.candidate_id); })
    .on('keydown',(event,row)=>{ if(row.type==='structural_hole' && ['Enter',' '].includes(event.key)){event.preventDefault();inspectRecommendation(seed.id,row.candidate_id);} });
  const node=g.append('g').selectAll('g').data(nodes).join('g').attr('class','map-node');
  node.append('circle').attr('r',row=>row.id===seed.id?15:11).attr('fill',row=>validColor(row.color)).attr('stroke',row=>row.id===seed.id?'#c63d1d':'white').attr('stroke-width',row=>row.id===seed.id?4:2);
  node.append('text').attr('class','map-label').attr('dx',15).attr('dy',4).text(row=>row.name.split(' ').slice(-1)[0]);
  node.append('title').text(row=>`${row.name} · ${row.community_name}`);
  function position(){line.attr('x1',row=>row.source.x).attr('y1',row=>row.source.y).attr('x2',row=>row.target.x).attr('y2',row=>row.target.y);node.attr('transform',row=>`translate(${row.x},${row.y})`);}
  // Moving a node does not restart a global simulation or invalidate the fitted view.
  node.call(d3.drag().on('drag',(event,row)=>{row.x=event.x;row.y=event.y;position();}));
  position();mapState={svg,g,zoom,nodes,width,height};fitMap();
}
function fitMap() {
  if (!mapState || activeScreen !== 'map') return;
  const {svg,zoom,nodes,width,height}=mapState;
  const x0=d3.min(nodes,row=>row.x)-45,x1=d3.max(nodes,row=>row.x)+85,y0=d3.min(nodes,row=>row.y)-45,y1=d3.max(nodes,row=>row.y)+45;
  const scale=Math.max(.2,Math.min(1.5,(width-35)/(x1-x0),(height-135)/(y1-y0)));
  svg.call(zoom.transform,d3.zoomIdentity.translate(width/2,(height-75)/2).scale(scale).translate(-(x0+x1)/2,-(y0+y1)/2));
}
function openIntroModal(seed,row,trigger) {
  returnFocus=trigger;
  byId('copyStatus').textContent='';
  const route=row.path_ids ? row.path_ids.map(id=>appData.graph.nodes.find(node=>node.id===id).name).join(' → ') : 'No observed co-authorship route within three hops';
  byId('modalEmailText').value=`Subject: Research interests and a possible conversation\n\nDear ${row.name},\n\nI am exploring research related to ${seed.name}'s work and would like to learn more about your current research.\n\nBridgeFinder shows this historical publication route: ${route}. It is not a confirmed personal connection. I would check any proposed intermediary before requesting an introduction.\n\nWould you be open to a brief conversation about your research and appropriate opportunities for a student to contribute?\n\nBest regards,\n[Your name and actual affiliation]`;
  byId('introModal').showModal();byId('modalEmailText').focus();
}
function downloadText(text,filename,mime='text/plain') {
  const url=URL.createObjectURL(new Blob([text],{type:mime}));const link=element('a');link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function copyEmail() {
  try { if (!navigator.clipboard) throw new Error('Clipboard unavailable');await navigator.clipboard.writeText(byId('modalEmailText').value);byId('copyStatus').textContent='Message copied.'; }
  catch { byId('copyStatus').textContent='Copy is unavailable in this browser. Select the message and copy it manually, or download the text.'; }
}
byId('retryLoad').addEventListener('click',loadData);
byId('seedSearchInput').addEventListener('input',renderSeedGrid);
for (const id of ['communityFilter','topicFilter']) byId(id).addEventListener('change',renderSeedGrid);
byId('clearFilters').addEventListener('click',()=>{byId('seedSearchInput').value='';byId('communityFilter').value='all';byId('topicFilter').value='all';renderSeedGrid();});
document.querySelectorAll('.nav-tab').forEach(tab=>tab.addEventListener('click',()=>{if(tab.dataset.screen==='recommendations')candidateFilter=null;showScreen(tab.dataset.screen);}));
byId('mapAllCards').addEventListener('click',showAllRecommendations);byId('showAllCards').addEventListener('click',showAllRecommendations);
byId('changeSeed').addEventListener('click',()=>showScreen('researchers'));
byId('zoomIn').addEventListener('click',()=>{if(mapState)mapState.svg.call(mapState.zoom.scaleBy,1.3);});
byId('zoomOut').addEventListener('click',()=>{if(mapState)mapState.svg.call(mapState.zoom.scaleBy,1/1.3);});byId('resetZoom').addEventListener('click',fitMap);
byId('closeDraft').addEventListener('click',()=>byId('introModal').close());
byId('introModal').addEventListener('close',()=>returnFocus?.focus());
byId('introModal').addEventListener('click',event=>{if(event.target===byId('introModal')){const box=event.target.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)event.target.close();}});
byId('copyDraft').addEventListener('click',copyEmail);
byId('downloadDraft').addEventListener('click',()=>downloadText(byId('modalEmailText').value,'bridgefinder-outreach.txt'));
window.addEventListener('popstate',restoreLocation);
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(appData && activeScreen==='map')renderMap();},120);});
loadData();
