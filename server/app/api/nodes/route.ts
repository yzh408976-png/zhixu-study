/**
 * 考试节点（民生信息管家）
 * GET   /api/nodes?from=&to=   — 区间节点
 * POST  /api/nodes             — 新增节点
 * DELETE /api/nodes?id=        — 删除节点
 * PATCH /api/nodes?id=         — 标记完成 / 取消完成
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const KINDS = ['register', 'confirm', 'ticket', 'exam', 'reminder', 'other'] as const;
const NewNode = z.object({
  subject: z.string().min(1).max(50),
  title: z.string().min(1).max(80),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  kind: z.enum(KINDS).default('reminder')
});

export async function GET(req: NextRequest) {
  try {
    const s = await requireSession();
    const from = req.nextUrl.searchParams.get('from');
    const to = req.nextUrl.searchParams.get('to');
    if (!from || !to) return err(400, '需要 from 和 to 参数', 'BAD_INPUT');
    const db = getDb();
    const rows = db
      .prepare(`SELECT id, subject, title, date, kind, done FROM nodes
                WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC`)
      .all(s.sub, from, to) as any[];
    return ok({ nodes: rows });
  } catch (e) {
    return handleError(e);
  }
}

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    const json = await req.json().catch(() => null);
    const parsed = NewNode.safeParse(json);
    if (!parsed.success) return err(400, '节点格式错误：' + parsed.error.errors[0]?.message, 'BAD_INPUT');
    const db = getDb();
    const info = db
      .prepare(`INSERT INTO nodes (user_id, subject, title, date, kind) VALUES (?, ?, ?, ?, ?)`)
      .run(s.sub, parsed.data.subject, parsed.data.title, parsed.data.date, parsed.data.kind);
    return ok({ id: Number(info.lastInsertRowid) }, { status: 201 });
  } catch (e) {
    return handleError(e);
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const s = await requireSession();
    const id = Number(req.nextUrl.searchParams.get('id'));
    if (!id) return err(400, '缺少 id', 'BAD_INPUT');
    const db = getDb();
    db.prepare('DELETE FROM nodes WHERE id = ? AND user_id = ?').run(id, s.sub);
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}

export async function PATCH(req: NextRequest) {
  try {
    const s = await requireSession();
    const id = Number(req.nextUrl.searchParams.get('id'));
    if (!id) return err(400, '缺少 id', 'BAD_INPUT');
    const body = await req.json().catch(() => ({}));
    const done = body?.done === true ? 1 : 0;
    const db = getDb();
    db.prepare('UPDATE nodes SET done = ? WHERE id = ? AND user_id = ?').run(done, id, s.sub);
    return ok({ ok: true });
  } catch (e) {
    return handleError(e);
  }
}