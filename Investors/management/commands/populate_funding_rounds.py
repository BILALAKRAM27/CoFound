from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Investors.models import FundingRound, InvestmentCommitment
from Entrepreneurs.models import Startup
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate funding rounds and investment commitments'

    def handle(self, *args, **options):
        self.stdout.write('Populating funding rounds and investments...')
        
        # Get all startups and investors
        startups = list(Startup.objects.all())
        investors = list(User.objects.filter(role='investor'))
        
        if not startups:
            self.stdout.write(self.style.ERROR('No startups found. Please create entrepreneurs and startups first.'))
            return
        
        if not investors:
            self.stdout.write(self.style.ERROR('No investors found. Please create investors first.'))
            return
        
        # Sample funding round names
        round_names = [
            "Seed Round", "Series A", "Series B", "Series C", "Growth Round",
            "Bridge Round", "Pre-Series A", "Series A Extension", "Strategic Round"
        ]
        
        # Sample meeting locations
        meeting_locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
            "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
            "Miami, FL", "Portland, OR", "Video Call", "Phone Call"
        ]
        
        funding_rounds_created = 0
        investments_created = 0
        
        # Create funding rounds for each startup
        for startup in startups:
            # Create 1-3 funding rounds per startup
            num_rounds = random.randint(1, 3)
            
            for round_num in range(num_rounds):
                # Determine round type based on sequence
                if round_num == 0:
                    round_name = "Seed Round"
                    target_goal = Decimal(random.randint(100000, 1000000))
                    equity_offered = Decimal(random.uniform(5.0, 15.0))
                elif round_num == 1:
                    round_name = "Series A"
                    target_goal = Decimal(random.randint(1000000, 5000000))
                    equity_offered = Decimal(random.uniform(10.0, 25.0))
                else:
                    round_name = "Series B"
                    target_goal = Decimal(random.randint(5000000, 20000000))
                    equity_offered = Decimal(random.uniform(15.0, 35.0))
                
                # Random deadline within next 6 months
                deadline = timezone.now() + timedelta(days=random.randint(30, 180))
                
                # Random status (mostly active, some successful/failed)
                status_weights = {'active': 0.7, 'successful': 0.2, 'failed': 0.1}
                status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
                
                # Create funding round
                funding_round = FundingRound.objects.create(
                    startup=startup,
                    round_name=round_name,
                    target_goal=target_goal,
                    equity_offered=equity_offered,
                    deadline=deadline,
                    status=status
                )
                funding_rounds_created += 1
                
                # Add random investment commitments
                if status == 'active':
                    # For active rounds, add 0-5 investments
                    num_investments = random.randint(0, min(5, len(investors)))
                elif status == 'successful':
                    # For successful rounds, add enough investments to meet the goal
                    num_investments = random.randint(3, min(8, len(investors)))
                else:
                    # For failed rounds, add 0-2 investments (below goal)
                    num_investments = random.randint(0, min(2, len(investors)))
                
                if num_investments > 0:
                    # Select random investors
                    selected_investors = random.sample(investors, num_investments)
                    
                    for investor in selected_investors:
                        # Calculate investment amount
                        if status == 'successful':
                            # For successful rounds, ensure we meet the goal
                            if investor == selected_investors[-1]:  # Last investor
                                # Calculate remaining amount needed
                                committed_so_far = sum(
                                    ic.amount for ic in funding_round.investments.all()
                                )
                                remaining = target_goal - committed_so_far
                                if remaining > 0:
                                    amount = remaining
                                else:
                                    max_amount = max(100000, int(target_goal * Decimal('0.3')))
                                    amount = Decimal(random.randint(100000, max_amount))
                            else:
                                # Random amount up to 30% of goal
                                max_amount = max(100000, int(target_goal * Decimal('0.3')))
                                amount = Decimal(random.randint(100000, max_amount))
                        else:
                            # For active/failed rounds, random amount
                            max_amount = max(50000, int(target_goal * Decimal('0.4')))
                            amount = Decimal(random.randint(50000, max_amount))
                        
                        # Create investment commitment
                        InvestmentCommitment.objects.create(
                            funding_round=funding_round,
                            investor=investor,
                            amount=amount
                        )
                        investments_created += 1
                
                self.stdout.write(f'  Created {round_name} for {startup.name}: ${target_goal:,} goal, {equity_offered}% equity')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {funding_rounds_created} funding rounds and {investments_created} investment commitments!'
            )
        )
        
        # Display statistics
        total_rounds = FundingRound.objects.count()
        total_investments = InvestmentCommitment.objects.count()
        active_rounds = FundingRound.objects.filter(status='active').count()
        successful_rounds = FundingRound.objects.filter(status='successful').count()
        failed_rounds = FundingRound.objects.filter(status='failed').count()
        
        self.stdout.write(f'Total funding rounds: {total_rounds}')
        self.stdout.write(f'Total investments: {total_investments}')
        self.stdout.write(f'Active rounds: {active_rounds}')
        self.stdout.write(f'Successful rounds: {successful_rounds}')
        self.stdout.write(f'Failed rounds: {failed_rounds}')
        
        # Show some sample rounds
        self.stdout.write('\nSample funding rounds:')
        for round_obj in FundingRound.objects.all()[:5]:
            total_committed = round_obj.total_committed()
            percent_raised = (total_committed / round_obj.target_goal * 100) if round_obj.target_goal > 0 else 0
            self.stdout.write(
                f'  {round_obj.round_name} - {round_obj.startup.name}: '
                f'${total_committed:,} / ${round_obj.target_goal:,} ({percent_raised:.1f}%) - {round_obj.status}'
            )
