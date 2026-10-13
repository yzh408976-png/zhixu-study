/**
 * 情绪打卡 — 民生核心模块
 * GET   /api/moods?from=&to=    — 区间情绪记录
 * POST  /api/moods              — 打卡 / 更新（一天一次）
 *
 * 心理守卫相关逻辑在前端实现：低分关怀、4-7-8 呼吸、12355 转介。
 * 后端只做数据持久化，让隐私最敏感的情绪数据由用户自己掌控。
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Body = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  score: z.number().int().min(1).max(5),
  note: z.string().max(500).optional()
});

export async function GET(req: NextRequest) {
  try {
    const s = await requireSession();
    const from = req.nextUrl.searchParams.get('from');
    const to = req.nextUrl.searchParams.get('to');
    if (!from || !to) return err(400, '需要 from 和 to 参数', 'BAD_INPUT');
    const db = getDb();
    const rows = db
      .prepare(`SELECT date, score, note, created_at FROM moods WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC`)
      .all(s.sub, from, to) as any[];
    return ok({ moods: rows });
  } catch (e) {
    return handleError(e);
  }
}

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    const json = await req.json().catch(() => null);
    const parsed = Body.safeParse(json);
    if (!parsed.success) return err(400, '参数错误', 'BAD_INPUT');
    const db = getDb();
    db.prepare(`INSERT INTO moods (user_id, date, score, note) VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET score = excluded.score, note = excluded.note, created_at = datetime('now')`)
      .run(s.sub, parsed.data.date, parsed.data.score, parsed.data.note || null);
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}