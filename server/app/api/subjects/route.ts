/**
 * 学科档案 CRUD。管理：把前端 profile.subjects 同步到 SQLite。
 * GET    /api/subjects        — 列表
 * POST   /api/subjects        — 新增/批量替换（数组覆盖语义）
 * DELETE /api/subjects?id=xx  — 删除
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Subject = z.object({
  id: z.string().optional(),           // 客户端 uuid
  name: z.string().min(1).max(50),
  mastery: z.number().int().min(1).max(5),
  difficulty: z.number().int().min(1).max(5),
  interest: z.number().int().min(1).max(5),
  weight: z.number().int().min(1).max(80),
  examDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  category: z.string().max(30).optional()
});

const ListSchema = z.array(Subject);

export async function GET() {
  try {
    const s = await requireSession();
    const db = getDb();
    const rows = db
      .prepare('SELECT id, name, mastery, difficulty, interest, weight, exam_date, category FROM subjects WHERE user_id = ? ORDER BY id ASC')
      .all(s.sub) as any[];
    return ok({ subjects: rows.map((r) => ({
      ...r,
      examDate: r.exam_date,
      exam_date: undefined
    })) });
  } catch (e) {
    return handleError(e);
  }
}

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    const json = await req.json().catch(() => null);
    const parsed = ListSchema.safeParse(json);
    if (!parsed.success) {
      return err(400, '科目格式错误：' + parsed.error.errors[0]?.message, 'BAD_INPUT');
    }

    const db = getDb();
    const tx = db.transaction((userId: string, list: z.infer<typeof Subject>[]) => {
      // 覆盖语义——简单可靠：清空旧 + 插入新
      db.prepare('DELETE FROM subjects WHERE user_id = ?').run(userId);
      const ins = db.prepare(`INSERT INTO subjects (user_id, name, mastery, difficulty, interest, weight, exam_date, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
      for (const sub of list) {
        ins.run(userId, sub.name, sub.mastery, sub.difficulty, sub.interest, sub.weight, sub.examDate || null, sub.category || null);
      }
    });
    tx(s.sub, parsed.data);

    return ok({ saved: parsed.data.length });
  } catch (e) {
    return handleError(e);
  }
}