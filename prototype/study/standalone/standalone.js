'use strict';
// Self-guided BridgeFinder study. CARDS, APP_DOC and BUILD are inlined by
// build_standalone.py. Card ratings and SUS use the same wording, scales and
// export fields as study.js (protocol student-interest-v1), so
// analyze_study.py accepts the result. Everything stays in this browser until
// the participant copies or downloads it.
const STORE = 'bridgefinder-selfguided-v1';
const STUDY_PROTOCOL = 'student-interest-v1';
const STEPS = ['welcome', 'about', 'interest', 'app', 'check', 'choose', 'cards', 'sus', 'feedback', 'send'];
const DATASET_ID = CARDS[0].dataset_id;
const DIMENSIONS = [
  ['relevance', '1. Relevance', "How relevant is this person's research to your stated research interest?", '1 = not relevant · 7 = very relevant'],
  ['novelty', '2. Novelty', 'How unfamiliar or unexpected is this research suggestion to you?', '1 = already familiar · 7 = new to me'],
  ['actionability', '3. Willingness to contact', 'Given the suggested route, how realistic would contacting this person feel?', '1 = not realistic · 7 = very realistic'],
];
const SUS_ITEMS = [
  'I think that I would like to use this system frequently.',
  'I found the system unnecessarily complex.',
  'I thought the system was easy to use.',
  'I think that I would need the support of a technical person to be able to use this system.',
  'I found the various functions in this system were well integrated.',
  'I thought there was too much inconsistency in this system.',
  'I would imagine that most people would learn to use this system very quickly.',
  'I found the system very cumbersome to use.',
  'I felt very confident using the system.',
  'I needed to learn a lot of things before I could get going with this system.',
];
const SUS_LABELS = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'];
const CORRECT = {
  solid_lines: 'The two people have published a paper together',
  dashed_lines: 'A suggested connection that does not exist yet',
  route_meaning: 'A chain of people who wrote papers together, linking the starting researcher to the suggested researcher',
};
const MAX_EVENTS = 250;

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const validRating = (value, max) => Number.isInteger(value) && value >= 1 && value <= max;
const text = (tag, className, content) => { const node = document.createElement(tag); if (className) node.className = className; if (content !== undefined) node.textContent = content; return node; };

function uuid() {
  if (crypto.randomUUID) return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
  const hex = [...bytes].map(value => value.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
function fresh() {
  return {v: 1, dataset_id: DATASET_ID, build: BUILD.build_id, step: 'welcome', participant_id: uuid(), started_at: null, finished_at: null,
    background: {}, research_interest: '', app: {start_ms: null, end_ms: null, events: []}, comprehension: {},
    seed_id: null, order: [], index: 0, responses: {}, sus: Array(10).fill(null), debrief: {}};
}
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE));
    if (saved && saved.v === 1 && saved.dataset_id === DATASET_ID && STEPS.includes(saved.step) && typeof saved.participant_id === 'string') return saved;
  } catch { /* storage blocked or corrupt */ }
  return null;
}
let S = load() || fresh();
let storageWorks = true;
function save() {
  try { localStorage.setItem(STORE, JSON.stringify(S)); storageWorks = true; }
  catch { storageWorks = false; }
  $('#saveNote').textContent = storageWorks ? '' : 'This browser cannot save progress. Keep this tab open until you have sent your answers.';
}
function clearSaved() { try { localStorage.removeItem(STORE); } catch { /* ignore */ } }

// ---------- generic widgets ----------
function radioGroup(container, name, options, current, onChange) {
  container.replaceChildren();
  options.forEach((option, index) => {
    const label = text('label', 'choice');
    const input = document.createElement('input');
    input.type = 'radio'; input.name = name; input.value = option; input.id = `${name}_${index}`;
    input.checked = current === option;
    input.addEventListener('change', () => onChange(option));
    label.append(input, text('span', '', option));
    container.append(label);
  });
}
function bindRadios(scope, store) {
  for (const container of $$(`[data-step="${scope}"] [data-radio]`)) {
    const key = container.dataset.radio;
    radioGroup(container, key, container.dataset.options.split('|'), store[key], value => { store[key] = value; save(); });
  }
}
function error(step, message) { const node = $(`[data-error="${step}"]`); if (node) node.textContent = message || ''; }

