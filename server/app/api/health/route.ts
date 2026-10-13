/**
 * 健康检查 — 用于部署平台探活
 * GET /api/health → { ok: true, version, uptime, time }
 */
export async function GET() {
  return Response.json({
    ok: true,
    service: 'zhixu-study',
    version: '2.0.0',
    uptime_seconds: Math.round(process.uptime()),
    time: new Date().toISOString()
  });
}