// 把仓库根目录的前端源文件同步到两个发布目录：
//   1. server/public/       —— Next.js 使用的副本
//   2. dist/                —— 纯静态托管（GitHub Pages / Qoder Sites 等）的一键发布目录
// 根目录是唯一事实来源，靠本脚本保证所有副本永远一致。
// 跨平台（Windows / macOS / Linux 均可），无需依赖 shell 的 cp 命令。
import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const serverRoot = resolve(here, '..');
const repoRoot = resolve(serverRoot, '..');
const targets = [
  resolve(serverRoot, 'public'),
  resolve(repoRoot, 'dist'),
];

const files = ['index.html', 'api-client.js'];
for (const dir of targets) {
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  for (const f of files) {
    const src = resolve(repoRoot, f);
    if (!existsSync(src)) {
      console.error(`[sync] 源文件不存在，已跳过：${src}`);
      continue;
    }
    copyFileSync(src, resolve(dir, f));
    console.log(`[sync] ${f}  ->  ${dir.replace(repoRoot, '.')}/${f}`);
  }
}
console.log('[sync] 前端文件同步完成（server/public + dist）');
