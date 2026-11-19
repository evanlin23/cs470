'use strict';
// One-minute BridgeFinder study. CARDS, SETS, AREAS, APP_DOC and BUILD are inlined
// by build_standalone.py. Each participant rates one prepared set of six cards
// (two from each method, method labels never included in this page) with two
// yes/no questions, then picks the one person they would most like to contact.
const STORE = 'bridgefinder-quick-v1';
const PROTOCOL = 'quick-v1';
const DATASET_ID = CARDS[0].dataset_id;
const MAX_EVENTS = 200;
const QUESTIONS = [['relevant', 'Relevant to my interests?'], ['knew', 'Had you heard of them?']];

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const el = (tag, className, content) => { const node = document.createElement(tag); if (className) node.className = className; if (content !== undefined) node.textContent = content; return node; };
const cardById = id => CARDS.find(card => card.card_id === id);
const random = n => Math.floor(crypto.getRandomValues(new Uint32Array(1))[0] / 4294967296 * n);

function uuid() {
  if (crypto.randomUUID) return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16)); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
  const h = [...b].map(v => v.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}
function fresh() {
  return {v: 1, dataset_id: DATASET_ID, step: 'start', participant_id: uuid(), started_at: null, finished_at: null,
    background: {}, seed_id: null, set_id: null, shown: [], answers: {}, contact: null, comment: '',
    app: {opened: false, start_ms: null, end_ms: null, events: [], confusing: ''}};
}
function load() {
  try {
    const s = JSON.parse(localStorage.getItem(STORE));
    if (s && s.v === 1 && s.dataset_id === DATASET_ID && typeof s.participant_id === 'string') return s;
  } catch { /* storage blocked */ }
  return null;
}
let S = load() || fresh();
function save() {
  let ok = true;
  try { localStorage.setItem(STORE, JSON.stringify(S)); } catch { ok = false; }
  $('#saveNote').textContent = ok ? '' : 'This browser cannot save progress. Keep this tab open until you have sent your answers.';
}
function clearSaved() { try { localStorage.removeItem(STORE); } catch { /* ignore */ } }
function error(step, message) { $(`[data-error="${step}"]`).textContent = message || ''; }

// ---------- navigation ----------
const LABELS = {start: 'About a minute', area: 'Step 2 of 4', rate: 'Step 3 of 4', send: 'Step 4 of 4', app: 'Optional'};
function go(step) {
  S.step = step; save(); render();
  window.scrollTo(0, 0);
  const heading = $(`[data-step="${step}"] h1`);
  if (heading) heading.focus({preventScroll: true});
}
function render() {
  for (const section of $$('[data-step]')) section.hidden = section.dataset.step !== S.step;
  $('#stepBadge').textContent = LABELS[S.step];
  document.body.classList.toggle('wide-step', S.step === 'app' || S.step === 'rate');
  $('#withdraw').hidden = S.step === 'start';
  ({start: renderStart, area: renderArea, rate: renderRate, send: renderSend, app: renderApp})[S.step]();
  if (S.step !== 'app') removeApp();
}

function renderStart() {
  for (const row of $$('[data-pills]')) {
    const key = row.dataset.pills;
    row.replaceChildren(...row.dataset.options.split('|').map(option => {
      const button = el('button', 'pill', option);
      button.type = 'button';
      button.setAttribute('aria-pressed', String(S.background[key] === option));
      button.addEventListener('click', () => { S.background[key] = option; save(); error('start'); renderStart(); });
      return button;
    }));
  }
  $('#field').value = S.background.field || '';
  $('#consent').checked = Boolean(S.started_at);
}
function renderArea() {
  $('#areaChoices').replaceChildren(...AREAS.map(area => {
    const button = el('button', 'area-button');
    button.type = 'button';
    button.append(el('strong', '', area.label), el('small', '', `Starting researcher: ${area.seed_name}`));
    button.addEventListener('click', () => chooseArea(area.seed_id));
    return button;
  }));
}
function chooseArea(seedId) {
  if (S.seed_id !== seedId || !S.shown.length) {
    const sets = SETS[seedId];
    const index = random(sets.length);
    const order = [...sets[index]];
    for (let i = order.length - 1; i > 0; i--) { const j = random(i + 1); [order[i], order[j]] = [order[j], order[i]]; }
    Object.assign(S, {seed_id: seedId, set_id: `${AREAS.findIndex(a => a.seed_id === seedId)}-${index}`, shown: order, answers: {}, contact: null});
  }
  go('rate');
}

