/**
 * 数据迁移工具：从 localStorage 备份文件导入到 SQLite。
 *
 * 用法：
 *   1. 用户在前端点击「导出」按钮，得到一个 JSON 文件
 *   2. 把这个文件放到 server/data/import.json
 *   3. 运行 npm run db:migrate -- --user=email@example.com
 *
 * 这是参赛答辩的加分项：旧用户数据无缝迁移到云端。
 */

import fs from 'node:fs';
import path from 'node:path';
import { getDb, closeDb } from '../lib/db';
import { hashPassword } from '../lib/auth';

async function main() {
  const email = (process.argv[2] || '').trim();
  if (!email) {
    console.error('用法：npm run db:migrate -- <email>');
    console.error('示例：npm run db:migrate -- user@example.com');
    process.exit(1);
  }

  const importPath = path.join(process.cwd(), 'data', 'import.json');
  if (!fs.existsSync(importPath)) {
    console.error('找不到 data/import.json。请先把前端导出的备份放到该路径。');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(importPath, 'utf8'));
  const db = getDb();

  // 1. 注册/获取用户
  const exists: any = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
  let userId: string;
  if (exists) {
    userId = String(exists.id);
    console.log('[migrate] 用户已存在，id=' + userId);
  } else {
    const tempPassword = 'changeme-' + Math.random().toString(36).slice(2, 8);
    const hash = await hashPassword(tempPassword);
    const info = db
      .prepare('INSERT INTO users (email, password_hash, nickname) VALUES (?, ?, ?)')
      .run(email, hash, data?.profile?.nickname || email.split('@')[0]);
    userId = String(info.lastInsertRowid);
    console.log('[migrate] 新用户已创建，id=' + userId + '，临时密码=' + tempPassword);
    console.log('[migrate] 请登录后立即修改密码！');
  }

  // 2. 导入 subjects
  if (Array.isArray(data.subjects)) {
    const ins = db.prepare(`INSERT INTO subjects (user_id, name, mastery, difficulty, interest, weight, exam_date, category)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
    db.transaction(() => {
      db.prepare('DELETE FROM subjects WHERE user_id = ?').run(userId);
      for (const s of data.subjects) {
        ins.run(userId, s.name, s.mastery || 3, s.difficulty || 3, s.interest || 3, s.weight || 25, s.examDate || null, s.category || null);
      }
    })();
    console.log(`[migrate] 导入 ${data.subjects.length} 个科目`);
  }

  // 3. 导入 plans / completions / moods / nodes
  if (data.plans && typeof data.plans === 'object') {
    const ins = db.prepare('INSERT OR REPLACE INTO plans (user_id, date, blocks, generated) VALUES (?, ?, ?, ?)');
    let n = 0;
    for (const [date, blocks] of Object.entries(data.plans)) {
      ins.run(userId, String(date), JSON.stringify(blocks), new Date().toISOString());
      n++;
    }
    console.log(`[migrate] 导入 ${n} 天的计划`);
  }

  if (data.completions && typeof data.completions === 'object') {
    const ins = db.prepare(`INSERT OR REPLACE INTO completions (user_id, date, block_id, subject, score, completed) VALUES (?, ?, ?, ?, ?, ?)`);
    let n = 0;
    for (const [date, items] of Object.entries(data.completions)) {
      for (const c of items as any[]) {
        ins.run(userId, String(date), c.block_id, c.subject || null, c.score ?? null, c.completed ?? 1);
        n++;
      }
    }
    console.log(`[migrate] 导入 ${n} 条完成记录`);
  }

  if (data.moods && typeof data.moods === 'object') {
    const ins = db.prepare(`INSERT OR REPLACE INTO moods (user_id, date, score, note) VALUES (?, ?, ?, ?)`);
    let n = 0;
    for (const [date, m] of Object.entries(data.moods)) {
      const mm = m as any;
      ins.run(userId, String(date), mm.score || 3, mm.note || null);
      n++;
    }
    console.log(`[migrate] 导入 ${n} 天情绪`);
  }

  if (Array.isArray(data.nodes)) {
    const ins = db.prepare('INSERT INTO nodes (user_id, subject, title, date, kind) VALUES (?, ?, ?, ?, ?)');
    let n = 0;
    for (const node of data.nodes) {
      ins.run(userId, node.subject, node.title, node.date, node.kind || 'reminder');
      n++;
    }
    console.log(`[migrate] 导入 ${n} 个考试节点`);
  }

  console.log('[migrate] 完成');
  closeDb();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});