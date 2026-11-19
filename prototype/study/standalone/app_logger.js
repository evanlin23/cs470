// Runs inside the embedded app after app.js. It records what the participant
// does (screens, choices, opened cards, the outreach draft) and posts each
// event to the study page. Typed draft text is never recorded.
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const clean = (value, max = 120) => String(value || '').trim().replace(/\s+/g, ' ').slice(0, max);
  const post = (type, detail = {}) => {
    try { parent.postMessage({bf: 'bridgefinder-app-event', type, detail}, '*'); } catch { /* not embedded */ }
  };
  const screens = {screenSeeds: 'researchers', screenMap: 'network', screenRecs: 'suggestions'};
  let lastScreen = null, lastCards = '', draftFor = null, draftOpen = false, lastWheel = 0;

  function checkScreen() {
    for (const [id, name] of Object.entries(screens)) {
      const node = byId(id);
      if (node && !node.hidden && name !== lastScreen) {
        lastScreen = name;
        post('screen', name === 'network' ? {screen: name, seed: clean(byId('sidebarSeedName').textContent)} : {screen: name});
      }
    }
  }
  function checkCards() {
    const list = byId('recCardList');
    if (!list || byId('screenRecs').hidden) return;
    const cards = [...list.querySelectorAll('article.rec-card')];
    const seed = clean(byId('recsSeedHeaderName').textContent);
    const key = `${seed}@${cards.map(card => card.dataset.candidateId).join('|')}`;
    if (!cards.length || key === lastCards) return;
    lastCards = key;
    if (cards.length === 1) {
      const route = [...cards[0].querySelectorAll('.path-step-node')].map(step => clean(step.lastChild && step.lastChild.textContent, 80));
      post('card_opened', {seed, candidate: clean(cards[0].querySelector('.rec-name').textContent), route});
    } else {
      post('card_list', {seed, count: cards.length});
    }
  }
  function checkDraft() {
    const open = byId('introModal').open;
    if (open && !draftOpen) post('draft_opened', {candidate: draftFor});
    if (!open && draftOpen) post('draft_closed');
    draftOpen = open;
  }
  const observer = new MutationObserver(() => { checkScreen(); checkCards(); checkDraft(); });
  for (const id of Object.keys(screens)) observer.observe(byId(id), {attributes: true, attributeFilter: ['hidden']});
  observer.observe(byId('recCardList'), {childList: true});
  observer.observe(byId('introModal'), {attributes: true, attributeFilter: ['open']});

  document.addEventListener('click', event => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return;
    const card = target.closest('article.rec-card');
    const cardName = card ? clean(card.querySelector('.rec-name').textContent) : null;
    if (target.closest('.select-seed-btn')) post('researcher_chosen', {seed: clean(target.closest('.select-seed-btn').getAttribute('aria-label')).replace(/^Explore /, '')});
    else if (target.closest('.mini-rec')) post('suggestion_from_list', {candidate: clean(target.closest('.mini-rec').firstChild && target.closest('.mini-rec').firstChild.textContent, 80)});
    else if (target.closest('.map-link')) post('map_line_clicked');
    else if (target.closest('.map-node')) post('map_person_clicked', {name: clean(target.closest('.map-node').textContent, 60)});
    else if (target.closest('.nav-tab')) post('nav_tab', {screen: target.closest('.nav-tab').dataset.screen});
    else if (target.closest('#mapAllCards, #showAllCards')) post('all_suggestions');
    else if (target.closest('#changeSeed')) post('change_researcher');
    else if (target.closest('.outreach-button')) { draftFor = cardName; }
    else if (target.closest('#copyDraft')) post('draft_copied');
    else if (target.closest('#downloadDraft')) post('draft_downloaded');
    else if (target.closest('.ranking-details summary')) post('ranking_explanation_toggled', {candidate: cardName});
    else if (target.closest('.profile-source')) post('openalex_profile_opened', {candidate: cardName});
    else if (target.closest('#zoomIn, #zoomOut, #resetZoom')) post('map_zoom_button', {button: target.closest('button').id});
    else if (target.closest('#clearFilters')) post('filters_cleared');
  }, true);
  byId('topoMapSvg').addEventListener('wheel', () => {
    if (Date.now() - lastWheel > 3000) { lastWheel = Date.now(); post('map_scroll_zoom'); }
  }, {passive: true});
  let searchTimer = null;
  byId('seedSearchInput').addEventListener('input', event => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { if (event.target.value.trim()) post('search', {query: clean(event.target.value, 60)}); }, 1200);
  });
  for (const id of ['communityFilter', 'topicFilter']) {
    byId(id).addEventListener('change', event => post('filter', {filter: id, value: clean(event.target.selectedOptions[0] && event.target.selectedOptions[0].textContent, 60)}));
  }
  post('app_loaded');
  checkScreen();
})();
