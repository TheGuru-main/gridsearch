const express = require('express');
const cors = require('cors');
const { calculate_lsum, calculate_ssum, first_letter_index, gsp_place, elasticCloud } = require('./gsp');
const { findTopic } = require('./knowledge');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// In‑memory message store (replace with Wizard DB later)
const messages = {};

// ── Search endpoint ────────────────────────────────
app.get('/api/search', (req, res) => {
  const q = (req.query.q || '').trim();
  if (!q) return res.json({ error: 'Missing query' });

  const topic = findTopic(q);
  if (!topic) return res.json({ error: 'Topic not found' });

  const L = calculate_lsum(topic.title);
  const S = calculate_ssum(topic.title);
  const c = first_letter_index(topic.title);
  const gsp = gsp_place(L, S, c);
  const cloud = elasticCloud(L, S, c, 1, 1);

  res.json({
    ...topic,
    Lsum: L,
    Ssum: S,
    first_letter_index: c,
    gsp,
    elastic_cloud_size: cloud.length
  });
});

// ── Dictionary proxy ───────────────────────────────
app.get('/api/dictionary', async (req, res) => {
  const q = req.query.q;
  if (!q) return res.json({ error: 'Missing query' });
  try {
    const fetch = (await import('node-fetch')).default;
    const resp = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(q)}`);
    const data = await resp.json();
    const def = data[0]?.meanings?.[0]?.definitions?.[0]?.definition;
    res.json({ definition: def || 'No definition found' });
  } catch (e) {
    res.json({ error: 'Failed to fetch definition' });
  }
});

// ── News placeholder ────────────────────────────────
app.get('/api/news', (req, res) => {
  res.json({ articles: [] });
});

// ── Messaging API ───────────────────────────────────
app.post('/api/messages/send', (req, res) => {
  const { from, to, text } = req.body;
  if (!from || !to || !text) return res.status(400).json({ error: 'Missing fields' });
  if (!messages[to]) messages[to] = [];
  messages[to].push({ from, text, timestamp: Date.now() });
  res.json({ success: true });
});

app.get('/api/messages/inbox/:user', (req, res) => {
  const user = req.params.user;
  res.json({ messages: messages[user] || [] });
});

// ── Start server ────────────────────────────────────
const listener = app.listen(process.env.PORT || 3000, () => {
  console.log('Gridsearch running on port ' + listener.address().port);
});