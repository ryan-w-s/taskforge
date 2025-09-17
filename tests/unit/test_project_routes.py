from tests.TestCase import TestCase
from app.models.User import User
from app.models.Project import Project
import uuid


class ProjectRoutesTest(TestCase):
    def setUp(self):
        super().setUp()
        self.email = f"tester+{uuid.uuid4().hex[:8]}@example.com"
        self.user = User.create(name="Tester", email=self.email, password="secret")
        self.actingAs(self.user)

    def tearDown(self):
        Project.where("id", ">", 0).delete()
        existing = User.where("email", self.email).first()
        if existing:
            try:
                existing.force_delete()
            except Exception:
                existing.delete()
        super().tearDown()

    def test_index_auth(self):
        response = self.get("/projects")
        response.assertOk()

    def test_crud_flow(self):
        # Create
        response = self.post(
            "/projects",
            {
                "name": "Alpha",
                "description": "First project",
            },
        )
        response.assertRedirect()
        location = response.response.header("Location")
        self.assertTrue(location.startswith("/projects/"))
        project_id = int(location.split("/")[-1])

        # Show
        self.get(f"/projects/{project_id}").assertOk()

        # Board
        self.get(f"/projects/{project_id}/board").assertOk()

        # Edit
        self.get(f"/projects/{project_id}/edit").assertOk()

        # Update
        response = self.post(
            f"/projects/{project_id}/update",
            {
                "name": "Alpha Updated",
                "description": "Updated",
            },
        )
        response.assertRedirect()

        # Delete (should work if no tickets)
        response = self.post(f"/projects/{project_id}/delete", {})
        response.assertRedirect()
