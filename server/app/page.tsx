import { redirect } from 'next/navigation';

export default function Home() {
  // 单文件前端继续保留在 /app，前端路由优先
  redirect('/app');
}