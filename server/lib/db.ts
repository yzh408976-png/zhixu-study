/**
 * SQLite 数据层
 *
 * 为什么选 better-sqlite3：
 *  1. 同步 API，对 Node.js serverless 友好
 *  2. 性能最快（C++ 实现）
 *  3. 文件即数据库，无需独立进程
 *  4. 部署到云时，可替换为 libSQL/Turso（同一协议）
 *
 * 生产部署建议：
 *  - 单机小流量直接用文件
 *  - 多副本或高并发时，把 DB_PATH 换成云数据库 URL，
 *    实现统一接口即可（Prisma/Drizzle 适配层）
 */

import Database from 'better-sqlite3';
import path from 'node:path';
import fs from 'node:fs';

let _db: Database.Database | null = null;

/**
 * 获取数据库实例。第一次调用会建表、迁移。
 */
export function getDb(): Database.Database {
  if (_db) return _db;

  const dbPath = process.env.DATABASE_PATH || path.join(process.cwd(), 'data', 'zhixu.db');
  const dir = path.dirname(dbPath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const instance = new Database(dbPath);
  instance.pragma('journal_mode = WAL');     // 写并发更稳
  instance.pragma('synchronous = NORMAL');  // 写入性能 / 安全性折中
  instance.pragma('foreign_keys = ON');

  migrate(instance);
  _db = instance;
  return instance;
}

/**
 * 初始化表结构。版本号写在 user_version pragma 里。
 * 每次 schema 变化加一个 ALTER/CREATE 分支。
 */
function migrate(db: Database.Database) {
  // 当前 schema 版本（首次部署 = 1）
  const cur = (db.pragma('user_version', { simple: true }) as number) || 0;

  if (cur < 1) {
    db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        email         TEXT    UNIQUE NOT NULL,
        password_hash TEXT    NOT NULL,
        nickname      TEXT    NOT NULL,
        created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
        last_login_at TEXT
      );

      CREATE TABLE IF NOT EXISTS profiles (
        user_id      TEXT         PRIMARY KEY,  -- 与 session sub 对齐
        payload      TEXT         NOT NULL,    -- JSON
        updated_at   TEXT         NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS subjects (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT    NOT NULL,
        name        TEXT    NOT NULL,
        mastery     INTEGER NOT NULL DEFAULT 3,
        difficulty  INTEGER NOT NULL DEFAULT 3,
        interest    INTEGER NOT NULL DEFAULT 3,
        weight      INTEGER NOT NULL DEFAULT 25,
        exam_date   TEXT,
        category    TEXT,
        payload     TEXT,
        updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
      );
      CREATE INDEX IF NOT EXISTS idx_subjects_user ON subjects(user_id);

      CREATE TABLE IF NOT EXISTS plans (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT    NOT NULL,
        date       TEXT    NOT NULL,   -- YYYY-MM-DD
        blocks     JSONB,             -- 任务块数组
        generated  TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, date)
      );
      CREATE INDEX IF NOT EXISTS idx_plans_user_date ON plans(user_id, date);

      CREATE TABLE IF NOT EXISTS completions (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT    NOT NULL,
        date       TEXT    NOT NULL,
        block_id   TEXT    NOT NULL,
        subject    TEXT,
        score      INTEGER,
        completed  INTEGER NOT NULL DEFAULT 1,
        completed_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, date, block_id)
      );
      CREATE INDEX IF NOT EXISTS idx_completions_user_date ON completions(user_id, date);

      CREATE TABLE IF NOT EXISTS moods (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT    NOT NULL,
        date       TEXT    NOT NULL,   -- YYYY-MM-DD
        score      INTEGER NOT NULL,   -- 1-5
        note       TEXT,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, date)
      );
      CREATE INDEX IF NOT EXISTS idx_moods_user_date ON moods(user_id, date);

      CREATE TABLE IF NOT EXISTS nodes (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT    NOT NULL,
        subject    TEXT    NOT NULL,
        title      TEXT    NOT NULL,
        date       TEXT    NOT NULL,   -- YYYY-MM-DD
        kind       TEXT    NOT NULL DEFAULT 'reminder',
        done       INTEGER NOT NULL DEFAULT 0,
        created_at TEXT    NOT NULL DEFAULT (datetime('now'))
      );
      CREATE INDEX IF NOT EXISTS idx_nodes_user_date ON nodes(user_id, date);

      CREATE TABLE IF NOT EXISTS streaks (
        user_id    TEXT PRIMARY KEY,
        last_date  TEXT,
        n          INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS preferences (
        user_id    TEXT PRIMARY KEY,
        big_font    INTEGER NOT NULL DEFAULT 0,
        payload     TEXT,
        updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
      );
    `);
    db.pragma('user_version = 1');
  }
}

/**
 * 关闭数据库（用于脚本退出时）。
 */
export function closeDb() {
  if (_db) {
    _db.close();
    _db = null;
  }
}