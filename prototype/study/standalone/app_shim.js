// Runs inside the embedded app before d3 and app.js. The page is opened from a
// file or a static host, so data.json is served from memory, and history
// updates that a file:// or srcdoc document refuses are ignored.
(() => {
  'use strict';
  const realFetch = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = (input, init) => {
    const url = String(input && input.url ? input.url : input);
    if (/(^|\/)data\.json(\?|#|$)/.test(url)) {
      return Promise.resolve(new Response(JSON.stringify(window.__BF_DATA__), {status: 200, headers: {'Content-Type': 'application/json'}}));
    }
    if (!realFetch) return Promise.reject(new Error('fetch unavailable'));
    return realFetch(input, init);
  };
  for (const name of ['pushState', 'replaceState']) {
    const original = history[name].bind(history);
    history[name] = (...args) => { try { return original(...args); } catch { return undefined; } };
  }
})();
