/**
 * 数据库初始化脚本（手动执行一次即可）
 * 用法：npm run db:init
 *
 * 该脚本会调用 lib/db.ts 的迁移逻辑，
 * 生成 ./data/zhixu.db 文件并创建所有表。
 */

import { getDb, closeDb } from '../lib/db';

console.log('[init] connecting database...');
const instance = getDb();
const tables = instance
  .prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
  .all() as { name: string }[];

console.log('[init] 已创建表：');
for (const t of tables) console.log('  · ' + t.name);
console.log('[init] 数据库路径：', process.env.DATABASE_PATH || './data/zhixu.db');
console.log('[init] 完成');
closeDb();