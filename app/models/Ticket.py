from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class Ticket(Model):
    """Ticket Model."""

    __table__ = "tickets"

    __fillable__ = [
        "title",
        "description",
        "status",
        "assignee_id",
        "project_id",
    ]

    # Centralized statuses for validation and rendering
    ALLOWED_STATUSES = [
        "open",
        "in_progress",
        "blocked",
        "done",
        "closed",
    ]

    @belongs_to("assignee_id", "id")
    def assignee(self):
        from app.models.User import User

        return User


    @belongs_to("project_id", "id")
    def project(self):
        from app.models.Project import Project

        return Project
