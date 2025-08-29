from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Favorite, CollaborationRequest
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate favorites (follows) and collaboration requests between users'

    def handle(self, *args, **options):
        self.stdout.write('Populating connections and collaboration requests...')
        
        # Get all users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        entrepreneurs = [u for u in users if u.role == 'entrepreneur']
        investors = [u for u in users if u.role == 'investor']
        
        if not entrepreneurs or not investors:
            self.stdout.write(self.style.ERROR('Need both entrepreneurs and investors to create connections.'))
            return
        
        favorites_created = 0
        collaboration_requests_created = 0
        
        # Sample collaboration request messages
        collaboration_messages = [
            "I'm interested in learning more about your startup and potential investment opportunities.",
            "Your company's vision aligns perfectly with our investment thesis. Would love to discuss collaboration.",
            "We're looking to invest in innovative companies like yours. Let's schedule a meeting to explore possibilities.",
            "Your startup shows great potential in the market. Interested in discussing funding options.",
            "We'd like to learn more about your business model and growth strategy for potential investment.",
            "Your company's technology is impressive. Would love to explore partnership opportunities.",
            "We're actively investing in your industry and would like to discuss potential collaboration.",
            "Your startup's approach to solving market problems is innovative. Let's explore investment opportunities.",
            "We're looking for promising companies to add to our portfolio. Would love to learn more about yours.",
            "Your company's growth trajectory is impressive. Interested in discussing investment and partnership."
        ]
        
        # Create favorites (follows) - realistic social network
        for user in users:
            # Each user follows 2-6 other users
            num_follows = random.randint(2, min(6, len(users) - 1))
            
            # Get potential users to follow (excluding self)
            potential_follows = [u for u in users if u != user]
            
            # Ensure some cross-role connections (entrepreneurs following investors and vice versa)
            if user.role == 'entrepreneur':
                # Entrepreneurs follow mostly investors, some other entrepreneurs
                investor_follows = random.randint(1, min(4, len(investors)))
                entrepreneur_follows = random.randint(0, min(2, len(entrepreneurs) - 1))
                
                # Select investors to follow
                selected_investors = random.sample(investors, investor_follows)
                for investor in selected_investors:
                    if not Favorite.objects.filter(user=user, target_user=investor).exists():
                        Favorite.objects.create(user=user, target_user=investor)
                        favorites_created += 1
                
                # Select entrepreneurs to follow
                if entrepreneur_follows > 0:
                    other_entrepreneurs = [u for u in entrepreneurs if u != user]
                    if other_entrepreneurs:
                        selected_entrepreneurs = random.sample(other_entrepreneurs, min(entrepreneur_follows, len(other_entrepreneurs)))
                        for entrepreneur in selected_entrepreneurs:
                            if not Favorite.objects.filter(user=user, target_user=entrepreneur).exists():
                                Favorite.objects.create(user=user, target_user=entrepreneur)
                                favorites_created += 1
                                
            else:  # investor
                # Investors follow mostly entrepreneurs, some other investors
                entrepreneur_follows = random.randint(2, min(5, len(entrepreneurs)))
                investor_follows = random.randint(0, min(2, len(investors) - 1))
                
                # Select entrepreneurs to follow
                selected_entrepreneurs = random.sample(entrepreneurs, entrepreneur_follows)
                for entrepreneur in selected_entrepreneurs:
                    if not Favorite.objects.filter(user=user, target_user=entrepreneur).exists():
                        Favorite.objects.create(user=user, target_user=entrepreneur)
                        favorites_created += 1
                
                # Select investors to follow
                if investor_follows > 0:
                    other_investors = [u for u in investors if u != user]
                    if other_investors:
                        selected_investors = random.sample(other_investors, min(investor_follows, len(other_investors)))
                        for investor in selected_investors:
                            if not Favorite.objects.filter(user=user, target_user=investor).exists():
                                Favorite.objects.create(user=user, target_user=investor)
                                favorites_created += 1
        
        # Create collaboration requests
        for investor in investors:
            # Each investor sends 2-4 collaboration requests
            num_requests = random.randint(2, min(4, len(entrepreneurs)))
            
            # Select random entrepreneurs
            selected_entrepreneurs = random.sample(entrepreneurs, num_requests)
            
            for entrepreneur in selected_entrepreneurs:
                # Check if request already exists
                if not CollaborationRequest.objects.filter(investor=investor, entrepreneur=entrepreneur).exists():
                    # Random status (mostly pending, some accepted/rejected)
                    status_weights = {'pending': 0.6, 'accepted': 0.3, 'rejected': 0.1}
                    status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
                    
                    message = random.choice(collaboration_messages)
                    
                    CollaborationRequest.objects.create(
                        investor=investor,
                        entrepreneur=entrepreneur,
                        message=message,
                        status=status
                    )
                    collaboration_requests_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {favorites_created} favorites and {collaboration_requests_created} collaboration requests!'
            )
        )
        
        # Display statistics
        total_favorites = Favorite.objects.count()
        total_collaboration_requests = CollaborationRequest.objects.count()
        pending_requests = CollaborationRequest.objects.filter(status='pending').count()
        accepted_requests = CollaborationRequest.objects.filter(status='accepted').count()
        rejected_requests = CollaborationRequest.objects.filter(status='rejected').count()
        
        self.stdout.write(f'Total favorites (follows): {total_favorites}')
        self.stdout.write(f'Total collaboration requests: {total_collaboration_requests}')
        self.stdout.write(f'Pending requests: {pending_requests}')
        self.stdout.write(f'Accepted requests: {accepted_requests}')
        self.stdout.write(f'Rejected requests: {rejected_requests}')
        
        # Show some sample connections
        self.stdout.write('\nSample favorites:')
        for favorite in Favorite.objects.all()[:5]:
            self.stdout.write(f'  {favorite.user.get_full_name()} follows {favorite.target_user.get_full_name()}')
        
        self.stdout.write('\nSample collaboration requests:')
        for request in CollaborationRequest.objects.all()[:5]:
            self.stdout.write(f'  {request.investor.get_full_name()} → {request.entrepreneur.get_full_name()}: {request.status}')
