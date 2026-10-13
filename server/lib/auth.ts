/**
 * 认证工具：JWT 签发/校验、密码哈希、Session 解析。
 *
 * 使用 jose（Edge runtime 友好）替代 jsonwebtoken，避免依赖加密算法补丁。
 * Cookie 设置为 HttpOnly + SameSite=Lax，XSS 风险最小化。
 */

import { SignJWT, jwtVerify } from 'jose';
import bcrypt from 'bcryptjs';
import { cookies } from 'next/headers';
import { NextRequest } from 'next/server';

const COOKIE_NAME = 'zhixu_session';
const TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30; // 30 天

function getSecret(): Uint8Array {
  const raw = process.env.JWT_SECRET || 'dev-only-secret-please-change-in-production-32chars';
  if (raw.length < 32) {
    console.warn('[auth] JWT_SECRET 长度过短，生产环境建议 32+ 字符');
  }
  return new TextEncoder().encode(raw);
}

export interface SessionPayload {
  /** 用户表 id（base64 字符串） */
  sub: string;
  /** 邮箱 */
  email: string;
  /** 昵称 */
  nickname: string;
}

/**
 * 生成 JWT。
 */
export async function signToken(payload: SessionPayload): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  return await new SignJWT({ ...payload })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt(now)
    .setExpirationTime(now + TOKEN_TTL_SECONDS)
    .setIssuer('zhixu-study')
    .sign(getSecret());
}

/**
 * 校验并解码 JWT。
 */
export async function verifyToken(token: string): Promise<SessionPayload | null> {
  try {
    const { payload } = await jwtVerify(token, getSecret(), { issuer: 'zhixu-study' });
    if (typeof payload.sub !== 'string') return null;
    return {
      sub: payload.sub,
      email: payload.email as string,
      nickname: payload.nickname as string
    };
  } catch {
    return null;
  }
}

/**
 * 密码哈希。
 */
export async function hashPassword(plain: string): Promise<string> {
  return bcrypt.hash(plain, 10);
}

/**
 * 密码校验。
 */
export async function verifyPassword(plain: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plain, hash);
}

/**
 * 从 NextRequest 读取 cookie 拿到当前用户。
 */
export async function getSessionFromRequest(req: NextRequest): Promise<SessionPayload | null> {
  const token = req.cookies.get(COOKIE_NAME)?.value;
  if (!token) return null;
  return verifyToken(token);
}

/**
 * 从 cookies() 拿到当前用户（App Router 内）。
 */
export async function getSession(): Promise<SessionPayload | null> {
  const token = cookies().get(COOKIE_NAME)?.value;
  if (!token) return null;
  return verifyToken(token);
}

/**
 * 设置登录 cookie。
 */
export function buildAuthCookie(token: string): string {
  const maxAge = TOKEN_TTL_SECONDS;
  return [
    `${COOKIE_NAME}=${token}`,
    `Max-Age=${maxAge}`,
    'Path=/',
    'HttpOnly',
    'SameSite=Lax'
  ].join('; ');
}

/**
 * 注销 cookie。
 */
export function buildLogoutCookie(): string {
  return [`${COOKIE_NAME}=`, 'Max-Age=0', 'Path=/', 'HttpOnly', 'SameSite=Lax'].join('; ');
}

/**
 * 在 API 路由中要求已登录。失败抛出 401。
 */
export async function requireSession(): Promise<SessionPayload> {
  const s = await getSession();
  if (!s) {
    const err: any = new Error('unauthorized');
    err.status = 401;
    throw err;
  }
  return s;
}