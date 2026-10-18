// Test-Attrappe für window.claude: db (im Speicher), user, downloads. Spiegelt die Verträge aus db.d.ts.
(() => {
  const store = new Map(); // path -> data
  const subs = [];
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const parent = (p) => p.split('/').slice(0, -1).join('/');
  const notify = () => subs.forEach((s) => s());
  const snapDoc = (p) => { const has = store.has(p); return { id: p.split('/').pop(), exists: has, data: () => (has ? clone(store.get(p)) : undefined), metadata: { fromCache: false, hasPendingWrites: false } }; };
  const colDocs = (c) => [...store.keys()].filter((k) => parent(k) === c).sort().map(snapDoc);
  const mk = () => Math.random().toString(36).slice(2, 12);
  const db = {
    log: [],
    doc(path) {
      return { id: path.split('/').pop(), path,
        get: async () => snapDoc(path),
        set: async (d) => { db.log.push(['set', path]); store.set(path, clone(d)); notify(); },
        update: async (d) => { if (!store.has(path)) throw { code: 'invalid_argument', message: 'Dokument existiert nicht' }; db.log.push(['update', path]); const o = store.get(path); const m = (a, b) => { for (const k in b) a[k] = b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object' ? m(a[k], b[k]) : clone(b[k]); return a; }; store.set(path, m(o, clone(d))); notify(); },
        delete: async () => { db.log.push(['delete', path]); store.delete(path); notify(); },
        onSnapshot(next) { const f = () => next(snapDoc(path)); subs.push(f); setTimeout(f, 0); return () => { const i = subs.indexOf(f); if (i >= 0) subs.splice(i, 1); }; },
        collection: (c) => db.collection(path + '/' + c) };
    },
    collection(path) {
      const q = { path,
        doc: (id) => db.doc(path + '/' + (id || mk())),
        add: async (d) => { const r = db.doc(path + '/' + mk()); await r.set(d); return r; },
        get: async () => { const docs = colDocs(path); return { docs, size: docs.length, empty: !docs.length }; },
        onSnapshot(next) { const f = () => { const docs = colDocs(path); next({ docs, size: docs.length, empty: !docs.length, docChanges: () => [] }); }; subs.push(f); setTimeout(f, 0); return () => { const i = subs.indexOf(f); if (i >= 0) subs.splice(i, 1); }; } };
      return q;
    },
    _dump: () => Object.fromEntries(store), _seed: (o) => { for (const k in o) store.set(k, clone(o[k])); notify(); },
  };
  const downloads = { saved: [], save: async (r) => { downloads.saved.push({ filename: r.filename, data: r.data instanceof Uint8Array ? Array.from(r.data) : r.data }); return { status: 'saved' }; } };
  const user = { isOwner: async () => true, canEdit: async () => true, can: async () => (window.__QA_RO__ ? false : true), me: async () => ({ id: 'u_test', name: 'Tester' }), id: async () => 'u_test' };
  const comments = { canSendToClaude: async () => (window.__QA_NOSESSION__ ? 'no_session' : 'available'), anchorFor: async () => ({ fake: true }), sendToClaude: async (t) => { (window.__sent = window.__sent || []).push(t); return { threadId: 'th1', commentId: 'c1' }; } };
  const caps = { db, user, downloads, comments };
  window.__db = db; window.__downloads = downloads;
  window.claude = { use: async (n) => (n === 'db' && window.__QA_NODB__ ? null : caps[n] || null) };
})();
