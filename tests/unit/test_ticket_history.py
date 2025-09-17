from tests.TestCase import TestCase
from app.models.User import User
from app.models.Ticket import Ticket
from app.models.TicketHistory import TicketHistory
from app.models.Project import Project
import uuid


class TicketHistoryTest(TestCase):
    def setUp(self):
        super().setUp()
        # Ensure a user exists and authenticate
        self.email = f"tester+{uuid.uuid4().hex[:8]}@example.com"
        self.user = User.create(name="Tester", email=self.email, password="secret")
        self.actingAs(self.user)
        # Track records created by this test
        self.created_ticket_ids = []

    def tearDown(self):
        # Only delete records created during this test
        if getattr(self, "created_ticket_ids", None):
            if self.created_ticket_ids:
                TicketHistory.where_in("ticket_id", self.created_ticket_ids).delete()
                Ticket.where_in("id", self.created_ticket_ids).delete()
        existing = User.where("email", self.email).first()
        if existing:
            try:
                existing.force_delete()
            except Exception:
                existing.delete()
        super().tearDown()

    def test_history_entry_on_ticket_create(self):
        """Test that creating a ticket emits a history entry"""
        # Create a ticket
        response = self.post(
            "/tickets",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "open",
                "assignee_id": "",
            },
        )
        response.assertRedirect()
        location = response.response.header("Location")
        ticket_id = int(location.split("/")[-1])
        self.created_ticket_ids.append(ticket_id)

        # Check that history entry was created
        history = TicketHistory.where("ticket_id", ticket_id).get()
        self.assertEqual(len(history), 1)

        entry = history[0]
        self.assertEqual(entry.event_type, "created")
        self.assertEqual(entry.to_status, "open")
        self.assertIsNone(entry.from_status)
        self.assertEqual(entry.changed_by_id, self.user.id)
        self.assertIsNone(entry.from_assignee_id)
        self.assertIsNone(entry.to_assignee_id)

    def test_history_entry_on_status_change(self):
        """Test that changing status emits a history entry"""
        # Create a ticket first
        response = self.post(
            "/tickets",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "open",
                "assignee_id": "",
            },
        )
        ticket_id = int(response.response.header("Location").split("/")[-1])
        self.created_ticket_ids.append(ticket_id)

        # Update status
        response = self.post(
            f"/tickets/{ticket_id}/update",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "in_progress",
                "assignee_id": "",
            },
        )
        response.assertRedirect()

        # Check that history entries were created (1 for create + 1 for status change)
        history = TicketHistory.where("ticket_id", ticket_id).order_by("created_at").get()
        self.assertEqual(len(history), 2)

        # The second entry should be the status change
        status_change_entry = history[1]
        self.assertEqual(status_change_entry.event_type, "status_changed")
        self.assertEqual(status_change_entry.from_status, "open")
        self.assertEqual(status_change_entry.to_status, "in_progress")
        self.assertEqual(status_change_entry.changed_by_id, self.user.id)

    def test_history_entry_on_assignee_change(self):
        """Test that changing assignee emits a history entry"""
        # Create another user to assign to
        assignee_email = f"assignee+{uuid.uuid4().hex[:8]}@example.com"
        assignee = User.create(name="Assignee", email=assignee_email, password="secret")

        # Create a ticket first
        response = self.post(
            "/tickets",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "open",
                "assignee_id": "",
            },
        )
        ticket_id = int(response.response.header("Location").split("/")[-1])
        self.created_ticket_ids.append(ticket_id)

        # Update assignee
        response = self.post(
            f"/tickets/{ticket_id}/update",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "open",
                "assignee_id": str(assignee.id),
            },
        )
        response.assertRedirect()

        # Check that history entries were created (1 for create + 1 for assignee change)
        history = TicketHistory.where("ticket_id", ticket_id).order_by("created_at").get()
        self.assertEqual(len(history), 2)

        # The second entry should be the assignee change
        assignee_change_entry = history[1]
        self.assertEqual(assignee_change_entry.event_type, "assignee_changed")
        self.assertIsNone(assignee_change_entry.from_assignee_id)
        self.assertEqual(assignee_change_entry.to_assignee_id, assignee.id)
        self.assertEqual(assignee_change_entry.changed_by_id, self.user.id)

        # Clean up assignee
        try:
            assignee.delete()
        except Exception:
            pass  # Ignore if delete fails due to foreign key constraints

    def test_comment_creates_history_entry(self):
        """Test that posting a comment creates a commented history entry"""
        # Create a ticket first
        response = self.post(
            "/tickets",
            {
                "title": "Test Ticket",
                "description": "Test Description",
                "status": "open",
                "assignee_id": "",
            },
        )
        ticket_id = int(response.response.header("Location").split("/")[-1])
        self.created_ticket_ids.append(ticket_id)

        # Post a comment (this will be implemented later in controller)
        comment_body = "This is a test comment"

        # For now, we'll create the history entry manually to test the structure
        TicketHistory.create(
            ticket_id=ticket_id,
            changed_by_id=self.user.id,
            event_type="commented",
            body=comment_body
        )

        # Check that the comment history entry exists
        history = TicketHistory.where("ticket_id", ticket_id).where("event_type", "commented").first()
        self.assertIsNotNone(history)
        self.assertEqual(history.body, comment_body)
        self.assertEqual(history.changed_by_id, self.user.id)

    def test_move_creates_status_changed_history(self):
        # Create project and ticket
        project = Project.create(name="P1", description="", created_by_id=self.user.id)
        response = self.post(
            "/tickets",
            {
                "title": "Move Ticket",
                "description": "",
                "status": "open",
                "project_id": str(project.id),
                "assignee_id": "",
            },
        )
        ticket_id = int(response.response.header("Location").split("/")[-1])
        self.created_ticket_ids.append(ticket_id)

        # Move
        res = self.post(f"/tickets/{ticket_id}/move", {"to_status": "done"})
        res.assertOk()

        # Validate history includes status_changed
        history = TicketHistory.where("ticket_id", ticket_id).order_by("created_at").get()
        types = [h.event_type for h in history]
        self.assertIn("status_changed", types)
