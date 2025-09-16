"""CreateProjectsTable Migration."""

from masoniteorm.migrations import Migration


class CreateProjectsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("projects") as table:
            table.increments("id")
            table.string("name", length=255)
            table.text("description").nullable()
            table.integer("created_by_id").unsigned()

            table.timestamps()

            # Foreign keys
            table.foreign("created_by_id").references("id").on("users")

        # Indexes
        with self.schema.table("projects") as table:
            table.index(["name"])  # search by name
            table.index(["created_by_id"])  # filter by creator

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("projects")
