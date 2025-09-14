## Ticket Change History Plan (MVP)

Scope: Track ticket lifecycle events (created, status change, assignee change). Keep it simple and additive-only.

### What to store
- `id` (pk)
- `ticket_id` (fk → `tickets.id`, indexed)
- `changed_by_id` (fk → `users.id`, nullable for system events)
- `event_type` (string; one of: `created`, `status_changed`, `assignee_changed`, `commented`)
- `from_status` (string, nullable)
- `to_status` (string, nullable)
- `from_assignee_id` (int, nullable)
- `to_assignee_id` (int, nullable)
- `body` (text, nullable; used for comments and optional notes)
- `created_at` (timestamp)

Indexes: `ticket_id`, `created_at` (for fast per-ticket timeline), optionally `event_type`.

Status values: reuse `Ticket.ALLOWED_STATUSES`.

### Generators / Commands
- Migration
  - Create file: `python craft migration create_ticket_histories_table`
  - Then define columns listed above; add indexes for `ticket_id`, `created_at`.
- Model
  - Create file: `python craft model TicketHistory`
  - Configure:
    - `__table__ = "ticket_histories"`
    - `__fillable__ = ["ticket_id", "changed_by_id", "event_type", "from_status", "to_status", "from_assignee_id", "to_assignee_id", "body"]`
    - Relations: `belongs_to` `ticket` and `actor` (User).
- Tests (basic)
  - Create file: `python craft test TicketHistoryTest`
  - Cases: entry on create; entry when status changes; entry when assignee changes.

### Controller integration (minimal)
- `TicketController.store`
  - After creating the ticket, insert 1 history row:
    - `event_type = "created"`
    - `to_status = ticket.status`
    - `to_assignee_id = ticket.assignee_id`
    - `changed_by_id = request.user().id`
- `TicketController.update`
  - Load `before = Ticket.find_or_fail(id)` before mutating.
  - After saving changes, compare and insert rows:
    - If status changed: add `status_changed` with `from_status`/`to_status` and `changed_by_id`.
    - If assignee changed: add `assignee_changed` with `from_assignee_id`/`to_assignee_id` and `changed_by_id`.
  - Optional: wrap in a DB transaction if writing multiple rows.

- Comments via history (unified)
  - Add a new action to `TicketController` (or a tiny `TicketCommentController` if preferred):
    - Route: `POST /tickets/@id/comment` (auth + CSRF)
    - Validation: `body` required, `length:1..2000`
    - Insert row in `ticket_histories` with:
      - `event_type = "commented"`
      - `ticket_id = id`
      - `changed_by_id = request.user().id`
      - `body = request.input("body")`

### View integration (minimal)
- `tickets.show`
  - Query: `TicketHistory.where("ticket_id", ticket.id).order_by("-created_at").get()`
  - Render a simple list: timestamp, actor, event summary.
    - For `commented`, display comment `body` content.
  - Add a minimal comment form posting to `/tickets/@id/comment` with CSRF.

### Acceptance criteria
- Each create/update emits appropriate immutable history rows.
- `tickets.show` displays a reverse-chronological timeline.
- Tests cover: create emits 1 row; status change emits 1 row; assignee change emits 1 row; posting a comment emits a `commented` row.

### Notes
- Keep `event_type` as TEXT (SQLite-friendly). Validation at application layer.
- Future: extend to title/description edits, batching, and user-facing notes.

### References
- Masonite tutorial patterns for routes/controllers/views: Creating A Blog Tutorial — https://docs.masoniteproject.com/prologue/create-a-blog


