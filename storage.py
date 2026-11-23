"""Small local SQLite store for prototype users and generated audio."""
import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('ARIRANG_DATA_DIR', str(BASE / '.arirang_data')))
DB = DATA / 'arirang.sqlite3'


def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    cn = sqlite3.connect(DB, timeout=20)
    cn.execute('PRAGMA foreign_keys = ON')
    cn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, salt BLOB NOT NULL, pw_hash BLOB NOT NULL, created TEXT NOT NULL)')
    cn.execute('CREATE TABLE IF NOT EXISTS tracks (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL, prompt TEXT NOT NULL, lyrics TEXT NOT NULL, audio BLOB NOT NULL, created TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)')
    cn.commit()
    return cn


def register(username, password):
    username = username.strip().lower()
    if not re.fullmatch(r'[a-z0-9_]{3,24}', username):
        return False, '아이디는 영문 소문자·숫자·밑줄 3~24자로 입력해 주세요.'
    if len(password) < 8 or len(password) > 128:
        return False, '비밀번호는 8~128자로 설정해 주세요.'
    salt = secrets.token_bytes(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf8'), salt, 300_000)
    with connect() as cn:
        try:
            cn.execute('INSERT INTO users (username,salt,pw_hash,created) VALUES (?,?,?,?)', (username, salt, pw_hash, datetime.now(timezone.utc).isoformat()))
        except sqlite3.IntegrityError:
            return False, '이미 사용 중인 아이디입니다.'
    return True, '회원가입 완료! 로그인해 주세요.'


def authenticate(username, password):
    with connect() as cn:
        row = cn.execute('SELECT id,salt,pw_hash FROM users WHERE username=?', (username.strip().lower(),)).fetchone()
    if row is None:
        return None
    value = hashlib.pbkdf2_hmac('sha256', password.encode('utf8'), row[1], 300_000)
    return row[0] if hmac.compare_digest(value, row[2]) else None


def save_track(user_id, title, prompt, lyrics, audio):
    if not audio or len(audio) > 40 * 1024 * 1024:
        raise ValueError('저장할 음원이 없거나 40MB를 초과했습니다.')
    with connect() as cn:
        cur = cn.execute('INSERT INTO tracks(user_id,title,prompt,lyrics,audio,created) VALUES(?,?,?,?,?,?)', (user_id, title[:100], prompt, lyrics, sqlite3.Binary(audio), datetime.now(timezone.utc).isoformat(timespec='seconds')))
        return cur.lastrowid


def list_tracks(user_id):
    with connect() as cn:
        return cn.execute('SELECT id,title,created,length(audio) FROM tracks WHERE user_id=? ORDER BY id DESC', (user_id,)).fetchall()


def get_track(user_id, track_id):
    with connect() as cn:
        return cn.execute('SELECT id,title,prompt,lyrics,audio,created FROM tracks WHERE user_id=? AND id=?', (user_id, track_id)).fetchone()


def delete_track(user_id, track_id):
    with connect() as cn:
        cn.execute('DELETE FROM tracks WHERE user_id=? AND id=?', (user_id, track_id))
