Developer notes:
- Settings.py allows all CORS origins for local dev. For production, tighten this.
- The scoring algorithm returns a numeric score and short textual explanation suitable for display in UI.
- To adapt strategies (fastest/impact/deadline), either:
   - adjust weights in scoring.py before calling analyze, or
   - implement server-side handling of a 'strategy' parameter.
