/**
 * 每日任务计划 CRUD。管理：当前生成的当日 6 块式时表。
 * GET   /api/plans?date=YYYY-MM-DD     — 拉某日计划
 * POST  /api/plans                     — 写入某日计划（替换）
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Block = z.object({
  id: z.string(),
  type: z.string(),   // first-win / peak / retrieval / interleaving / spacing / cliffhanger
  subject: z.string(),
  duration: z.number(),
  title: z.string(),
  reason: z.string().optional()
});

const PlanSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  blocks: z.array(Block)
});

export async function GET(req: NextRequest) {
  try {
    const s = await requireSession();
    const date = req.nextUrl.searchParams.get('date');
    if (!date) return err(400, '缺少 date 参数', 'BAD_INPUT');
    const db = getDb();
    const row: any = db
      .prepare('SELECT blocks, generated FROM plans WHERE user_id = ? AND date = ?')
      .get(s.sub, date);
    if (!row) return ok({ plan: null });
    return ok({ plan: { date, blocks: JSON.parse(row.blocks), generated: row.generated } });
  } catch (e) {
    return handleError(e);
  }
}

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    const json = await req.json().catch(() => null);
    const parsed = PlanSchema.safeParse(json);
    if (!parsed.success) {
      return err(400, '计划格式错误', 'BAD_INPUT');
    }
    const db = getDb();
    db.prepare(`INSERT INTO plans (user_id, date, blocks) VALUES (?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET blocks = excluded.blocks, generated = datetime('now')`)
      .run(s.sub, parsed.data.date, JSON.stringify(parsed.data.blocks));
    return ok({ saved: parsed.data.blocks.length });
  } catch (e) {
    return handleError(e);
  }
}