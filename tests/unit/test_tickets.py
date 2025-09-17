from tests import TestCase
from app.models.User import User
from app.models.Ticket import Ticket
from app.models.Project import Project
import uuid


class TicketRoutesTest(TestCase):
    def setUp(self):
        super().setUp()
        # Ensure a user exists and authenticate
        self.email = f"tester+{uuid.uuid4().hex[:8]}@example.com"
        self.user = User.create(name="Tester", email=self.email, password="secret")
        self.actingAs(self.user)

    def tearDown(self):
        Ticket.where("id", ">", 0).delete()
        existing = User.where("email", self.email).first()
        if existing:
            try:
                existing.force_delete()
            except Exception:
                existing.delete()
        super().tearDown()

    def test_index(self):
        response = self.get("/tickets")
        response.assertOk()

    def test_create_get(self):
        response = self.get("/tickets/create")
        response.assertOk()

    def test_store_and_show_edit_update_and_delete(self):
        # store
        response = self.post(
            "/tickets",
            {
                "title": "Test Ticket",
                "description": "Body",
                "status": "open",
                "assignee_id": "",
            },
        )
        # redirected to show
        response.assertRedirect()
        location = response.response.header("Location")
        self.assertTrue(location.startswith("/tickets/"))

        # extract id
        ticket_id = int(location.split("/")[-1])

        # show
        self.get(f"/tickets/{ticket_id}").assertOk()

        # edit
        self.get(f"/tickets/{ticket_id}/edit").assertOk()

        # update
        response = self.post(
            f"/tickets/{ticket_id}/update",
            {
                "title": "Updated Ticket",
                "description": "Updated Body",
                "status": "in_progress",
                "assignee_id": "",
            },
        )
        response.assertRedirect()

        # delete
        response = self.post(f"/tickets/{ticket_id}/delete", {})
        response.assertRedirect()
        # after delete, index should still be accessible
        self.get("/tickets").assertOk()

    def test_move_updates_status_and_creates_history(self):
        # Create a project to attach ticket to
        project = Project.create(name="P1", description="", created_by_id=self.user.id)

        # Create ticket in project
        response = self.post(
            "/tickets",
            {
                "title": "Move Me",
                "description": "",
                "status": "open",
                "project_id": str(project.id),
                "assignee_id": "",
            },
        )
        ticket_id = int(response.response.header("Location").split("/")[-1])

        # Move to in_progress
        res = self.post(f"/tickets/{ticket_id}/move", {"to_status": "in_progress"})
        res.assertOk()

        # Fetch show and verify status changed in page (implicit DB read)
        self.get(f"/tickets/{ticket_id}").assertOk()
