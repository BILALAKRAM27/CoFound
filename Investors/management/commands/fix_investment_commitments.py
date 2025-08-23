from django.core.management.base import BaseCommand
from Investors.models import InvestmentCommitment
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix InvestmentCommitment records with string amounts'

    def handle(self, *args, **options):
        self.stdout.write('Checking for InvestmentCommitment records with string amounts...')
        
        # Get all commitments
        commitments = InvestmentCommitment.objects.all()
        fixed_count = 0
        
        for commitment in commitments:
            try:
                # Try to access the amount - if it's a string, this will cause issues
                current_amount = commitment.amount
                
                # If it's already a Decimal, skip
                if isinstance(current_amount, Decimal):
                    continue
                
                # Convert to Decimal and save
                try:
                    decimal_amount = Decimal(str(current_amount))
                    commitment.amount = decimal_amount
                    commitment.save(update_fields=['amount'])
                    fixed_count += 1
                    self.stdout.write(f'Fixed commitment {commitment.id}: {current_amount} -> {decimal_amount}')
                except (ValueError, TypeError) as e:
                    self.stdout.write(self.style.ERROR(f'Could not convert amount for commitment {commitment.id}: {current_amount} - {e}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing commitment {commitment.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} InvestmentCommitment records'))
        self.stdout.write('Done!')
