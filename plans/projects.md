## Projects Feature Plan (MVP)

Scope: Introduce Projects so tickets belong to a project. Provide CRUD for projects, integrate projects into ticket forms and views, and prepare for a future kanban board per project.

### What to store
- **id**: primary key
- **name**: string (1..255)
- **description**: text (nullable)
- **created_by_id**: fk → `users.id` (who created the project)
- **created_at / updated_at**: timestamps

Indexes: `name`, `created_by_id`.

### Generators / Commands
- Create migration for projects table:
  - `python craft migration create_projects_table`
- Create Project model:
  - `python craft model Project`
- Add `project_id` on tickets:
  - `python craft migration add_project_id_to_tickets_table`
- Create Projects controller:
  - `python craft controller ProjectController`
- Create tests (skeletons):
  - `python craft test ProjectRoutesTest`

### Migrations
- **create_projects_table**
  - Columns: `id`, `name`, `description` (nullable), `created_by_id` (nullable=False), timestamps
  - Index `name`, `created_by_id`
  - FK: `created_by_id` → `users.id`

- **add_project_id_to_tickets_table**
  - Add nullable `project_id` (unsigned int) to `tickets`
  - Index `project_id`
  - FK: `project_id` → `projects.id`
  - Keep nullable initially; can enforce NOT NULL in a future migration once all tickets have a project

### Models
- **app/models/Project.py**
  - `__table__ = "projects"`
  - `__fillable__ = ["name", "description", "created_by_id"]`
  - Relationships:
    - `@belongs_to("created_by_id", "id") def creator()` → `User`
    - `@has_many("id", "project_id") def tickets()` → `Ticket`

- **app/models/Ticket.py**
  - Add `"project_id"` to `__fillable__`
  - Add relationship: `@belongs_to("project_id", "id") def project()` → `Project`

### Routes
Protected by `auth` middleware.

Add to `routes/web.py`:
- `GET  /projects` → `ProjectController@index` (list)
- `GET  /projects/create` → `ProjectController@create`
- `POST /projects` → `ProjectController@store`
- `GET  /projects/@id:int` → `ProjectController@show`
- `GET  /projects/@id:int/edit` → `ProjectController@edit`
- `POST /projects/@id:int/update` → `ProjectController@update`
- `POST /projects/@id:int/delete` → `ProjectController@delete`

### Controller (ProjectController)
- **index**: list projects with counts of tickets (optional: eager load counts)
- **create**: render form
- **store**: validate `name: required|length:1..255`; create with `created_by_id = request.user().id`
- **show**: show project details + list tickets for the project
- **edit/update**: update name/description
- **delete**: soft strategy: prevent delete if tickets exist, or cascade if you prefer; MVP can allow delete if empty

### Views (templates)
- `templates/projects/index.html`: table of projects (Name, Tickets, Created By, Created At)
- `templates/projects/create.html`: form (name, description)
- `templates/projects/edit.html`: form
- `templates/projects/show.html`: project info + table/list of tickets in the project with links to tickets
- Update ticket forms to include Project selection:
  - `templates/tickets/create.html` and `templates/tickets/edit.html`: add a `<select name="project_id">` populated from `Project.all()`
- Update navigation to include a link to `/projects`

### Tests
- Project routes smoke tests (`ProjectRoutesTest`):
  - `GET /projects` returns 200 when authenticated
  - Create a project via `POST /projects` → redirect + appears on index
  - Show/edit/update and delete routes work
- Ticket integration tests (extend current):
  - Creating a ticket with `project_id` persists it and shows on ticket show page
  - Editing a ticket can change `project_id`

Suggested commands when running locally:
```bash
python craft migrate
python -m pytest -q
```

### Acceptance criteria
- Users can create, view, edit, and delete projects
- Tickets can be associated with projects; project appears in ticket views
- Ticket create/edit forms include project selection
- Projects index and show pages render correctly

### Future enhancements
- Kanban board per project (columns mapped to ticket status)
- Permissions/ownership for projects (only creator/admins can modify)
- Project labels, project members/watchers
- Search/filter tickets by project

