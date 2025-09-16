from masonite.controllers import Controller
from masonite.views import View
from masonite.request import Request
from masonite.response import Response

from app.models.Ticket import Ticket
from app.models.User import User
from app.models.TicketHistory import TicketHistory
from app.models.Project import Project


class TicketController(Controller):
    def index(self, view: View):
        tickets = Ticket.with_("assignee").order_by("-id").get()
        return view.render("tickets.index", {"tickets": tickets})

    def create(self, view: View):
        users = User.all()
        projects = Project.all()
        return view.render(
            "tickets.create",
            {
                "statuses": Ticket.ALLOWED_STATUSES,
                "users": users,
                "projects": projects,
            },
        )

    def store(self, request: Request, response: Response):
        errors = request.validate(
            {
                "title": "required|length:1..255",
                "status": "required|is_in:" + ",".join(Ticket.ALLOWED_STATUSES),
            }
        )

        if errors:
            return response.back().with_errors(errors)

        assignee_raw = request.input("assignee_id")
        assignee_id = (
            int(assignee_raw) if assignee_raw and str(assignee_raw).isdigit() else None
        )

        project_raw = request.input("project_id")
        project_id = (
            int(project_raw) if project_raw and str(project_raw).isdigit() else None
        )

        ticket = Ticket.create(
            title=request.input("title"),
            description=request.input("description"),
            status=request.input("status"),
            assignee_id=assignee_id,
            project_id=project_id,
        )

        # Create history entry for ticket creation
        TicketHistory.create(
            ticket_id=ticket.id,
            changed_by_id=request.user().id,
            event_type="created",
            to_status=ticket.status,
            to_assignee_id=ticket.assignee_id,
        )

        return response.redirect(f"/tickets/{ticket.id}")

    def show(self, view: View, request: Request):
        ticket = Ticket.with_("assignee", "project").find_or_fail(request.param("id"))

        # Load ticket history with actor relationships
        history = TicketHistory.with_("actor", "from_assignee", "to_assignee") \
                              .where("ticket_id", ticket.id) \
                              .order_by("-created_at") \
                              .get()

        return view.render("tickets.show", {
            "ticket": ticket,
            "history": history
        })

    def edit(self, view: View, request: Request):
        ticket = Ticket.find_or_fail(request.param("id"))
        users = User.all()
        projects = Project.all()
        return view.render(
            "tickets.edit",
            {
                "ticket": ticket,
                "statuses": Ticket.ALLOWED_STATUSES,
                "users": users,
                "projects": projects,
            },
        )

    def update(self, request: Request, response: Response):
        errors = request.validate(
            {
                "title": "required|length:1..255",
                "status": "required|is_in:" + ",".join(Ticket.ALLOWED_STATUSES),
            }
        )

        if errors:
            return response.back().with_errors(errors)

        ticket = Ticket.find_or_fail(request.param("id"))

        # Store original values before updating
        original_status = ticket.status
        original_assignee_id = ticket.assignee_id

        # Update the ticket
        ticket.title = request.input("title")
        ticket.description = request.input("description")
        ticket.status = request.input("status")
        assignee_raw = request.input("assignee_id")
        ticket.assignee_id = (
            int(assignee_raw) if assignee_raw and str(assignee_raw).isdigit() else None
        )
        project_raw = request.input("project_id")
        ticket.project_id = (
            int(project_raw) if project_raw and str(project_raw).isdigit() else None
        )
        ticket.save()

        # Create history entries for changes
        history_entries = []

        # Check for status change
        if ticket.status != original_status:
            history_entries.append({
                "ticket_id": ticket.id,
                "changed_by_id": request.user().id,
                "event_type": "status_changed",
                "from_status": original_status,
                "to_status": ticket.status,
            })

        # Check for assignee change
        if ticket.assignee_id != original_assignee_id:
            history_entries.append({
                "ticket_id": ticket.id,
                "changed_by_id": request.user().id,
                "event_type": "assignee_changed",
                "from_assignee_id": original_assignee_id,
                "to_assignee_id": ticket.assignee_id,
            })

        # Create history entries
        for entry in history_entries:
            TicketHistory.create(**entry)

        return response.redirect(f"/tickets/{ticket.id}")

    def delete(self, request: Request, response: Response):
        ticket = Ticket.find_or_fail(request.param("id"))
        ticket.delete()
        return response.redirect("/tickets")

    def comment(self, request: Request, response: Response):
        """Add a comment to a ticket"""
        ticket_id = request.param("id")

        # Ensure ticket exists
        ticket = Ticket.find_or_fail(ticket_id)

        # Validate comment
        errors = request.validate(
            {
                "body": "required|length:1..2000",
            }
        )

        if errors:
            return response.back().with_errors(errors)

        # Create comment history entry
        TicketHistory.create(
            ticket_id=ticket_id,
            changed_by_id=request.user().id,
            event_type="commented",
            body=request.input("body"),
        )

        return response.redirect(f"/tickets/{ticket_id}")


