/**
 * 用户偏好 — 大字模式、主题等
 * GET    /api/profile/preferences
 * POST   /api/profile/preferences   — 覆盖更新
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Pref = z.object({
  big_font: z.boolean(),
  payload: z.record(z.any()).optional()
});

export async function GET() {
  try {
    const s = await requireSession();
    const db = getDb();
    const row: any = db
      .prepare('SELECT big_font, payload FROM preferences WHERE user_id = ?')
      .get(s.sub);
    if (!row) return ok({ preferences: { big_font: false } });
    return ok({
      preferences: {
        big_font: !!row.big_font,
        payload: row.payload ? JSON.parse(row.payload) : {}
      }
    });
  } catch (e) {
    return handleError(e);
  }
}

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    const json = await req.json().catch(() => null);
    const parsed = Pref.safeParse(json);
    if (!parsed.success) return err(400, '参数错误', 'BAD_INPUT');
    const db = getDb();
    db.prepare(`INSERT INTO preferences (user_id, big_font, payload) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET big_font = excluded.big_font, payload = excluded.payload, updated_at = datetime('now')`)
      .run(s.sub, parsed.data.big_font ? 1 : 0, JSON.stringify(parsed.data.payload || {}));
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}