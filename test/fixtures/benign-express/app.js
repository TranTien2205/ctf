// Precision fixture: an ordinary Express app with NO web bug class present.
// If tools/classify.py scores any class above the noise threshold here, a
// signal in knowledge/bug-classes.json is too broad. Do not "fix" the test by
// raising the threshold -- tighten the signal instead.
const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.get('/greet', (req, res) => {
  const name = String(req.query.name || 'world');
  res.render('greet', { name });          // escaped by the template engine
});

app.listen(3000);
