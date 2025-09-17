from masonite.controllers import Controller
from masonite.views import View
from masonite.request import Request

from app.models.Ticket import Ticket


class HomeController(Controller):
    def show(self, view: View, request: Request):
        user = request.user()
        tickets = (
            Ticket.with_("project")
            .where("assignee_id", user.id)
            .order_by("-id")
            .get()
        )
        return view.render("auth.home", {"tickets": tickets, "user": user})
