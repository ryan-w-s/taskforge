"""CreateTicketHistoriesTable Migration."""

from masoniteorm.migrations import Migration


class CreateTicketHistoriesTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("ticket_histories") as table:
            table.increments("id")
            table.integer("ticket_id").unsigned()
            table.integer("changed_by_id").unsigned().nullable()
            table.string("event_type")
            table.string("from_status").nullable()
            table.string("to_status").nullable()
            table.integer("from_assignee_id").unsigned().nullable()
            table.integer("to_assignee_id").unsigned().nullable()
            table.text("body").nullable()
            table.timestamps()
            # Foreign key constraints (define during creation on SQLite)
            table.foreign("ticket_id").references("id").on("tickets")
            table.foreign("changed_by_id").references("id").on("users")
            table.foreign("from_assignee_id").references("id").on("users")
            table.foreign("to_assignee_id").references("id").on("users")

        with self.schema.table("ticket_histories") as table:
            # Indexes for performance
            table.index("ticket_id")
            table.index("created_at")

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("ticket_histories")
