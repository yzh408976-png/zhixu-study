/**
 * GET /api/auth/me — 当前登录用户信息
 */
import { getSession } from '@/lib/auth';
import { ok, err } from '@/lib/api';

export async function GET() {
  const s = await getSession();
  if (!s) return err(401, '未登录', 'UNAUTHORIZED');
  return ok({ user: { id: s.sub, email: s.email, nickname: s.nickname } });
}