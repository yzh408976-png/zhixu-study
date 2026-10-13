/**
 * Next.js 配置
 *
 * ⚠️ 重要 — exFAT 兼容补丁
 * 本机工作区位于 exFAT 格式的移动硬盘（E:）。exFAT 不支持符号链接，
 * 且其 readlink 对普通文件返回 EISDIR（而非标准的 EINVAL），
 * 会让 webpack 的 symlink 解析崩溃（报错：EISDIR: illegal operation on a directory, readlink）。
 * 下面的补丁把 EISDIR 归一化为 EINVAL，webpack 即可正常工作。
 * 部署到 Linux/云服务器（ext4 / overlayfs）时该补丁不生效也无害。
 */
import fs from 'node:fs';

function normalizeReadlinkError(e) {
  if (e && e.code === 'EISDIR') {
    const err = new Error('EINVAL: invalid argument, readlink');
    err.code = 'EINVAL';
    err.errno = -4071;
    err.syscall = 'readlink';
    return err;
  }
  return e;
}

const _readlinkSync = fs.readlinkSync;
fs.readlinkSync = function (...args) {
  try { return _readlinkSync.apply(fs, args); }
  catch (e) { throw normalizeReadlinkError(e); }
};

const _readlink = fs.readlink;
fs.readlink = function (...args) {
  const cb = args[args.length - 1];
  if (typeof cb === 'function') {
    const rest = args.slice(0, -1);
    return _readlink.call(fs, ...rest, (e, link) => cb(normalizeReadlinkError(e), link));
  }
  return _readlink.apply(fs, args);
};

const _readlinkPromise = fs.promises && fs.promises.readlink ? fs.promises.readlink.bind(fs.promises) : null;
if (fs.promises && _readlinkPromise) {
  fs.promises.readlink = async function (...args) {
    try { return await _readlinkPromise(...args); }
    catch (e) { throw normalizeReadlinkError(e); }
  };
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',  // Docker 部署需要
  // better-sqlite3 是原生模块，需要作为外部依赖处理
  experimental: {
    serverComponentsExternalPackages: ['better-sqlite3', 'bcryptjs']
  },
  // 旧版单文件应用通过 /app 访问
  async rewrites() {
    return [
      { source: '/app', destination: '/index.html' }
    ];
  },
  // exFAT 兼容：关闭 webpack 的符号链接解析，避免 readlink 崩溃
  webpack: (config) => {
    config.resolve = config.resolve || {};
    config.resolve.symlinks = false;
    return config;
  }
};

export default nextConfig;