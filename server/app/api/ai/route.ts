/**
 * AI 教练 — 平台代理端点
 *
 * 为什么做这个：参赛叙事里我们说"开箱即用、不要让用户去申请 API Key"。
 * 这个路由是占位实现——开启 AI_PROXY_ENABLED 后，平台用内置的 Key 调用大模型。
 *
 * 安全考虑：
 *  - 限流（每用户每分钟 20 次）
 *  - 仅暴露给登录用户
 *  - 不持久化用户原始 prompt（隐私）
 *  - 默认关闭，配置好密钥后再启用
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getDb } from '@/lib/db';
import { requireSession } from '@/lib/auth';
import { ok, err, handleError, rateLimit } from '@/lib/api';

const Body = z.object({
  task: z.enum(['diagnose', 'review', 'explain', 'breathe']),
  input: z.string().max(2000)
});

export async function POST(req: NextRequest) {
  try {
    const s = await requireSession();
    if (!rateLimit(s.sub, 20)) return err(429, '调用太频繁，请稍后再试', 'RATE_LIMIT');

    const json = await req.json().catch(() => null);
    const parsed = Body.safeParse(json);
    if (!parsed.success) return err(400, '参数错误', 'BAD_INPUT');

    if (process.env.AI_PROXY_ENABLED !== 'true') {
      return err(503,
        'AI 平台代理尚未启用。请在 AI 教练页填入你自己的 API Key（DeepSeek 免费额度足够日常使用）。',
        'AI_DISABLED');
    }

    // 下面是占位实现。开启 AI_PROXY_ENABLED 后填入对应厂商 SDK：
    //   DeepSeek:    https://api.deepseek.com/v1/chat/completions
    //   OpenAI:      https://api.openai.com/v1/chat/completions
    //   通义千问:    https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
    //
    // 实现思路：fetch 端点 + 流式返回，组装 messages 提示词 + 任务模板。
    // 任务模板保存在 lib/prompts.ts。

    const db = getDb();
    db.prepare(`INSERT INTO moods (user_id, date, score, note) VALUES (?, '', 0, ?)`).run(s.sub, `ai:${parsed.data.task}`); // 简化埋点

    return ok({
      placeholder: true,
      task: parsed.data.task,
      hint: 'AI 代理已启用占位：请在 lib/prompts.ts 配置提示词模板并实现对应厂商 SDK 调用。'
    });
  } catch (e) {
    return handleError(e);
  }
}