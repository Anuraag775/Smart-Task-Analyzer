"""API views for task analysis endpoints.

Two endpoints:
- POST /api/tasks/analyze/  -> accepts tasks JSON and returns scored, sorted tasks
- GET  /api/tasks/suggest/  -> returns top 3 tasks from provided tasks query param
"""
import json
from datetime import datetime, date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scoring import detect_circular_dependencies, compute_dependency_counts, score_task

DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d")

def _parse_date(s):
    if s in (None, "", []):
        return None
    if isinstance(s, date):
        return s
    if isinstance(s, str):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
    return None

@csrf_exempt
def analyze_tasks(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    # Accept either { "tasks": [...] } or a raw list
    tasks_input = payload.get('tasks') if isinstance(payload, dict) and 'tasks' in payload else payload
    if not isinstance(tasks_input, list):
        return JsonResponse({'error': 'expected a list of tasks'}, status=400)

    # Normalize tasks and assign ids if missing
    tasks = []
    for idx, raw in enumerate(tasks_input):
        t = dict(raw)  # shallow copy
        if 'id' not in t:
            t['id'] = idx
        t['due_date'] = _parse_date(t.get('due_date'))
        try:
            t['estimated_hours'] = int(t.get('estimated_hours') or 0)
        except Exception:
            t['estimated_hours'] = 0
        try:
            t['importance'] = int(t.get('importance') or 0)
        except Exception:
            t['importance'] = 0
        deps = t.get('dependencies') or []
        if not isinstance(deps, list):
            try:
                deps = json.loads(deps)
            except Exception:
                deps = []
        t['dependencies'] = deps
        tasks.append(t)

    circular = detect_circular_dependencies(tasks)
    dep_counts = compute_dependency_counts(tasks)

    scored = []
    for t in tasks:
        score_val, explanation = score_task(t, dep_counts)
        scored.append({
            'id': t['id'],
            'title': t.get('title',''),
            'due_date': t['due_date'].isoformat() if isinstance(t['due_date'], date) else None,
            'estimated_hours': t.get('estimated_hours', 0),
            'importance': t.get('importance', 0),
            'dependencies': t.get('dependencies', []),
            'score': score_val,
            'explanation': explanation,
        })

    scored_sorted = sorted(scored, key=lambda x: x['score'], reverse=True)

    return JsonResponse({'circular_dependencies_detected': circular, 'tasks': scored_sorted})

def suggest_tasks(request):
    tasks_param = request.GET.get('tasks')
    if not tasks_param:
        return JsonResponse({'error': 'please provide tasks param as JSON'}, status=400)
    try:
        tasks_input = json.loads(tasks_param)
    except Exception:
        return JsonResponse({'error': 'invalid tasks JSON'}, status=400)

    tasks = []
    for idx, raw in enumerate(tasks_input):
        t = dict(raw)
        if 'id' not in t:
            t['id'] = idx
        t['due_date'] = _parse_date(t.get('due_date'))
        t['estimated_hours'] = int(t.get('estimated_hours') or 0)
        t['importance'] = int(t.get('importance') or 0)
        t['dependencies'] = t.get('dependencies') or []
        tasks.append(t)

    dep_counts = compute_dependency_counts(tasks)
    scored = []
    for t in tasks:
        score_val, explanation = score_task(t, dep_counts)
        scored.append({'id': t['id'], 'title': t.get('title',''), 'score': score_val, 'explanation': explanation})
    top3 = sorted(scored, key=lambda x: x['score'], reverse=True)[:3]
    return JsonResponse({'top_3': top3})
