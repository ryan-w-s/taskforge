# AGENTS

## Project overview

Jira clone.

## Features

* Tickets have a title, description, status, assignee, project, and labels
* Users can be assigned to tickets.
* Projects have a name and description.
* Labels have a name and description.
* Projects can be displayed as a kanban board.
* Tickets can be searched

## Run

```bash
python craft serve
```

## Test

```bash
python -m pytest -q
```

## `python craft` commands

Generally, prefer to use `python craft` commands as a starting point for new features (if an appropriate command exists).

```
AVAILABLE COMMANDS
  auth                   Creates a new authentication scaffold.
  command                Creates a new command class.
  controller             Creates a new controller class.
  db:shell               Connect to your database interactive terminal.
  down                   Puts the server in a maintenance state.
  event                  Creates a new event class.
  help                   Display the manual of a command
  job                    Creates a new job class.
  key                    Generate a new key.
  listener               Creates a new listener class.
  mailable               Creates a new mailable class.
  middleware             Creates a new middleware class.
  migrate                Run migrations.
  migrate:refresh        Rolls back migrations and migrates them again.
  migrate:reset          Reset migrations.
  migrate:rollback       Rolls back the last batch of migrations.
  migrate:status         Display migrations status.
  migration              Creates a new migration file.
  model                  Creates a new model file.
  model:docstring        Generate model docstring and type hints (for auto-completion).
  notification           Creates a new notification class.
  notification:table     Creates the notifications table needed for storing notifications in the database.
  observer               Creates a new observer file.
  package:publish        Publish package files to your project
  policy                 Creates a new policy class.
  preset                 Scaffold frontend preset in your project
  provider               Creates a new provider class.
  queue:failed           Creates a failed jobs table
  queue:retry            Puts all failed queue jobs back onto the queue.
  queue:table            Creates the jobs table
  queue:work             Creates a new queue worker to consume queue jobs
  routes:list            List all your application routes.
  rule                   Creates a new rule.
  rule:enclosure         Creates a new rule enclosure.
  schedule:run           Run the scheduled tasks
  seed                   Creates a new seed file.
  seed:run               Run seeds.
  serve                  Run the Masonite server.
  task                   Create a new task
  test                   Creates a new test class.
  tinker                 Run a python shell with the container pre-loaded.
  up                     Brings the server out of maintenance state.
  view                   Creates a new view.
```


## Tech Stack

* Masonite
* Python 3.11
* uv
* sqlite

## Prerequisites

* Python 3.11
* Node.js 16+ (for asset building)
* uv (optional)

## Install

```bash
# using uv (recommended)
uv sync

# or using pip
pip install -r requirements.txt
```

## Database

```bash
python craft migrate
python craft seed:run
```

## Default user

Email: `user@example.com`  Password: `secret`

## Environment

```bash
# generate a new APP_KEY (recommended before production)
python craft key
```

## Assets (optional)

```bash
npm install
npm run dev   # for development
# npm run prod  # for production builds
```

App runs at `http://localhost:8000/` by default.

## Useful commands

```bash
# show routes
python craft routes:list

# check migration status
python craft migrate:status

# reset or refresh database
python craft migrate:reset
python craft migrate:refresh

# open DB shell (connection-specific)
python craft db:shell
```

Default SQLite DB file: `masonite.sqlite3` (see `config/database.py`).