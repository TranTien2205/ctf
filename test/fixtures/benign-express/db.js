// Parameterised queries only: no interpolation reaches SQL.
const sqlite = require('sqlite-async');

async function findUser(db, username) {
  return db.get('SELECT id, username FROM users WHERE username = ?', username);
}

async function addUser(db, username, hash) {
  return db.run('INSERT INTO users (username, password) VALUES (?, ?)', username, hash);
}

module.exports = { findUser, addUser };