// ---------- navigation ----------
function go(step) {
  S.step = step; save(); render();
  const heading = $(`[data-step="${step}"] h1`);
  window.scrollTo(0, 0);
  if (heading) heading.focus({preventScroll: true});
}
function render() {
  for (const section of $$('[data-step]')) section.hidden = section.dataset.step !== S.step;
  const position = STEPS.indexOf(S.step);
  $('#stepBadge').textContent = S.step === 'cards' ? `Card ${S.index + 1} of ${S.order.length}` : `Step ${position + 1} of ${STEPS.length}`;
  document.body.classList.toggle('wide-step', S.step === 'app');
  for (const node of $$('[data-show="interest"]')) node.textContent = S.research_interest;
  $('#withdraw').hidden = S.step === 'welcome' || S.step === 'send';
  ({welcome: renderWelcome, about: renderAbout, interest: renderInterest, app: renderApp, check: renderCheck,
    choose: renderChoose, cards: renderCard, sus: renderSus, feedback: renderFeedback, send: renderSend})[S.step]();
  if (S.step !== 'app') removeApp();
}

function renderWelcome() { $('#consent').checked = Boolean(S.started_at); }
function renderAbout() { bindRadios('about', S.background); $('#field').value = S.background.field || ''; }
function renderInterest() { $('#interest').value = S.research_interest; }
function renderCheck() {
  bindRadios('check', S.comprehension);
  $('#routeNames').value = S.comprehension.route_names || '';
  $('#stuck').value = S.comprehension.stuck || '';
}
function renderFeedback() {
  for (const key of ['confusing', 'contact', 'trust', 'change', 'use']) $(`#fb_${key}`).value = S.debrief[key] || '';
}

// ---------- embedded app ----------
let appFrame = null;
function renderApp() {
  if (!S.app.start_ms) { S.app.start_ms = Date.now(); save(); }
  if (appFrame) return;
  appFrame = document.createElement('iframe');
  appFrame.title = 'BridgeFinder app';
  appFrame.className = 'app-frame';
  appFrame.srcdoc = APP_DOC;
  $('#appHost').replaceChildren(appFrame);
}
function removeApp() { if (appFrame) { appFrame.remove(); appFrame = null; } }
window.addEventListener('message', event => {
  if (!appFrame || event.source !== appFrame.contentWindow) return;
  const data = event.data;
  if (!data || data.bf !== 'bridgefinder-app-event' || typeof data.type !== 'string') return;
  if (S.step !== 'app' || S.app.events.length >= MAX_EVENTS) return;
  const detail = data.detail && typeof data.detail === 'object' ? data.detail : {};
  S.app.events.push({t: Math.round((Date.now() - S.app.start_ms) / 100) / 10, type: data.type.slice(0, 40), ...detail});
  save();
});
function appSummary() {
  const events = S.app.events, has = type => events.some(event => event.type === type);
  const opened = events.filter(event => event.type === 'card_opened');
  const chose = has('researcher_chosen') || events.some(event => event.type === 'screen' && event.screen === 'network');
  return {
    seconds: S.app.start_ms && S.app.end_ms ? Math.round((S.app.end_ms - S.app.start_ms) / 1000) : null,
    chose_researcher: chose, opened_card: opened.length > 0, opened_draft: has('draft_opened'),
    task_completed: chose && opened.length > 0 && has('draft_opened'),
    cards_opened: opened.length,
    researchers_explored: [...new Set(events.filter(event => event.type === 'screen' && event.screen === 'network').map(event => event.seed))].length,
    explanation_opened: has('ranking_explanation_toggled'), searches: events.filter(event => event.type === 'search').length,
    map_lines_clicked: events.filter(event => event.type === 'map_line_clicked').length,
    events_truncated: events.length >= MAX_EVENTS,
  };
}

