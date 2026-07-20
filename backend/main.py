"""
main.py — FastAPI Application Entry Point
==========================================

Responsibilities:
  1.  Create & configure the FastAPI application instance.
  2.  Register CORS middleware so the React frontend (localhost:5173)
      can communicate with this API during development.
  3.  Include routers / sub-applications (added as the project grows).
  4.  Expose a health-check endpoint for quick liveness verification.
  5.  Serve the embedded admin panel (HTML) for reviewing scraped data.

Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routes.admin import router as admin_router
from routes.discovery import router as discovery_router
from routes.schools import router as schools_router

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Central Course Guide API",
    description=(
        "RESTful API powering the Central Course Guide — helping new "
        "tertiary students explore schools, programmes, subjects, and "
        "career paths."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------
# During development the React dev server runs on localhost:5173.
# In production, replace / extend this list with your actual domain(s).
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Origins permitted to call the API
    allow_credentials=True,          # Allow cookies / auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST …)
    allow_headers=["*"],             # Allow all headers
)

# ---------------------------------------------------------------------------
# Register API routers
# ---------------------------------------------------------------------------
app.include_router(schools_router)
app.include_router(discovery_router)
app.include_router(admin_router)

# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def root():
    """
    Root health-check endpoint.

    Returns a simple JSON payload confirming the API is running.
    """
    return {
        "status": "healthy",
        "service": "Central Course Guide API",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Dedicated health-check route — useful for container orchestrators,
    load balancers, and uptime monitors.
    """
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Embedded Admin Panel UI
# ---------------------------------------------------------------------------
# A single-page admin interface served directly from FastAPI.
# No separate build step needed — just visit http://localhost:8000/admin-panel
# ---------------------------------------------------------------------------

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin Panel — Central Course Guide</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    :root {
      --maroon: #8B0000;
      --maroon-dark: #5C0000;
      --maroon-light: #A52A2A;
      --bg: #F8F5F2;
      --surface: #FFFFFF;
      --surface-alt: #F0EBE3;
      --text: #1A1A2E;
      --text-sec: #4A4A68;
      --text-muted: #8A8AA0;
      --accent: #D4A853;
      --green: #16a34a;
      --green-bg: #dcfce7;
      --amber: #d97706;
      --amber-bg: #fef3c7;
      --red: #dc2626;
      --red-bg: #fee2e2;
      --radius: 12px;
      --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg); color: var(--text);
      min-height: 100vh;
    }
    /* --- Header --- */
    .header {
      background: var(--surface);
      border-bottom: 1px solid var(--surface-alt);
      padding: 16px 32px;
      display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 50;
      backdrop-filter: blur(12px);
    }
    .header h1 {
      font-size: 20px; font-weight: 800;
    }
    .header h1 span { color: var(--maroon); }
    .header-actions { display: flex; gap: 10px; }
    /* --- Stats Cards --- */
    .stats {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px; padding: 24px 32px;
    }
    .stat-card {
      background: var(--surface); border-radius: var(--radius);
      padding: 20px 24px; box-shadow: var(--shadow);
      border: 1px solid var(--surface-alt);
    }
    .stat-card .label { font-size: 13px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-card .value { font-size: 32px; font-weight: 800; margin-top: 4px; color: var(--text); }
    .stat-card.maroon .value { color: var(--maroon); }
    .stat-card.green .value { color: var(--green); }
    .stat-card.amber .value { color: var(--amber); }
    /* --- Controls --- */
    .controls {
      padding: 0 32px 16px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    }
    select, .btn {
      font-family: inherit; font-size: 14px; padding: 10px 16px;
      border-radius: 8px; border: 1px solid var(--surface-alt);
      background: var(--surface); cursor: pointer; transition: all 0.15s;
    }
    select:focus, .btn:focus { outline: none; box-shadow: 0 0 0 3px rgba(139,0,0,0.15); }
    .btn { font-weight: 600; }
    .btn-primary { background: var(--maroon); color: #fff; border-color: var(--maroon); }
    .btn-primary:hover { background: var(--maroon-dark); }
    .btn-success { background: var(--green); color: #fff; border-color: var(--green); }
    .btn-success:hover { opacity: 0.9; }
    .btn-danger { background: var(--red); color: #fff; border-color: var(--red); }
    .btn-danger:hover { opacity: 0.9; }
    .btn-ghost { background: transparent; border-color: var(--surface-alt); color: var(--text-sec); }
    .btn-ghost:hover { background: var(--surface-alt); }
    .btn-sm { padding: 6px 12px; font-size: 12px; border-radius: 6px; }
    /* --- Table --- */
    .table-wrap {
      padding: 0 32px 32px; overflow-x: auto;
    }
    table {
      width: 100%; border-collapse: collapse; background: var(--surface);
      border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow);
    }
    th {
      text-align: left; padding: 12px 16px; font-size: 12px;
      text-transform: uppercase; letter-spacing: 0.05em;
      color: var(--text-muted); font-weight: 600;
      background: var(--surface); border-bottom: 2px solid var(--surface-alt);
    }
    td {
      padding: 14px 16px; font-size: 14px; border-bottom: 1px solid var(--surface-alt);
      vertical-align: middle;
    }
    tr:hover td { background: #fafaf8; }
    .badge {
      display: inline-flex; padding: 3px 10px; border-radius: 20px;
      font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;
    }
    .badge-reviewed { background: var(--green-bg); color: var(--green); }
    .badge-pending { background: var(--amber-bg); color: var(--amber); }
    .school-tag {
      display: inline-flex; padding: 2px 8px; border-radius: 4px;
      font-size: 11px; font-weight: 500; background: #f0e6ff; color: #6b21a8;
    }
    .name-cell { font-weight: 600; color: var(--text); }
    .raw-name { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
    .actions-cell { display: flex; gap: 6px; }
    /* --- Modal --- */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.5);
      display: flex; align-items: center; justify-content: center;
      z-index: 100; opacity: 0; pointer-events: none; transition: opacity 0.2s;
    }
    .modal-overlay.active { opacity: 1; pointer-events: all; }
    .modal {
      background: var(--surface); border-radius: 16px;
      padding: 32px; width: 90%; max-width: 640px; box-shadow: var(--shadow-lg);
      max-height: 88vh; overflow-y: auto;
      transform: scale(0.95); transition: transform 0.2s;
    }
    .modal-overlay.active .modal { transform: scale(1); }
    .modal h2 { font-size: 20px; font-weight: 700; margin-bottom: 20px; color: var(--maroon); }
    .form-group { margin-bottom: 16px; }
    .form-group label {
      display: block; font-size: 13px; font-weight: 600;
      color: var(--text-sec); margin-bottom: 6px;
    }
    .form-group input, .form-group textarea {
      width: 100%; padding: 10px 14px; border: 1px solid var(--surface-alt);
      border-radius: 8px; font-family: inherit; font-size: 14px;
      transition: border-color 0.15s;
    }
    .form-group input:focus, .form-group textarea:focus {
      outline: none; border-color: var(--maroon);
      box-shadow: 0 0 0 3px rgba(139,0,0,0.1);
    }
    .form-group textarea { resize: vertical; min-height: 80px; }
    /* --- Interest tags & composition editors --- */
    .tag-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 12px; }
    .tag-item {
      display: flex; align-items: center; gap: 8px;
      font-size: 13px; color: var(--text-sec); cursor: pointer;
    }
    .tag-item input { width: auto; accent-color: var(--maroon); cursor: pointer; }
    .comp-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .comp-cell label {
      display: block; font-size: 11px; font-weight: 600;
      color: var(--text-muted); margin-bottom: 4px;
    }
    .comp-total { margin-top: 8px; font-size: 12px; font-weight: 600; color: var(--text-muted); }
    .comp-total.bad { color: var(--red); }
    .badge-row { display: flex; gap: 4px; margin-top: 4px; }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
    /* --- Empty / Loading --- */
    .empty-state {
      text-align: center; padding: 60px 20px; color: var(--text-muted);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
    .loading { text-align: center; padding: 40px; color: var(--text-muted); }
    /* --- Toast --- */
    .toast {
      position: fixed; bottom: 24px; right: 24px; padding: 14px 24px;
      background: var(--text); color: #fff; border-radius: 10px;
      font-size: 14px; font-weight: 500; box-shadow: var(--shadow-lg);
      transform: translateY(100px); opacity: 0; transition: all 0.3s;
      z-index: 200;
    }
    .toast.show { transform: translateY(0); opacity: 1; }
  </style>
</head>
<body>

  <!-- Header -->
  <div class="header">
    <h1><span>Central</span> Course Guide — Admin Panel</h1>
    <div class="header-actions">
      <a href="/docs" class="btn btn-ghost btn-sm" target="_blank">API Docs</a>
      <a href="http://localhost:5173" class="btn btn-ghost btn-sm" target="_blank">Frontend</a>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats" id="stats"></div>

  <!-- Controls -->
  <div class="controls">
    <select id="schoolFilter">
      <option value="">All Schools</option>
    </select>
    <select id="statusFilter">
      <option value="">All Statuses</option>
      <option value="false">Pending Review</option>
      <option value="true">Reviewed</option>
    </select>
    <button class="btn btn-success btn-sm" onclick="reviewAll()">✓ Mark All Reviewed</button>
    <span id="countLabel" style="margin-left:auto; font-size:13px; color:var(--text-muted);"></span>
  </div>

  <!-- Table -->
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Programme Name</th>
          <th>School</th>
          <th>Code</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        <tr><td colspan="5" class="loading">Loading…</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Edit Modal -->
  <div class="modal-overlay" id="editModal">
    <div class="modal">
      <h2>Edit Programme</h2>
      <input type="hidden" id="editId" />
      <div class="form-group">
        <label>Programme Name</label>
        <input type="text" id="editName" />
      </div>
      <div class="form-group">
        <label>Code (e.g. BSC-CS)</label>
        <input type="text" id="editCode" />
      </div>
      <div class="form-group">
        <label>Duration (years)</label>
        <input type="number" id="editDuration" min="1" max="10" />
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea id="editDesc"></textarea>
      </div>
      <div class="form-group">
        <label>Career Paths (comma-separated)</label>
        <input type="text" id="editCareers" placeholder="e.g. Software Engineer, Data Analyst" />
      </div>
      <div class="form-group">
        <label>Interest Tags (used by the quiz to recommend this programme)</label>
        <div id="editTags" class="tag-grid"></div>
      </div>
      <div class="form-group">
        <label>Composition % (values must total exactly 100 — or leave all blank)</label>
        <div id="editComp" class="comp-grid"></div>
        <div id="compTotal" class="comp-total">Total: 0%</div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveEdit()">Save Changes</button>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast" id="toast"></div>

  <script>
    const API = '';  // same origin

    // ---- Toast ----
    function toast(msg) {
      const el = document.getElementById('toast');
      el.textContent = msg;
      el.classList.add('show');
      setTimeout(() => el.classList.remove('show'), 3000);
    }

    // ---- Stats ----
    async function loadStats() {
      const r = await fetch(API + '/admin/stats');
      const s = await r.json();
      document.getElementById('stats').innerHTML = `
        <div class="stat-card maroon"><div class="label">Schools</div><div class="value">${s.total_schools}</div></div>
        <div class="stat-card"><div class="label">Total Programmes</div><div class="value">${s.total_programmes}</div></div>
        <div class="stat-card green"><div class="label">Reviewed</div><div class="value">${s.reviewed_programmes}</div></div>
        <div class="stat-card amber"><div class="label">Pending Review</div><div class="value">${s.unreviewed_programmes}</div></div>
      `;
    }

    // ---- Schools dropdown ----
    async function loadSchools() {
      const r = await fetch(API + '/admin/schools');
      const schools = await r.json();
      const sel = document.getElementById('schoolFilter');
      schools.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s._id;
        opt.textContent = `${s.name} (${s.programme_count})`;
        sel.appendChild(opt);
      });
    }

    // ---- Programmes table ----
    async function loadProgrammes() {
      const schoolId = document.getElementById('schoolFilter').value;
      const reviewed = document.getElementById('statusFilter').value;
      let url = API + '/admin/programmes?';
      if (schoolId) url += `school_id=${schoolId}&`;
      if (reviewed !== '') url += `reviewed=${reviewed}&`;

      const r = await fetch(url);
      const progs = await r.json();
      const tbody = document.getElementById('tableBody');
      document.getElementById('countLabel').textContent = `${progs.length} programme(s)`;

      if (progs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No programmes found.</td></tr>`;
        return;
      }

      tbody.innerHTML = progs.map(p => `
        <tr>
          <td>
            <div class="name-cell">${esc(p.name)}</div>
            ${p.raw_name && p.raw_name !== p.name ? `<div class="raw-name">Raw: ${esc(p.raw_name)}</div>` : ''}
          </td>
          <td><span class="school-tag">${esc(p.school_name || '—')}</span></td>
          <td style="color:var(--text-muted)">${esc(p.code || '—')}</td>
          <td>
            <span class="badge ${p.is_reviewed ? 'badge-reviewed' : 'badge-pending'}">
              ${p.is_reviewed ? 'Reviewed' : 'Pending'}
            </span>
            <div class="badge-row">
              <span class="badge ${(p.interest_tags && p.interest_tags.length) ? 'badge-reviewed' : 'badge-pending'}">Tags</span>
              <span class="badge ${(p.composition && Object.keys(p.composition).length) ? 'badge-reviewed' : 'badge-pending'}">Comp</span>
            </div>
          </td>
          <td>
            <div class="actions-cell">
              <button class="btn btn-ghost btn-sm" onclick='openEdit(${JSON.stringify(p)})'>Edit</button>
              ${!p.is_reviewed ? `<button class="btn btn-success btn-sm" onclick="reviewOne('${p._id}')">✓</button>` : ''}
              <button class="btn btn-danger btn-sm" onclick="deleteProg('${p._id}')">✕</button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    function esc(s) { if(!s) return ''; const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

    // ---- Interest & composition taxonomy (fetched from the public API) ----
    async function loadTaxonomy() {
      const [ri, rd] = await Promise.all([
        fetch(API + '/interests'),
        fetch(API + '/composition-dimensions'),
      ]);
      const interests = await ri.json();
      const dimensions = await rd.json();

      document.getElementById('editTags').innerHTML = interests.map(i => `
        <label class="tag-item"><input type="checkbox" value="${i.id}" /> ${esc(i.label)}</label>
      `).join('');

      document.getElementById('editComp').innerHTML = dimensions.map(d => `
        <div class="comp-cell">
          <label>${esc(d.label)}</label>
          <input type="number" min="0" max="100" step="5" data-dim="${d.id}" placeholder="0" />
        </div>
      `).join('');

      document.querySelectorAll('#editComp input').forEach(inp =>
        inp.addEventListener('input', updateCompTotal));
    }

    function readComposition() {
      const comp = {};
      document.querySelectorAll('#editComp input').forEach(inp => {
        const v = parseInt(inp.value) || 0;
        if (v > 0) comp[inp.dataset.dim] = v;
      });
      return comp;
    }

    function updateCompTotal() {
      const total = Object.values(readComposition()).reduce((a, b) => a + b, 0);
      const el = document.getElementById('compTotal');
      el.textContent = `Total: ${total}%`;
      el.classList.toggle('bad', total !== 0 && total !== 100);
    }

    // ---- Filters ----
    document.getElementById('schoolFilter').addEventListener('change', loadProgrammes);
    document.getElementById('statusFilter').addEventListener('change', loadProgrammes);

    // ---- Actions ----
    async function reviewOne(id) {
      await fetch(API + `/admin/programmes/${id}/review`, { method: 'POST' });
      toast('Marked as reviewed');
      loadProgrammes(); loadStats();
    }

    async function reviewAll() {
      if (!confirm('Mark ALL pending programmes as reviewed?')) return;
      const r = await fetch(API + '/admin/programmes/review-all', { method: 'POST' });
      const d = await r.json();
      toast(d.detail);
      loadProgrammes(); loadStats();
    }

    async function deleteProg(id) {
      if (!confirm('Delete this programme permanently?')) return;
      await fetch(API + `/admin/programmes/${id}`, { method: 'DELETE' });
      toast('Programme deleted');
      loadProgrammes(); loadStats();
    }

    // ---- Edit Modal ----
    function openEdit(p) {
      document.getElementById('editId').value = p._id;
      document.getElementById('editName').value = p.name || '';
      document.getElementById('editCode').value = p.code || '';
      document.getElementById('editDuration').value = p.duration_years || '';
      document.getElementById('editDesc').value = p.description || '';
      document.getElementById('editCareers').value = (p.career_paths || []).join(', ');
      document.querySelectorAll('#editTags input').forEach(cb => {
        cb.checked = (p.interest_tags || []).includes(cb.value);
      });
      document.querySelectorAll('#editComp input').forEach(inp => {
        const v = (p.composition || {})[inp.dataset.dim];
        inp.value = v || '';
      });
      updateCompTotal();
      document.getElementById('editModal').classList.add('active');
    }

    function closeModal() {
      document.getElementById('editModal').classList.remove('active');
    }

    async function saveEdit() {
      const id = document.getElementById('editId').value;
      const careersRaw = document.getElementById('editCareers').value;
      const careers = careersRaw ? careersRaw.split(',').map(s => s.trim()).filter(Boolean) : [];

      const composition = readComposition();
      const compTotal = Object.values(composition).reduce((a, b) => a + b, 0);
      if (compTotal !== 0 && compTotal !== 100) {
        toast(`Composition must total exactly 100% (currently ${compTotal}%)`);
        return;
      }
      const interestTags = Array.from(
        document.querySelectorAll('#editTags input:checked')).map(cb => cb.value);

      const body = {
        name: document.getElementById('editName').value || undefined,
        code: document.getElementById('editCode').value || undefined,
        duration_years: parseInt(document.getElementById('editDuration').value) || undefined,
        description: document.getElementById('editDesc').value || undefined,
        career_paths: careers.length ? careers : undefined,
        is_reviewed: true,
        interest_tags: interestTags,   // [] clears the field
        composition: composition,      // {} clears the field
      };
      // Remove undefined keys
      Object.keys(body).forEach(k => body[k] === undefined && delete body[k]);

      const r = await fetch(API + `/admin/programmes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        const msg = Array.isArray(err.detail) ? err.detail[0]?.msg : err.detail;
        toast('Save failed: ' + (msg || r.status));
        return;
      }
      closeModal();
      toast('Programme updated');
      loadProgrammes(); loadStats();
    }

    // Click outside modal to close
    document.getElementById('editModal').addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) closeModal();
    });

    // ---- Init ----
    loadStats();
    loadSchools();
    loadTaxonomy();
    loadProgrammes();
  </script>
</body>
</html>
"""


@app.get("/admin-panel", response_class=HTMLResponse, tags=["Admin"])
async def admin_panel():
    """
    Serve the embedded admin panel UI.
    Visit http://localhost:8000/admin-panel in your browser.
    """
    return ADMIN_HTML


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
