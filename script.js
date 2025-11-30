// Simple frontend logic for demo purposes
let tasks = [];

function updateTaskList() {
  document.getElementById('task-list').textContent = JSON.stringify(tasks, null, 2);
}

document.getElementById('add-task').addEventListener('click', () => {
  const title = document.getElementById('title').value.trim();
  if (!title) { alert('Title is required'); return; }
  const due_date = document.getElementById('due_date').value || null;
  const estimated_hours = parseInt(document.getElementById('estimated_hours').value || 0);
  const importance = parseInt(document.getElementById('importance').value || 0);
  const depsRaw = document.getElementById('dependencies').value.trim();
  const dependencies = depsRaw ? depsRaw.split(',').map(s => s.trim()).filter(Boolean).map(x => isNaN(x) ? x : parseInt(x)) : [];
  const id = tasks.length;
  tasks.push({ id, title, due_date, estimated_hours, importance, dependencies });
  updateTaskList();
  document.getElementById('task-form').reset();
});

document.getElementById('analyze').addEventListener('click', async () => {
  const mode = document.querySelector('input[name="mode"]:checked').value;
  let payload;
  if (mode === 'bulk') {
    const txt = document.getElementById('bulk').value.trim();
    if (!txt) { alert('Paste JSON array in bulk textarea'); return; }
    try {
      payload = JSON.parse(txt);
      if (!Array.isArray(payload)) { alert('Bulk input must be a JSON array'); return; }
    } catch (e) { alert('Invalid JSON'); return; }
  } else {
    payload = tasks;
    if (payload.length === 0) { alert('No tasks to analyze'); return; }
  }

  document.getElementById('status').textContent = 'Analyzing...';
  try {
    const resp = await fetch('http://127.0.0.1:8000/api/tasks/analyze/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tasks: payload })
    });
    if (!resp.ok) {
      const err = await resp.json();
      alert('Server error: ' + (err.error || resp.statusText));
      document.getElementById('status').textContent = '';
      return;
    }
    const data = await resp.json();
    renderResults(data.tasks);
    document.getElementById('status').textContent = data.circular_dependencies_detected ? 'Warning: circular deps detected' : 'Done';
  } catch (err) {
    alert('Network error: ' + err.message);
    document.getElementById('status').textContent = '';
  }
});

function renderResults(list) {
  const container = document.getElementById('results');
  container.innerHTML = '';
  for (const t of list) {
    const card = document.createElement('div');
    card.className = 'card';
    let cls = 'p-low';
    if (t.score >= 70) cls = 'p-high';
    else if (t.score >= 40) cls = 'p-mid';
    card.classList.add(cls);

    const left = document.createElement('div');
    left.innerHTML = `<strong>${escapeHtml(t.title)}</strong>
      <div style="margin-top:6px">Due: ${t.due_date || '—'}</div>
      <div style="margin-top:6px">Importance: ${t.importance} • Effort: ${t.estimated_hours}h</div>`;

    const right = document.createElement('div');
    right.innerHTML = `<div>Score: ${t.score}</div>
      <div style="font-size:12px;color:#333;margin-top:6px">${escapeHtml(t.explanation)}</div>`;

    card.appendChild(left);
    card.appendChild(right);
    container.appendChild(card);
  }
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/[&<>"']/g, function(m){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]; });
}
