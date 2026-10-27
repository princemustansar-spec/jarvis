import json
import sqlite3
import threading
from pathlib import Path

class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, data TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, data TEXT NOT NULL);
        ''')
        self.db.commit()

    def add(self, kind, data):
        with self.lock:
            c = self.db.execute('INSERT INTO records(kind,data) VALUES (?,?)', (kind, json.dumps(data)))
            self.db.commit()
            return c.lastrowid

    def list(self, kind, limit=100):
        with self.lock:
            rows = self.db.execute('SELECT * FROM records WHERE kind=? ORDER BY id DESC LIMIT ?', (kind, limit)).fetchall()
            return [dict(id=r['id'], created=r['created'], **json.loads(r['data'])) for r in rows]

    def update(self, kind, ident, data):
        with self.lock:
            c = self.db.execute('UPDATE records SET data=? WHERE id=? AND kind=?', (json.dumps(data), ident, kind))
            self.db.commit()
            return c.rowcount

    def delete(self, kind, ident):
        with self.lock:
            self.db.execute('DELETE FROM records WHERE id=? AND kind=?', (ident, kind))
            self.db.commit()

    def get(self, key, default=None):
        with self.lock:
            row = self.db.execute('SELECT data FROM settings WHERE key=?', (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set(self, key, value):
        with self.lock:
            self.db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, json.dumps(value)))
            self.db.commit()

    def deliver_reminder(self, ident):
        """Atomically persist notification and delivered state across crashes."""
        with self.lock:
            row = self.db.execute('SELECT data FROM records WHERE id=? AND kind=?', (ident, 'reminder')).fetchone()
            if not row:
                return False
            data = json.loads(row[0])
            if data['done']:
                return False
            data['done'] = True
            try:
                self.db.execute('INSERT INTO records(kind,data) VALUES (?,?)', ('notification', json.dumps(dict(text='Reminder: ' + data['title']))))
                self.db.execute('UPDATE records SET data=? WHERE id=? AND kind=?', (json.dumps(data), ident, 'reminder'))
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return True
