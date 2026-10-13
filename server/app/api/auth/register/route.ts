/**
 * POST /api/auth/register
 * Body: { email, password, nickname }
 * 成功：201 + httpOnly cookie + 用户基本信息
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { hashPassword, buildAuthCookie, signToken } from '@/lib/auth';
import { ok, err, handleError } from '@/lib/api';

const Body = z.object({
  email: z.string().email('邮箱格式不正确').max(100),
  password: z.string().min(6, '密码至少 6 位').max(100),
  nickname: z.string().min(1, '昵称不能为空').max(20)
});

export async function POST(req: NextRequest) {
  try {
    const json = await req.json().catch(() => ({}));
    const parsed = Body.safeParse(json);
    if (!parsed.success) {
      return err(400, parsed.error.errors[0]?.message || '参数错误', 'BAD_INPUT');
    }
    const { email, password, nickname } = parsed.data;

    const db = getDb();
    const exists = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (exists) {
      return err(409, '该邮箱已注册，请直接登录', 'EMAIL_EXISTS');
    }

    const hash = await hashPassword(password);
    const info = db
      .prepare('INSERT INTO users (email, password_hash, nickname) VALUES (?, ?, ?)')
      .run(email.toLowerCase(), hash, nickname);

    const userId = String(info.lastInsertRowid);
    const token = await signToken({ sub: userId, email, nickname });

    return ok(
      { user: { id: userId, email, nickname } },
      { status: 201, headers: { 'Set-Cookie': buildAuthCookie(token) } }
    );
  } catch (e) {
    return handleError(e);
  }
}