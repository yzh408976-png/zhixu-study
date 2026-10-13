/**
 * 完成记录 — 任务块完成情况
 * GET   /api/completions?from=YYYY-MM-DD&to=YYYY-MM-DD
 * POST  /api/completions   — 标记完成（幂等：同一天同一块只算一次）
 * DELETE /api/completions?date=YYYY-MM-DD  — 取消今日所有完成（重新做）
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Body = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  block_id: z.string(),
  subject: z.string().optional(),
  score: z.number().int().min(0).max(100).optional(),
  completed: z.boolean().default(true)
});

export async function GET(req: NextRequest) {
  try {
    const s = await requireSession();
    const from = req.nextUrl.searchParams.get('from');
    const to = req.nextUrl.searchParams.get('to');
    if (!from || !to) return err(400, '需要 from 和 to 参数', 'BAD_INPUT');
    const db = getDb();
    const rows = db
      .prepare(`SELECT date, block_id, subject, score, completed, completed_at
                FROM completions WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date ASC, completed_at ASC`)
      .all(s.sub, from, to) as any[];
    return ok({ completions: rows });
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

    if (parsed.data.completed) {
      db.prepare(`INSERT INTO completions (user_id, date, block_id, subject, score)
                  VALUES (?, ?, ?, ?, ?)
                  ON CONFLICT(user_id, date, block_id) DO UPDATE SET
                    score = excluded.score,
                    completed_at = datetime('now')`)
        .run(s.sub, parsed.data.date, parsed.data.block_id, parsed.data.subject || null, parsed.data.score ?? null);
      // 更新 streak
      const today = parsed.data.date;
      const cur: any = db.prepare('SELECT last_date, n FROM streak WHERE user_id = ?').get(s.sub);
      let nextN = 1;
      if (cur) {
        if (cur.last_date === today) {
          nextN = cur.n;
        } else {
          const prev = new Date(cur.last_date);
          const now = new Date(today);
          const diff = Math.round((+now - +prev) / 86400000);
          nextN = diff === 1 ? cur.n + 1 : 1;
        }
      }
      db.prepare(`INSERT INTO streak (user_id, last_date, n, updated_at) VALUES (?, ?, ?, datetime('now'))
                  ON CONFLICT(user_id) DO UPDATE SET last_date = excluded.last_date, n = excluded.n, updated_at = datetime('now')`)
        .run(s.sub, today, nextN);
    } else {
      // 撤销完成
      db.prepare('DELETE FROM completions WHERE user_id = ? AND date = ? AND block_id = ?')
        .run(s.sub, parsed.data.date, parsed.data.block_id);
    }
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const s = await requireSession();
    const date = req.nextUrl.searchParams.get('date');
    if (!date) return err(400, '缺少 date 参数', 'BAD_INPUT');
    const db = getDb();
    db.prepare('DELETE FROM completions WHERE user_id = ? AND date = ?').run(s.sub, date);
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}