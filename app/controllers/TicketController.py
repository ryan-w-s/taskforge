from masonite.controllers import Controller
from masonite.views import View
from masonite.request import Request
from masonite.response import Response

from app.models.Ticket import Ticket
from app.models.User import User


class TicketController(Controller):
    def index(self, view: View):
        tickets = Ticket.with_("assignee").order_by("-id").get()
        return view.render("tickets.index", {"tickets": tickets})

    def create(self, view: View):
        users = User.all()
        return view.render(
            "tickets.create",
            {
                "statuses": Ticket.ALLOWED_STATUSES,
                "users": users,
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

        ticket = Ticket.create(
            title=request.input("title"),
            description=request.input("description"),
            status=request.input("status"),
            assignee_id=assignee_id,
        )

        return response.redirect(f"/tickets/{ticket.id}")

    def show(self, view: View, request: Request):
        ticket = Ticket.with_("assignee").find_or_fail(request.param("id"))
        return view.render("tickets.show", {"ticket": ticket})

    def edit(self, view: View, request: Request):
        ticket = Ticket.find_or_fail(request.param("id"))
        users = User.all()
        return view.render(
            "tickets.edit",
            {
                "ticket": ticket,
                "statuses": Ticket.ALLOWED_STATUSES,
                "users": users,
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
        ticket.title = request.input("title")
        ticket.description = request.input("description")
        ticket.status = request.input("status")
        assignee_raw = request.input("assignee_id")
        ticket.assignee_id = (
            int(assignee_raw) if assignee_raw and str(assignee_raw).isdigit() else None
        )
        ticket.save()

        return response.redirect(f"/tickets/{ticket.id}")

    def delete(self, request: Request, response: Response):
        ticket = Ticket.find_or_fail(request.param("id"))
        ticket.delete()
        return response.redirect("/tickets")


