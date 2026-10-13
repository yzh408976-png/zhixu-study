/**
 * POST /api/auth/login
 * Body: { email, password }
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { verifyPassword, signToken, buildAuthCookie } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Body = z.object({
  email: z.string().email('邮箱格式不正确'),
  password: z.string().min(1, '密码不能为空')
});

export async function POST(req: NextRequest) {
  try {
    const json = await req.json().catch(() => ({}));
    const parsed = Body.safeParse(json);
    if (!parsed.success) {
      return err(400, parsed.error.errors[0]?.message || '参数错误', 'BAD_INPUT');
    }
    const { email, password } = parsed.data;

    const db = getDb();
    const row: any = db
      .prepare('SELECT id, email, nickname, password_hash FROM users WHERE email = ?')
      .get(email.toLowerCase());
    if (!row) {
      return err(401, '邮箱或密码错误', 'INVALID_CRED');
    }
    const okPass = await verifyPassword(password, row.password_hash);
    if (!okPass) {
      return err(401, '邮箱或密码错误', 'INVALID_CRED');
    }

    db.prepare("UPDATE users SET last_login_at = datetime('now') WHERE id = ?").run(row.id);

    const token = await signToken({ sub: String(row.id), email: row.email, nickname: row.nickname });
    return ok(
      { user: { id: row.id, email: row.email, nickname: row.nickname } },
      { headers: { 'Set-Cookie': buildAuthCookie(token) } }
    );
  } catch (e) {
    return handleError(e);
  }
}