// ---------- card ratings ----------
const seeds = [...new Map(CARDS.map(card => [card.seed_id, card])).values()];
function renderChoose() {
  const container = $('#seedChoices');
  container.replaceChildren();
  for (const seed of seeds) {
    const label = text('label', 'choice seed-choice');
    const input = document.createElement('input');
    input.type = 'radio'; input.name = 'seed'; input.value = seed.seed_id; input.checked = S.seed_id === seed.seed_id;
    input.addEventListener('change', () => { error('choose'); });
    const body = text('span');
    body.append(text('strong', '', seed.seed_name), text('small', '', seed.seed_topics.join(' · ')));
    label.append(input, body);
    container.append(label);
  }
}
function startRating() {
  const chosen = $('input[name="seed"]:checked');
  if (!chosen) return error('choose', 'Please choose a starting researcher.');
  if (chosen.value !== S.seed_id || !S.order.length) {
    S.seed_id = chosen.value; S.responses = {}; S.index = 0;
    const order = CARDS.filter(card => card.seed_id === S.seed_id).map(card => card.card_id);
    for (let i = order.length - 1; i > 0; i--) {
      const j = Math.floor(crypto.getRandomValues(new Uint32Array(1))[0] / 4294967296 * (i + 1));
      [order[i], order[j]] = [order[j], order[i]];
    }
    S.order = order;
  }
  go('cards');
}
const cardById = id => CARDS.find(card => card.card_id === id);
function renderCard() {
  const card = cardById(S.order[S.index]);
  error('cards');
  $('#seedName').textContent = card.seed_name;
  $('#seedMeta').textContent = `${card.seed_department} · ${card.seed_topics.join(' · ')}`;
  $('#candidateName').textContent = card.candidate_name;
  $('#candTopics').replaceChildren(...card.candidate_topics.map(topic => text('span', 'topic-tag', topic)));
  $('#samplePapers').replaceChildren(...(card.sample_papers.length ? card.sample_papers : ['No example publications available.']).map(title => text('li', '', title)));
  $('#introPath').textContent = card.introduction_path;
  const scales = $('#scales');
  scales.replaceChildren();
  for (const [key, legend, question, help] of DIMENSIONS) {
    const fieldset = text('fieldset');
    fieldset.append(text('legend', '', legend), text('p', '', question));
    const row = text('div', 'likert-scale');
    for (let value = 1; value <= 7; value++) {
      const label = text('label', 'likert-option');
      const input = document.createElement('input');
      input.type = 'radio'; input.name = key; input.value = value; input.setAttribute('aria-label', `${key} ${value}`);
      input.checked = S.responses[card.card_id]?.[key] === value;
      input.addEventListener('change', () => { (S.responses[card.card_id] ??= {})[key] = value; error('cards'); save(); });
      label.append(input, text('span', '', String(value)));
      row.append(label);
    }
    fieldset.append(row, text('p', 'scale-help', help));
    scales.append(fieldset);
  }
  $('#prevCard').disabled = S.index === 0;
  $('#nextCard').textContent = S.index === S.order.length - 1 ? 'Continue' : 'Next card';
  $('#stepBadge').textContent = `Card ${S.index + 1} of ${S.order.length}`;
}
function cardComplete(id) { return DIMENSIONS.every(([key]) => validRating(S.responses[id]?.[key], 7)); }

// ---------- SUS ----------
function renderSus() {
  const list = $('#susList');
  list.replaceChildren();
  SUS_ITEMS.forEach((item, index) => {
    const fieldset = text('fieldset', 'sus-item');
    fieldset.append(text('legend', '', `${index + 1}. ${item}`));
    const row = text('div', 'sus-scale');
    SUS_LABELS.forEach((label, offset) => {
      const value = offset + 1, option = text('label', 'likert-option');
      const input = document.createElement('input');
      input.type = 'radio'; input.name = `sus${index}`; input.value = value; input.checked = S.sus[index] === value;
      input.setAttribute('aria-label', `${label} (${value})`);
      input.addEventListener('change', () => { S.sus[index] = value; error('sus'); save(); });
      option.append(input, text('span', '', label));
      row.append(option);
    });
    fieldset.append(row);
    list.append(fieldset);
  });
}

// ---------- results ----------
function payload() {
  const comprehension = {...S.comprehension};
  for (const key of Object.keys(CORRECT)) comprehension[`${key}_correct`] = comprehension[key] ? comprehension[key] === CORRECT[key] : null;
  return {
    schema_version: 1, study_protocol: STUDY_PROTOCOL, collection_mode: 'self-guided-html-v1', build_id: BUILD.build_id,
    dataset_id: DATASET_ID, participant_id: S.participant_id, research_interest: S.research_interest, seed_id: S.seed_id,
    sus: [...S.sus], ratings: S.order.map(id => ({card_id: id, ...S.responses[id]})),
    started_at: S.started_at, finished_at: S.finished_at, background: S.background,
    app: {...appSummary(), events: S.app.events}, comprehension, debrief: S.debrief,
  };
}
function answersText() {
  return ['BridgeFinder study answers. Please send everything from BEGIN to END.',
    '-----BEGIN BRIDGEFINDER ANSWERS-----', JSON.stringify(payload()), '-----END BRIDGEFINDER ANSWERS-----'].join('\n');
}
function renderSend() {
  $('#answersText').value = answersText();
  $('#participantCode').textContent = `P-${S.participant_id.slice(0, 6).toUpperCase()}`;
  $('#copyStatus').textContent = '';
}
async function copyAnswers() {
  const box = $('#answersText');
  let copied = false;
  try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(box.value); copied = true; } } catch { copied = false; }
  if (!copied) {
    try { box.focus(); box.select(); copied = document.execCommand('copy'); } catch { copied = false; }
  }
  $('#copyStatus').textContent = copied
    ? 'Copied. Now paste it into your reply and send it.'
    : 'Your browser blocked copying. The text below is selected: press Ctrl+C (or Cmd+C on a Mac), or download the file instead.';
  if (!copied) { box.focus(); box.select(); }
}
function downloadAnswers() {
  const url = URL.createObjectURL(new Blob([answersText()], {type: 'text/plain'}));
  const link = document.createElement('a');
  link.href = url; link.download = `bridgefinder-answers-${S.participant_id.slice(0, 6)}.txt`;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('#copyStatus').textContent = 'Downloaded. Attach the file to your reply.';
}

