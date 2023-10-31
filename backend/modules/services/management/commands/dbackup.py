from typing import Any 
from datetime import datetime

from django.core.management import BaseCommand, call_command



class DatabaseBackupCommand(BaseCommand):
    """
    Command to create a database backup
    """

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write('Waiting for database dump...')
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary', 
            '--exclude=contenttypes', 
            '--exclude=admin.logentry', 
            '--indent=4', 
            f'--output=database-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json'
        )
        self.stdout.write(self.style.SUCCESS('Database successfully backed up'))

        """
        This code is a custom Django command that performs a JSON backup of a database using the Django dumpdata command.

        The BaseCommand file from the django.core.management module is the base class for creating custom Django commands. 
        It defines the structure you need to use to create your own team.

        handle() is a required method for all Django custom commands and is called when the command is run.

        call_command() is a built-in Django function that calls other Django commands. In this case, we use call_command() 
        to call the dumpdata command with parameters that specify which models to exclude from the dump.

        In the parameter f'--output=database-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json' we specify the file name 
        for the output JSON -file, including the date and time the file was created.

        The self.stdout.write() method is used to write information to the standard output of the command line. After a 
        successful database backup, the self.stdout.write() method prints a success message using self.style.SUCCESS(), 
        which formats the output in green for easier readability.
        """