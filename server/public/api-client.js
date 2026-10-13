/**
 * 云帆 · 云适配客户端（v2.0）
 * 用法：在 index.html 顶部引入本文件
 *   <script src="/api-client.js"></script>
 *
 * 工作模式（自动降级，永不崩溃）：
 *   1. 启动时尝试 /api/auth/me 拿到登录态
 *   2. 已登录 → 数据双写（localStorage + 后端）
 *   3. 未登录 → 纯 localStorage（与旧版本完全兼容）
 *
 * 提供的全局对象：window.ZhixuCloud
 *   - ZhixuCloud.user        当前登录用户（null 表示匿名）
 *   - ZhixuCloud.login(...)  登录
 *   - ZhixuCloud.register(...) 注册
 *   - ZhixuCloud.logout()    注销
 *   - ZhixuCloud.save(...)   写入云端（best-effort）
 *   - ZhixuCloud.fetch(...)  从云端读取
 *   - ZhixuCloud.migrate()   把当前 localStorage 同步到云端
 */

(function () {
  if (window.ZhixuCloud) return;

  var BASE = '';  // 与前端同源，相对路径
  var COOKIE_USER = 'zhixu_user_cache';  // 轻量缓存当前用户

  var state = {
    user: null,
    ready: false,
    pending: []   // 离线时排队，恢复后批量发送
  };

  function readCache() {
    try {
      var raw = localStorage.getItem(COOKIE_USER);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }
  function writeCache(u) {
    try {
      if (u) localStorage.setItem(COOKIE_USER, JSON.stringify(u));
      else localStorage.removeItem(COOKIE_USER);
    } catch (e) {}
  }

  /**
   * 通用请求包装。会自动带 cookie、错误处理。
   */
  function request(path, opts) {
    opts = opts || {};
    var init = {
      method: opts.method || 'GET',
      credentials: 'include',
      headers: Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {})
    };
    if (opts.body !== undefined) init.body = JSON.stringify(opts.body);
    return fetch(BASE + path, init).then(function (r) {
      if (!r.ok) {
        return r.json().catch(function () { return { ok: false }; }).then(function (j) {
          var err = new Error((j && j.error && j.error.message) || ('HTTP ' + r.status));
          err.status = r.status;
          err.body = j;
          throw err;
        });
      }
      return r.json();
    });
  }

  /**
   * 静态托管检测（GitHub Pages / Gitee Pages / 本地 file:// 直开）。
   * 这些环境没有后端，直接进入匿名模式，避免无谓的 404 请求。
   */
  function isStaticHosting() {
    try {
      var h = location.hostname || '';
      return /\.github\.io$/i.test(h) || /\.gitee\.io$/i.test(h) || location.protocol === 'file:';
    } catch (e) { return false; }
  }

  /**
   * 启动时调用一次，确认是否已登录。
   */
  function bootstrap() {
    if (isStaticHosting()) {
      // 纯静态托管：无后端可用，跳过探测，直接匿名模式
      state.ready = true;
      setTimeout(function () {
        document.dispatchEvent(new CustomEvent('zhixu:cloud-ready', { detail: { user: null } }));
      }, 0);
      return Promise.resolve();
    }
    return request('/api/auth/me')
      .then(function (j) {
        if (j && j.ok && j.data && j.data.user) {
          state.user = j.data.user;
          writeCache(j.data.user);
        }
      })
      .catch(function () {
        // 401 或网络错误：当匿名处理
      })
      .then(function () {
        state.ready = true;
        // 恢复离线期间积攒的请求
        flushPending();
        document.dispatchEvent(new CustomEvent('zhixu:cloud-ready', { detail: { user: state.user } }));
      });
  }

  function flushPending() {
    if (!state.user || !state.pending.length) return;
    var queue = state.pending.slice();
    state.pending = [];
    queue.forEach(function (p) { p.resolve(); });
  }

  /**
   * 保存数据到云端。失败时降级到本地、排队等待。
   * 资源语义与 REST API 对齐：
   *     save('subjects', list)            → POST /api/subjects
   *     save('plan', { date, blocks })    → POST /api/plans
   *     save('completion', {...})         → POST /api/completions
   *     save('mood', { date, score, note }) → POST /api/moods
   *     save('node', { subject, title, date, kind }) → POST /api/nodes
   *     save('nodeDone', { id, done })    → PATCH /api/nodes?id=
   *     delete('node', id)                → DELETE /api/nodes?id=
   *     save('preferences', payload)      → POST /api/profile/preferences
   */
  function save(kind, payload) {
    if (!state.ready) {
      // 启动期请求全部排队，等就绪后批量放行
      return new Promise(function (resolve) {
        state.pending.push({ kind: kind, payload: payload, resolve: resolve });
      }).then(function () { return save(kind, payload); });
    }
    if (!state.user) return Promise.resolve(null);  // 匿名：纯本地模式
    var p, m;
    switch (kind) {
      case 'subjects':       p = '/api/subjects';      m = 'POST'; break;
      case 'plan':           p = '/api/plans';         m = 'POST'; break;
      case 'completion':     p = '/api/completions';   m = 'POST'; break;
      case 'mood':           p = '/api/moods';         m = 'POST'; break;
      case 'node':           p = '/api/nodes';         m = 'POST'; break;
      case 'nodeDone':       p = '/api/nodes?id=' + encodeURIComponent(payload.id); m = 'PATCH'; break;
      case 'preferences':    p = '/api/profile/preferences'; m = 'POST'; break;
      default: return Promise.reject(new Error('unknown kind: ' + kind));
    }
    return request(p, { method: m, body: payload }).catch(function (e) {
      console.warn('[cloud] ' + kind + ' 失败，已降级本地存储', e.message);
      return null;
    });
  }

  function remove(kind, id) {
    if (!state.user) return Promise.resolve(null);
    if (kind === 'node') return request('/api/nodes?id=' + encodeURIComponent(id), { method: 'DELETE' });
    return Promise.reject(new Error('unknown remove: ' + kind));
  }

  /**
   * 从云端拉取资源列表。
   *   fetch('subjects')    → list
   *   fetch('moods', { from, to })
   *   fetch('plans', { date })
   *   fetch('preferences')
   */
  function fetch_(kind, params) {
    if (!state.user) return Promise.resolve(null);
    params = params || {};
    var qs = Object.keys(params).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
    }).join('&');
    var url;
    switch (kind) {
      case 'subjects':    url = '/api/subjects'; break;
      case 'moods':       url = '/api/moods' + (qs ? '?' + qs : ''); break;
      case 'plans':       url = '/api/plans' + (qs ? '?' + qs : ''); break;
      case 'completions': url = '/api/completions' + (qs ? '?' + qs : ''); break;
      case 'nodes':       url = '/api/nodes' + (qs ? '?' + qs : ''); break;
      case 'preferences': url = '/api/profile/preferences'; break;
      default: return Promise.reject(new Error('unknown kind: ' + kind));
    }
    return request(url).then(function (j) { return (j && j.ok) ? j.data : null; });
  }

  /**
   * 把当前 localStorage 全部数据迁移到云端。
   * 老用户升级时一次性调用。
   */
  function migrate() {
    if (!state.user) return Promise.reject(new Error('not logged in'));
    try {
      var raw = localStorage.getItem('zhixu_v1');
      if (!raw) return Promise.reject(new Error('本地无数据'));
      var data = JSON.parse(raw);
      var ops = [];
      if (Array.isArray(data.subjects) && data.subjects.length) {
        ops.push(save('subjects', data.subjects));
      }
      if (data.moods && typeof data.moods === 'object') {
        Object.keys(data.moods).forEach(function (date) {
          var mm = data.moods[date];
          ops.push(save('mood', { date: date, score: mm.score || 3, note: mm.note || '' }));
        });
      }
      if (Array.isArray(data.nodes)) {
        data.nodes.forEach(function (n) {
          ops.push(save('node', { subject: n.subject, title: n.title, date: n.date, kind: n.kind || 'reminder' }));
        });
      }
      if (data.completions && typeof data.completions === 'object') {
        Object.keys(data.completions).forEach(function (date) {
          (data.completions[date] || []).forEach(function (c) {
            ops.push(save('completion', {
              date: date, block_id: c.block_id || c.block || '', subject: c.subject, score: c.score, completed: c.completed !== false
            }));
          });
        });
      }
      return Promise.all(ops).then(function () { return { migrated: ops.length }; });
    } catch (e) {
      return Promise.reject(e);
    }
  }

  /**
   * 登录。成功后会触发 'cloud-ready' 自定义事件。
   */
  function login(email, password) {
    return request('/api/auth/login', { method: 'POST', body: { email: email, password: password } })
      .then(function (j) {
        state.user = j.data.user;
        writeCache(j.data.user);
        document.dispatchEvent(new CustomEvent('zhixu:cloud-ready', { detail: { user: state.user } }));
        return j.data.user;
      });
  }

  /**
   * 注册。
   */
  function register(email, password, nickname) {
    return request('/api/auth/register', { method: 'POST', body: { email: email, password: password, nickname: nickname } })
      .then(function (j) {
        state.user = j.data.user;
        writeCache(j.data.user);
        document.dispatchEvent(new CustomEvent('zhixu:cloud-ready', { detail: { user: state.user } }));
        return j.data.user;
      });
  }

  /**
   * 注销。
   */
  function logout() {
    return request('/api/auth/logout', { method: 'POST' }).finally(function () {
      state.user = null;
      writeCache(null);
      document.dispatchEvent(new CustomEvent('zhixu:cloud-ready', { detail: { user: null } }));
    });
  }

  // 立即异步启动，事件派发由使用方监听 zhixu:cloud-ready
  bootstrap();

  window.ZhixuCloud = {
    get user() { return state.user; },
    get ready() { return state.ready; },
    /** 是否运行在无后端的静态托管环境（GitHub Pages 等） */
    get isStatic() { return isStaticHosting(); },
    login: login,
    register: register,
    logout: logout,
    save: save,
    fetch: fetch_,
    remove: remove,
    migrate: migrate
  };
})();