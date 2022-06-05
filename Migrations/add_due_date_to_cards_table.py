from orator.migrations import Migration


class AddDueDateToCardsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('users') as table:
            table.increments('id')
            table.timestamps()
            pass

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('cards') as table:
            pass
    