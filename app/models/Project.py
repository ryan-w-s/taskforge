""" Project Model """

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to, has_many


class Project(Model):
    """Project Model"""

    __table__ = "projects"

    __fillable__ = [
        "name",
        "description",
        "created_by_id",
    ]

    @belongs_to("created_by_id", "id")
    def creator(self):
        from app.models.User import User

        return User

    @has_many("id", "project_id")
    def tickets(self):
        from app.models.Ticket import Ticket

        return Ticket
