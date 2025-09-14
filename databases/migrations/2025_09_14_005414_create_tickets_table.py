"""CreateTicketsTable Migration."""

from masoniteorm.migrations import Migration


class CreateTicketsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("tickets") as table:
            table.increments("id")
            table.string("title", length=255)
            table.text("description").nullable()
            table.string("status", length=32).default("open")
            table.integer("assignee_id").nullable().unsigned()
            table.timestamps()

        with self.schema.table("tickets") as table:
            table.index(["status"])  # filter by status
            table.index(["assignee_id"])  # filter by assignee

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("tickets")