// ---------- step handlers ----------
const next = {
  welcome() {
    if (!$('#consent').checked) return error('welcome', 'Please tick the box to agree before starting.');
    S.started_at ||= new Date().toISOString();
    go('about');
  },
  about() {
    S.background.field = $('#field').value.trim();
    if (!S.background.level || !S.background.seeking || !S.background.tried_before || !S.background.field) return error('about', 'Please answer all four questions.');
    go('interest');
  },
  interest() {
    const value = $('#interest').value.trim();
    if (!value) return error('interest', 'Please write a research interest before continuing.');
    S.research_interest = value.slice(0, 500);
    go('app');
  },
  app() { S.app.end_ms = Date.now(); go('check'); },
  check() {
    S.comprehension.route_names = $('#routeNames').value.trim();
    S.comprehension.stuck = $('#stuck').value.trim();
    if (!S.comprehension.solid_lines || !S.comprehension.dashed_lines || !S.comprehension.route_meaning) return error('check', 'Please answer questions 1 to 3. "I\'m not sure" is fine.');
    go('choose');
  },
  choose: startRating,
  sus() {
    if (!S.sus.every(value => validRating(value, 5))) return error('sus', 'Please answer all ten statements.');
    go('feedback');
  },
  feedback() {
    for (const key of ['confusing', 'contact', 'trust', 'change', 'use']) S.debrief[key] = $(`#fb_${key}`).value.trim();
    S.finished_at ||= new Date().toISOString();
    go('send');
  },
};
for (const button of $$('[data-next]')) button.addEventListener('click', () => next[button.dataset.next]());
for (const button of $$('[data-back]')) button.addEventListener('click', () => go(STEPS[STEPS.indexOf(button.dataset.back) - 1]));
$('#nextCard').addEventListener('click', () => {
  if (!cardComplete(S.order[S.index])) return error('cards', 'Please answer all three ratings before continuing.');
  if (S.index === S.order.length - 1) return go('sus');
  S.index += 1; save(); renderCard(); window.scrollTo(0, 0); $('#candidateName').focus({preventScroll: true});
});
$('#prevCard').addEventListener('click', () => { if (S.index > 0) { S.index -= 1; save(); renderCard(); window.scrollTo(0, 0); } });
for (const [id, key] of [['#routeNames', 'route_names'], ['#stuck', 'stuck']]) $(id).addEventListener('input', event => { S.comprehension[key] = event.target.value.trim(); save(); });
for (const key of ['confusing', 'contact', 'trust', 'change', 'use']) $(`#fb_${key}`).addEventListener('input', event => { S.debrief[key] = event.target.value.trim(); save(); });
$('#interest').addEventListener('input', event => { S.research_interest = event.target.value.trim().slice(0, 500); save(); });
$('#field').addEventListener('input', event => { S.background.field = event.target.value.trim(); save(); });
$('#copyAnswers').addEventListener('click', copyAnswers);
$('#downloadAnswers').addEventListener('click', downloadAnswers);
$('#newSession').addEventListener('click', () => {
  if (!confirm('Have you sent your answers? Starting a new session deletes them from this browser.')) return;
  clearSaved(); S = fresh(); go('welcome');
});
$('#withdraw').addEventListener('click', () => {
  if (!confirm('Stop the study and delete your answers from this browser?')) return;
  clearSaved(); S = fresh(); go('welcome');
});
// A reload during the cards step must never skip unanswered cards.
if (S.step === 'cards') {
  if (!S.order.length || !S.order.every(cardById)) S.step = 'choose';
  else { const first = S.order.findIndex(id => !cardComplete(id)); if (first !== -1 && first < S.index) S.index = first; }
}
if (['sus', 'feedback', 'send'].includes(S.step) && !(S.order.length && S.order.every(cardComplete))) S.step = 'choose';
save();
render();
