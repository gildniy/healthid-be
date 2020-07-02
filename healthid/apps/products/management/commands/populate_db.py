# 
# Write a script to set the outlet_id of all existing batches 
# to the assigned outlet of the user who created them.
# 
from django.core.management.base import BaseCommand
from healthid.apps.products.models import BatchInfo
from healthid.apps.outlets.models import OutletUser

class Command(BaseCommand):
    args = 'No Arguments'
    help = 'A helper function to help populate the BatchInfo outlet_id to that of the user who created it'

    def _update_outlet_id(self):
        # firstly get all the batchinfo objects
        batches = BatchInfo.objects.all()
        error_count = success_count = 0

        for batch in batches:
            # update the outlet_id with that of the assigned outlet of the user who created them
            user_id=batch.user_id
            user_first_assigned_outlet = OutletUser.objects.filter(
                user_id=user_id
            ).first()
            try:
                batch.outlet_id = user_first_assigned_outlet.outlet_id
                batch.save()
                success_count += 1
            except:
                error_count += 1
            
        print(f"Added {success_count}, there were {error_count} errors")

    def handle(self, *args, **options):
        self._update_outlet_id()
