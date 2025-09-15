""" TicketHistory Model """

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class TicketHistory(Model):
    """TicketHistory Model"""

    __table__ = "ticket_histories"

    __fillable__ = [
        "ticket_id",
        "changed_by_id",
        "event_type",
        "from_status",
        "to_status",
        "from_assignee_id",
        "to_assignee_id",
        "body"
    ]

    @belongs_to("ticket_id", "id")
    def ticket(self):
        from app.models.Ticket import Ticket
        return Ticket

    @belongs_to("changed_by_id", "id")
    def actor(self):
        from app.models.User import User
        return User

    @belongs_to("from_assignee_id", "id")
    def from_assignee(self):
        from app.models.User import User
        return User

    @belongs_to("to_assignee_id", "id")
    def to_assignee(self):
        from app.models.User import User
        return User
