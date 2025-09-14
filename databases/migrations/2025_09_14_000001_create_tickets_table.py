"""CreateTicketsTable Migration (legacy placeholder for rollback)."""

from masoniteorm.migrations import Migration


class CreateTicketsTable(Migration):
    def up(self):
        """Legacy migration was creating tickets. Now a no-op to avoid duplicate creation."""
        pass

    def down(self):
        """Ensure tickets table can be dropped during refresh/reset."""
        if self.schema.has_table("tickets"):
            self.schema.drop("tickets")


