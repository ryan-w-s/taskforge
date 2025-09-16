from masonite.controllers import Controller
from masonite.views import View
from masonite.request import Request
from masonite.response import Response

from app.models.Project import Project
from app.models.Ticket import Ticket


class ProjectController(Controller):
    def index(self, view: View):
        projects = Project.with_("creator", "tickets").order_by("-id").get()
        return view.render("projects.index", {"projects": projects})

    def create(self, view: View):
        return view.render("projects.create")

    def store(self, request: Request, response: Response):
        errors = request.validate({
            "name": "required|length:1..255",
        })

        if errors:
            return response.back().with_errors(errors)

        project = Project.create(
            name=request.input("name"),
            description=request.input("description"),
            created_by_id=request.user().id,
        )

        return response.redirect(f"/projects/{project.id}")

    def show(self, view: View, request: Request):
        project = Project.with_("creator").find_or_fail(request.param("id"))
        tickets = Ticket.with_("assignee").where("project_id", project.id).order_by("-id").get()
        return view.render("projects.show", {"project": project, "tickets": tickets})

    def edit(self, view: View, request: Request):
        project = Project.find_or_fail(request.param("id"))
        return view.render("projects.edit", {"project": project})

    def update(self, request: Request, response: Response):
        errors = request.validate({
            "name": "required|length:1..255",
        })

        if errors:
            return response.back().with_errors(errors)

        project = Project.find_or_fail(request.param("id"))
        project.name = request.input("name")
        project.description = request.input("description")
        project.save()
        return response.redirect(f"/projects/{project.id}")

    def delete(self, request: Request, response: Response):
        project = Project.find_or_fail(request.param("id"))

        # Prevent delete if tickets exist
        if len(project.tickets) > 0:
            return response.back().with_errors({"project": "Cannot delete a project that has tickets."})

        project.delete()
        return response.redirect("/projects")
