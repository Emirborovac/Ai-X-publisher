import os
import pandas as pd
from django.core.management.base import BaseCommand
from X.models import WebsiteInput

class Command(BaseCommand):
    help = 'Import data from website_input.xlsx into the WebsiteInput model'

    def handle(self, *args, **kwargs):
        # Define the path to the Excel file
        excel_path = os.path.join('C:\\Users\\Ymir\\Desktop\\Git Adventure\\Twitter Poster\\Project-X-Ai-publisher', 'website_input.xlsx')

        # Read the Excel file into a DataFrame
        df = pd.read_excel(excel_path)

        # Iterate through the DataFrame and save each row to the database
        for _, row in df.iterrows():
            WebsiteInput.objects.create(
                url=row['URL'],
                selectors=row['Selectors']
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported website input data into the database.'))
