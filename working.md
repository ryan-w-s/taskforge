## Tickets Feature Plan (MVP)

Scope: Implement Tickets (CRUD, status, assignee) using Masonite patterns. Exclude projects, labels, search, and kanban for now. Auth is already present and required for all ticket routes.

Reference patterns follow Masonite's controller/view/routing flow shown in the blog tutorial (routes → controller → views → model, forms with CSRF) [Creating A Blog Tutorial](https://docs.masoniteproject.com/prologue/create-a-blog).

### 1) Data Model & Migration
- Create `tickets` table with fields:
  - `id` (pk)
  - `title` (string, required, <= 255)
  - `description` (text, optional)
  - `status` (string, required; default `open`)
  - `assignee_id` (int, nullable, fk → `users.id`)
  - `created_at` / `updated_at` (timestamps)
- Indices: `status`, `assignee_id`.
- Commands:
  - `python craft migration create_tickets_table`
  - Implement columns and FK in the generated migration.
  - `python craft migrate`

SQLite note: Enforce allowed statuses at the application layer for now (use validation); CHECK constraints can be added later when moving beyond SQLite or by custom SQL.

Statuses (initial set): `open`, `in_progress`, `blocked`, `done`, `closed`.

### 2) ORM Model
- `app/models/Ticket.py`
  - Define fillable fields: `title`, `description`, `status`, `assignee_id`.
  - Relationship: `assignee` → `User` (`belongs_to`).
  - Centralize `ALLOWED_STATUSES` for validation/rendering.
- Command scaffold: `python craft model Ticket`.

### 3) Routes (behind auth)
Add authenticated routes in `routes/web.py` mirroring Masonite tutorial patterns:
- `GET /tickets` → list
- `GET /tickets/create` → create form
- `POST /tickets` → store
- `GET /tickets/@id` → show
- `GET /tickets/@id/edit` → edit form
- `POST /tickets/@id/update` → update
- `POST /tickets/@id/delete` → delete

Apply `auth` middleware to all ticket routes. Ensure CSRF middleware is active for POST forms.

### 4) Controller
- `app/controllers/TicketController.py` methods:
  - `index(view)` → fetch all tickets with eager-loaded `assignee`; render list
  - `create(view)` → render form; pass `ALLOWED_STATUSES` and selectable users
  - `store(request, response)` → validate; create; redirect to show
  - `show(view, request)` → find by `id`; render details
  - `edit(view, request)` → fetch; render form with current values
  - `update(request, response)` → validate; update; redirect
  - `delete(request, response)` → delete; redirect to index

Validation rules (server-side):
- `title`: required, max length 255
- `status`: required, in `ALLOWED_STATUSES`
- `assignee_id`: nullable, exists in users table

Command: `python craft controller Ticket`.

### 5) Views / Templates
Create `templates/tickets/`:
- `index.html`: table/list of tickets (title → link to show, status, assignee email/name), link to create
- `create.html`: form fields `title`, `description`, `status` (select), `assignee_id` (select of users); include `{{ csrf_field }}`; `method="POST"`
- `show.html`: display fields; links to edit and delete (delete via POST form)
- `edit.html`: same as create but prefilled; submit to `/tickets/@id/update`.

Follow the Masonite tutorial form and route wiring (CSRF field, POST endpoints). Keep markup minimal initially; styling can come later.

### 6) Authentication & Authorization
- Require authentication on all ticket routes using existing auth middleware.
- Basic policy (MVP): Any authenticated user can create/read. Allow update/delete to any authenticated user for now. Tighten later if needed (e.g., only creator/assignee/admin).

### 7) Tests
- HTTP tests covering:
  - Unauthenticated users redirected on ticket routes
  - Create ticket (valid/invalid)
  - List, show
  - Update (status change, reassignment)
  - Delete
- Model tests for `ALLOWED_STATUSES` and `assignee` relation.
- Run: `python -m pytest -q`.

### 8) Seed Data (optional)
- Add sample tickets referencing the default user for local testing.
- Commands: `python craft seed` (generate), implement records, then `python craft seed:run`.

### 9) Future Iterations (not in MVP)
- Committed approach for history: Use a dedicated `ticket_histories` table tracking `old_status`, `new_status`, `from_assignee_id`, `to_assignee_id`, `changed_by_id`, and timestamp. Recorded on status/assignee changes.
- Comments: `ticket_comments` with `ticket_id`, `user_id`, `body`, timestamps.
- Labels and projects: add later; adjust forms and relations accordingly.
- Kanban board & search: build once projects/labels exist.

### Definition of Done
- Authenticated CRUD for tickets with status and assignee.
- Server-side validation enforced.
- Views render and forms submit with CSRF protection.
- Migrations applied; no runtime errors; tests pass.

