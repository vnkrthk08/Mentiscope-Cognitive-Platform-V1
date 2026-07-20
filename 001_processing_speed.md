# Processing Speed integration migration

The module writes to Mentiscope's existing `sessions`, `responses`, `events`, `results`, and `analytics` tables. It adds no module-specific table.

Ensure those shared tables can retain `module_id = 'processing-speed'`, an item identifier, response value, correctness, reaction time, and JSON analytics. For a new development database, `backend.main` creates the baseline shared tables automatically. For PostgreSQL, apply the platform's normal migration mechanism before deploying this router; do not run the legacy standalone module's MySQL schema because it duplicates the shared tables.
