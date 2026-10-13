// 全局布局：根路径被 redirect 到 /app（单文件前端）
// 单文件前端有自己的样式，不需要 React 服务端渲染。
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}