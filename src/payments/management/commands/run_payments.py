from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        '''
        Run Payments process directly
        '''
        from payments.tasks import auto_payments
        auto_payments()
