# Smart Task Analyzer (Human-friendly edition)

This is a small Django + vanilla JS project built for the assignment. It includes:
- A clear, commented scoring algorithm
- Two API endpoints: /api/tasks/analyze/ and /api/tasks/suggest/
- A minimal frontend to add/paste tasks and view sorted results
- Unit tests for the scoring logic

See `backend/README_NOTES.txt` for developer notes.

## Quick start
1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```
4. Run tests (optional):
   ```bash
   python manage.py test
   ```
5. Run dev server:
   ```bash
   python manage.py runserver
   ```
6. Open `frontend/index.html` in your browser and use the UI. The frontend calls `http://127.0.0.1:8000/api/tasks/analyze/`.

## Notes
- The scoring weights are in `backend/tasks/scoring.py` and are easy to adjust.
- The app is intentionally lightweight for clarity and grading.
