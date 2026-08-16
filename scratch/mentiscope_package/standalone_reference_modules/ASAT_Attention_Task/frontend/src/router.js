/* =====================================================
   ASAT – Hash Router (SPA)
   ===================================================== */

const routes = {};
let currentCleanup = null;

/** Register a route */
export function route(path, handler) {
  routes[path] = handler;
}

/** Navigate to a hash route */
export function navigate(path) {
  window.location.hash = path;
}

/** Get current path from hash */
function currentPath() {
  return window.location.hash.slice(1) || '/';
}

/** Match a path against route patterns, extract params */
function matchRoute(path) {
  for (const [pattern, handler] of Object.entries(routes)) {
    const paramNames = [];
    const regexStr = pattern.replace(/:([^/]+)/g, (_, name) => {
      paramNames.push(name);
      return '([^/]+)';
    });
    const regex = new RegExp(`^${regexStr}$`);
    const m = path.match(regex);
    if (m) {
      const params = {};
      paramNames.forEach((name, i) => { params[name] = m[i + 1]; });
      return { handler, params };
    }
  }
  return null;
}

/** Render current route into #app */
function render() {
  const path = currentPath();
  const matched = matchRoute(path);
  const appEl = document.getElementById('app');

  // Run cleanup from previous page
  if (typeof currentCleanup === 'function') {
    currentCleanup();
    currentCleanup = null;
  }

  if (!matched) {
    appEl.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;gap:16px">
        <div style="font-size:64px">🔍</div>
        <h2>Page Not Found</h2>
        <p>The page you are looking for doesn't exist.</p>
        <a href="#/" class="btn btn-primary" style="margin-top:8px">← Go Home</a>
      </div>`;
    return;
  }

  const cleanup = matched.handler(appEl, matched.params);
  if (typeof cleanup === 'function') {
    currentCleanup = cleanup;
  }
}

/** Start the router */
export function startRouter() {
  window.addEventListener('hashchange', render);
  render();
}
