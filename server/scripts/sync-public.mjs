// 把仓库根目录的前端源文件同步到 server/public/。
// 根目录是唯一事实来源（同时是 GitHub Pages 的部署目录），
// server/public/ 只是给 Next.js 用的副本，靠本脚本保证两者永远一致。
// 跨平台（Windows / macOS / Linux 均可），无需依赖 shell 的 cp 命令。
import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const serverRoot = resolve(here, '..');
const repoRoot = resolve(serverRoot, '..');
const publicDir = resolve(serverRoot, 'public');

if (!existsSync(publicDir)) mkdirSync(publicDir, { recursive: true });

const files = ['index.html', 'api-client.js'];
for (const f of files) {
  const src = resolve(repoRoot, f);
  const dest = resolve(publicDir, f);
  if (!existsSync(src)) {
    console.error(`[sync] 源文件不存在，已跳过：${src}`);
    continue;
  }
  copyFileSync(src, dest);
  console.log(`[sync] ${f}  ->  server/public/${f}`);
}
console.log('[sync] 前端文件同步完成');
