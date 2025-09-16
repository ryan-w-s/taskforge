"""AddProjectIdToTicketsTable Migration."""

from masoniteorm.migrations import Migration


class AddProjectIdToTicketsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("tickets") as table:
            table.integer("project_id").nullable().unsigned()

        # Index (omit FK on SQLite to avoid table rebuild issues during alter)
        with self.schema.table("tickets") as table:
            table.index(["project_id"])  # filter by project

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("tickets") as table:
            table.drop_column("project_id")
