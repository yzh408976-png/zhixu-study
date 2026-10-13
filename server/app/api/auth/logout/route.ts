/**
 * POST /api/auth/logout — 注销登录
 */
import { NextResponse } from 'next/server';
import { buildLogoutCookie } from '@/lib/auth';
import { ok } from '@/lib/api';

export async function POST() {
  return ok({ logged_out: true }, { headers: { 'Set-Cookie': buildLogoutCookie() } });
}