// ---------- rating ----------
function yesNo(cardId, key, label) {
  const group = el('div', 'yn');
  group.setAttribute('role', 'group');
  group.setAttribute('aria-label', label);
  group.append(el('span', 'yn-label', label));
  for (const [value, text] of [[true, 'Yes'], [false, 'No']]) {
    const button = el('button', 'yn-button', text);
    button.type = 'button';
    button.setAttribute('aria-pressed', String(S.answers[cardId]?.[key] === value));
    button.addEventListener('click', () => {
      // Round 3: pressing the chosen answer again clears it.
      const answers = (S.answers[cardId] ??= {});
      answers[key] = answers[key] === value ? undefined : value;
      save(); error('rate');
      for (const sibling of group.querySelectorAll('.yn-button')) sibling.setAttribute('aria-pressed', String(sibling === button && answers[key] === value));
      progress();
    });
    group.append(button);
  }
  return group;
}
function renderRate() {
  const seed = AREAS.find(area => area.seed_id === S.seed_id);
  $('#seedLabel').textContent = `${seed.seed_name} (${seed.label.toLowerCase()})`;
  $('#cardGrid').replaceChildren(...S.shown.map((id, position) => {
    const card = cardById(id), box = el('article', 'quick-card');
    box.dataset.cardId = id;
    box.append(el('h2', '', card.candidate_name));
    box.append(el('p', 'quick-topics', card.candidate_topics.slice(0, 3).join(' · ')));
    if (card.sample_papers.length) box.append(el('p', 'quick-paper', `“${card.sample_papers[0]}”`));
    const route = (card.path_ids && card.introduction_path.split(' (')[0]) || card.introduction_path;
    const routeLine = el('p', 'quick-route');
    routeLine.append(el('span', 'muted', 'Possible introduction: '), document.createTextNode(route));
    box.append(routeLine);
    for (const [key, label] of QUESTIONS) box.append(yesNo(id, key, label));
    const pick = el('label', 'choice contact-choice');
    const input = document.createElement('input');
    input.type = 'radio'; input.name = 'contact'; input.value = id; input.checked = S.contact === id;
    pick.append(input, el('span', '', 'I would most like to contact this person'));
    box.append(pick);
    box.setAttribute('aria-label', `Suggestion ${position + 1} of ${S.shown.length}: ${card.candidate_name}`);
    return box;
  }));
  $('input[name="contact"][value="none"]').checked = S.contact === 'none';
  for (const input of $$('input[name="contact"]')) {
    // Round 3: clicking the chosen option again, or "Clear my pick", removes the pick.
    input.addEventListener('click', () => {
      if (S.contact === input.value) { input.checked = false; S.contact = null; } else S.contact = input.value;
      save(); error('rate'); progress();
    });
  }
  progress();
}
function clearContact() {
  S.contact = null;
  for (const input of $$('input[name="contact"]')) input.checked = false;
  save(); progress();
}
function answered() { return S.shown.filter(id => QUESTIONS.every(([key]) => typeof S.answers[id]?.[key] === 'boolean')).length; }
function progress() {
  $('#rateProgress').textContent = `${answered()} of ${S.shown.length} rated${S.contact ? ', favorite chosen' : ''}`;
  $('#clearContact').hidden = !S.contact;
}

// ---------- optional app ----------
let appFrame = null;
function renderApp() {
  S.app.opened = true;
  if (!S.app.start_ms) { S.app.start_ms = Date.now(); save(); }
  $('#appConfusing').value = S.app.confusing || '';
  if (appFrame) return;
  appFrame = el('iframe', 'app-frame');
  appFrame.title = 'BridgeFinder app';
  appFrame.srcdoc = APP_DOC;
  $('#appHost').replaceChildren(appFrame);
}
function removeApp() { if (appFrame) { appFrame.remove(); appFrame = null; } }
window.addEventListener('message', event => {
  if (!appFrame || event.source !== appFrame.contentWindow) return;
  const data = event.data;
  if (!data || data.bf !== 'bridgefinder-app-event' || typeof data.type !== 'string' || S.app.events.length >= MAX_EVENTS) return;
  const detail = data.detail && typeof data.detail === 'object' ? data.detail : {};
  S.app.events.push({t: Math.round((Date.now() - S.app.start_ms) / 100) / 10, type: data.type.slice(0, 40), ...detail});
  save();
});
function appSummary() {
  if (!S.app.opened) return null;
  const events = S.app.events, has = type => events.some(e => e.type === type);
  const chose = has('researcher_chosen') || events.some(e => e.type === 'screen' && e.screen === 'network');
  const opened = events.filter(e => e.type === 'card_opened').length;
  return {seconds: S.app.end_ms ? Math.round((S.app.end_ms - S.app.start_ms) / 1000) : null, chose_researcher: chose,
    opened_card: opened > 0, opened_draft: has('draft_opened'), task_completed: chose && opened > 0 && has('draft_opened'),
    cards_opened: opened, explanation_opened: has('ranking_explanation_toggled'), confusing: S.app.confusing, events};
}

