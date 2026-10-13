/**
 * 通用响应助手 + 错误处理。
 */

import { NextResponse } from 'next/server';

export function ok<T>(data: T, init?: ResponseInit) {
  return NextResponse.json({ ok: true, data }, init);
}

export function err(status: number, message: string, code?: string) {
  return NextResponse.json({ ok: false, error: { message, code } }, { status });
}

/**
 * 统一错误兜底。处理已知错误码（status）和其他抛错。
 */
export function handleError(e: unknown) {
  if (e && typeof e === 'object' && 'status' in e) {
    const status = (e as any).status || 500;
    const message = (e as any).message || 'error';
    return err(status, message);
  }
  console.error('[api] unexpected', e);
  return err(500, '服务器内部错误');
}

/**
 * 简单 in-memory 限流器：每用户每分钟 60 次。
 *
 * 生产建议换成 Redis；本项目作为单机演示够用。
 */
const _buckets = new Map<string, { n: number; resetAt: number }>();
export function rateLimit(userId: string, limit = 60, windowMs = 60_000): boolean {
  const now = Date.now();
  const b = _buckets.get(userId);
  if (!b || now > b.resetAt) {
    _buckets.set(userId, { n: 1, resetAt: now + windowMs });
    return true;
  }
  b.n += 1;
  if (b.n > limit) return false;
  return true;
}