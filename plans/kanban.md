## Kanban Board Plan (MVP)

Scope: Add a board view per project with columns mapped to ticket status. Users can drag and drop tickets between columns to change status and reorder within a column. Persist order and emit history when status changes.

### Columns / Statuses
- **Columns**: `open`, `in_progress`, `blocked`, `done`, `closed` (from `Ticket.ALLOWED_STATUSES`)
- **Order** (left ➜ right): open → in_progress → blocked → done → closed

### Data Model Changes
- None. Keep the schema as-is.

Ordering Strategy:
- Order tickets by `id` descending within each column (most recent first).

### Routes
- GET `/projects/@id:int/board` → `ProjectController@board` (auth)
- POST `/tickets/@id:int/move` → `TicketController@move` (auth, JSON)

Optional (later):
- GET `/projects/@id:int/board/partial` → return HTML for columns to refresh after moves (for HTMX-style UI refresh)

### Controller Logic
- `ProjectController@board`:
  - Load `project` (with creator) and tickets for that project, grouped by status
  - Order tickets by `id` desc within each status
  - Render `templates/projects/board.html`

- `TicketController@move` (JSON API):
  - Request body: `{"to_status": "in_progress"}`
  - Validate `to_status` ∈ `Ticket.ALLOWED_STATUSES`
  - Load ticket; ensure ticket belongs to a project (board assumes a project context)
  - In a transaction: if `to_status != ticket.status`, update status and emit a `status_changed` history entry
  - No reordering persistence; UI order is visual only and resets to `id desc` on reload
  - Respond 200 with `{ ok: true }` (or 204)

Edge cases:
- Moving into same column: reorder only, no status history
- Invalid status or index: 422 with error payload
- Cross-project move attempts: 400 (disallowed)

### Template (Board UI)
- `templates/projects/board.html` with a responsive grid of 5 columns.
- Each column has `data-status="open|in_progress|..."` and contains items with `data-ticket-id`.
- Ticket card shows: id, title, assignee, status badge color.
- Include a link back to the project details.

### Drag & Drop Strategy (Local deps)
- Use SortableJS installed via npm and bundled with our existing Laravel Mix pipeline.
- Initialize one `Sortable` instance per column; on `onEnd`, send a POST to `/tickets/{id}/move` with `to_status`.
- On success: keep current DOM order (visual only). On page reload, columns re-render as `id desc`.

Script sketch (in the board template):
```html
<script>
  import Sortable from 'sortablejs';
  const csrf = document.querySelector('meta[name="csrf-token"]').content;

  document.querySelectorAll('[data-column]')
    .forEach((col) => new Sortable(col, {
      group: 'kanban',
      animation: 150,
      onEnd: async (evt) => {
        const el = evt.item;
        const ticketId = el.dataset.ticketId;
        const toStatus = evt.to.closest('[data-status]').dataset.status;
        await fetch(`/tickets/${ticketId}/move`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': csrf,
          },
          body: JSON.stringify({ to_status: toStatus })
        });
      },
    }));
<\/script>
```

### Validation & Security
- All endpoints require `auth` middleware.
- Validate the ticket belongs to the same project as the board (no cross-project moves).
- Only allow statuses from `Ticket.ALLOWED_STATUSES`.

### Migrations
- None needed for MVP.

### Tests
- Board routes:
  - `GET /projects/{id}/board` returns 200 (auth)
- Move API:
  - Moving between columns updates `status`, returns 200
  - Reordering within a column is visual only; no persistence
  - Invalid status returns 422; cross-project returns 400
  - Emits `status_changed` history only when status changes

### Rollout Steps
1) Create migration for `position`; migrate and backfill.
2) Add routes.
3) Implement `ProjectController@board` and board template.
4) Implement `TicketController@move` with transaction + reindex.
5) Add SortableJS to board template; wire up fetch with CSRF.
6) Write tests; run `python -m pytest -q`.

### Acceptance Criteria
- Users can open `/projects/{id}/board` and view tickets grouped by status.
- Dragging a card to another column changes ticket status and persists on reload.
- Dragging within a column updates ordering visually only; order resets to id desc on reload.
- History records are created for status changes.

### Future Enhancements
- Real-time updates via WebSockets (broadcast moves to viewers)
- WIP limits per column; color badges and analytics per column
- Column customization (add/remove columns or rename)
- Keyboard-accessible move controls and a11y improvements
- Batch moves and multi-select

