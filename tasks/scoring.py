"""Scoring logic for tasks.

This module intentionally favors clarity and explainability:
- Each factor is normalized to 0..1
- A weighted linear combination produces the final score (0..100)
- The weights are configurable constants at the top of the file
"""
from datetime import date
from typing import List, Dict, Any

# Tunable weights — adjust to change algorithm behavior
W_IMPORTANCE = 0.4
W_URGENCY = 0.3
W_EFFORT = 0.15
W_DEPENDENCY = 0.15

MAX_IMPORTANCE = 10.0
MAX_URGENCY_DAYS = 30.0  # beyond this, urgency contribution saturates
MAX_EFFORT = 40.0  # treat tasks above this as "high effort"

def _days_until(due_date):
    if due_date is None:
        return None
    today = date.today()
    return (due_date - today).days

def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> bool:
    """Detect cycles in dependency graph using depth-first search.
    tasks: list of dicts with 'id' and 'dependencies' keys.
    Returns True if any cycle exists.
    """
    graph = {t['id']: set(t.get('dependencies', [])) for t in tasks}
    visited = {}  # 0=unvisited, 1=visiting, 2=visited

    def dfs(node):
        if node not in graph:
            return False
        if visited.get(node) == 1:
            return True
        if visited.get(node) == 2:
            return False
        visited[node] = 1
        for neighbor in graph[node]:
            if dfs(neighbor):
                return True
        visited[node] = 2
        return False

    for n in graph:
        if visited.get(n) is None:
            if dfs(n):
                return True
    return False

def compute_dependency_counts(tasks: List[Dict[str, Any]]) -> Dict[Any, int]:
    """Return a mapping: task_id -> how many tasks depend on it."""
    counts = {t['id']: 0 for t in tasks}
    for t in tasks:
        for dep in t.get('dependencies', []):
            if dep in counts:
                counts[dep] += 1
    return counts

def score_task(task: Dict[str, Any], dep_counts: Dict[Any, int]) -> (float, str):
    """Compute a human-readable score (0..100) and explanation string for a single task."""
    # Importance normalized 0..1
    importance = float(task.get('importance') or 0)
    importance_norm = max(0.0, min(MAX_IMPORTANCE, importance)) / MAX_IMPORTANCE

    # Urgency normalized 0..1 (1 == most urgent/overdue)
    due = task.get('due_date')
    urgency = 0.0
    overdue = False
    if due:
        days_left = _days_until(due)
        if days_left is None:
            urgency = 0.0
        elif days_left < 0:
            urgency = 1.0
            overdue = True
        else:
            urgency = max(0.0, (MAX_URGENCY_DAYS - min(MAX_URGENCY_DAYS, days_left)) / MAX_URGENCY_DAYS)

    # Effort: lower hours => higher contribution
    try:
        est = float(task.get('estimated_hours') or 0)
    except Exception:
        est = 0.0
    est = max(0.0, est)
    effort_score = 1.0 - min(est, MAX_EFFORT) / MAX_EFFORT

    # Dependency impact
    dep_count = dep_counts.get(task['id'], 0)
    dep_score = min(1.0, dep_count / max(1.0, len(dep_counts)))

    # Weighted linear combination
    combined = (W_IMPORTANCE * importance_norm +
                W_URGENCY * urgency +
                W_EFFORT * effort_score +
                W_DEPENDENCY * dep_score)

    final_score = round(combined * 100, 2)

    explanation = (
        f"Importance: {importance}/10 => {round(importance_norm*100,1)}; "
        f"Urgency: {'OVERDUE' if overdue else round(urgency*100,1)}; "
        f"Effort benefit: {est}h => {round(effort_score*100,1)}; "
        f"Dependency impact: {dep_count} => {round(dep_score*100,1)}"
    )

    return final_score, explanation