// ---------- results ----------
function payload() {
  return {schema_version: 1, study_protocol: PROTOCOL, collection_mode: 'self-guided-quick-html-v1', build_id: BUILD.build_id,
    dataset_id: DATASET_ID, participant_id: S.participant_id, seed_id: S.seed_id, set_id: S.set_id, shown: S.shown,
    ratings: S.shown.map(id => ({card_id: id, ...S.answers[id]})), contact_choice: S.contact,
    background: S.background, comment: S.comment, started_at: S.started_at, finished_at: S.finished_at,
    seconds: S.started_at && S.finished_at ? Math.round((Date.parse(S.finished_at) - Date.parse(S.started_at)) / 1000) : null,
    app: appSummary()};
}
function answersText() {
  return ['BridgeFinder study answers. Please send everything from BEGIN to END.',
    '-----BEGIN BRIDGEFINDER ANSWERS-----', JSON.stringify(payload()), '-----END BRIDGEFINDER ANSWERS-----'].join('\n');
}
function renderSend() { $('#comment').value = S.comment; $('#answersText').value = answersText(); $('#copyStatus').textContent = ''; }
async function copyAnswers() {
  S.comment = $('#comment').value.trim(); save();
  const box = $('#answersText'); box.value = answersText();
  let copied = false;
  try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(box.value); copied = true; } } catch { copied = false; }
  if (!copied) {
    const more = box.closest('details'); if (more) more.open = true;
    try { box.focus(); box.select(); copied = document.execCommand('copy'); } catch { copied = false; }
  }
  $('#copyStatus').textContent = copied ? 'Copied! Now paste it into your reply and send it.'
    : 'Your browser blocked copying. The text is selected below: press Ctrl+C (Cmd+C on a Mac), or download the file instead.';
}
function downloadAnswers() {
  S.comment = $('#comment').value.trim(); save();
  const url = URL.createObjectURL(new Blob([answersText()], {type: 'text/plain'}));
  const link = el('a'); link.href = url; link.download = `bridgefinder-answers-${S.participant_id.slice(0, 6)}.txt`;
  document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('#copyStatus').textContent = 'Downloaded. Attach the file to your reply.';
}

// ---------- events ----------
const next = {
  start() {
    S.background.field = $('#field').value.trim();
    if (!S.background.level) return error('start', 'Please choose what describes you.');
    if (!$('#consent').checked) return error('start', 'Please tick the box to agree.');
    S.started_at ||= new Date().toISOString();
    go('area');
  },
  rate() {
    if (answered() < S.shown.length) {
      const first = S.shown.find(id => !QUESTIONS.every(([key]) => typeof S.answers[id]?.[key] === 'boolean'));
      $(`[data-card-id="${first}"]`).scrollIntoView({block: 'center'});
      return error('rate', 'Please answer both questions for every person.');
    }
    if (!S.contact) return error('rate', 'Please pick the one person you would most like to contact, or "I wouldn\'t contact any of them".');
    S.finished_at = new Date().toISOString();
    go('send');
  },
  app() { S.app.end_ms = Date.now(); S.app.confusing = $('#appConfusing').value.trim(); go('send'); },
};
for (const button of $$('[data-next]')) button.addEventListener('click', () => next[button.dataset.next]());
$('#field').addEventListener('input', e => { S.background.field = e.target.value.trim(); save(); });
$('#comment').addEventListener('input', e => { S.comment = e.target.value.trim(); save(); $('#answersText').value = answersText(); });
$('#appConfusing').addEventListener('input', e => { S.app.confusing = e.target.value.trim(); save(); });
$('#clearContact').addEventListener('click', clearContact);
$('#copyAnswers').addEventListener('click', copyAnswers);
$('#downloadAnswers').addEventListener('click', downloadAnswers);
$('#openApp').addEventListener('click', () => go('app'));
$('#newSession').addEventListener('click', () => { if (confirm('Have you sent your answers? A new session deletes them from this browser.')) { clearSaved(); S = fresh(); go('start'); } });
$('#withdraw').addEventListener('click', () => { if (confirm('Stop and delete your answers from this browser?')) { clearSaved(); S = fresh(); go('start'); } });
if (['rate', 'send', 'app'].includes(S.step) && !(S.shown.length && S.shown.every(cardById))) S.step = S.started_at ? 'area' : 'start';
if (['send', 'app'].includes(S.step) && !S.finished_at) S.step = 'rate';
save();
render();
