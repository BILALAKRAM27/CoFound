from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Meeting
import random
from datetime import timedelta, time
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate meetings between entrepreneurs and investors'

    def handle(self, *args, **options):
        self.stdout.write('Populating meetings...')
        
        # Get all users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        entrepreneurs = [u for u in users if u.role == 'entrepreneur']
        investors = [u for u in users if u.role == 'investor']
        
        if not entrepreneurs or not investors:
            self.stdout.write(self.style.ERROR('Need both entrepreneurs and investors to create meetings.'))
            return
        
        # Sample meeting titles
        meeting_titles = [
            "Initial Investment Discussion",
            "Startup Pitch Meeting",
            "Due Diligence Review",
            "Partnership Discussion",
            "Funding Round Negotiation",
            "Strategic Planning Session",
            "Market Analysis Review",
            "Team Introduction Meeting",
            "Product Demo and Q&A",
            "Business Model Discussion",
            "Growth Strategy Planning",
            "Exit Strategy Discussion",
            "Board Meeting",
            "Advisory Session",
            "Networking Introduction"
        ]
        
        # Sample meeting descriptions
        meeting_descriptions = [
            "Discussing potential investment opportunities and exploring partnership possibilities.",
            "Presenting our startup vision and business model to potential investors.",
            "Deep dive into our financials, market analysis, and growth projections.",
            "Exploring strategic partnership opportunities and collaboration areas.",
            "Negotiating terms for our upcoming funding round and investment structure.",
            "Strategic planning session to align on business objectives and milestones.",
            "Reviewing market analysis, competitive landscape, and growth opportunities.",
            "Introducing our team and discussing key roles and responsibilities.",
            "Product demonstration and addressing investor questions and concerns.",
            "Detailed discussion of our business model, revenue streams, and monetization strategy.",
            "Planning growth strategies and expansion into new markets.",
            "Discussing potential exit strategies and long-term vision for the company.",
            "Regular board meeting to review progress and discuss strategic decisions.",
            "Advisory session to get expert guidance on business challenges and opportunities.",
            "Initial networking meeting to explore potential collaboration opportunities."
        ]
        
        # Sample meeting locations
        meeting_locations = [
            "San Francisco, CA - Venture Capital Office",
            "New York, NY - Conference Room",
            "Austin, TX - Startup Incubator",
            "Seattle, WA - Tech Hub",
            "Boston, MA - Innovation Center",
            "Los Angeles, CA - Creative Office",
            "Chicago, IL - Business District",
            "Denver, CO - Tech Campus",
            "Miami, FL - Innovation Hub",
            "Portland, OR - Creative Space",
            "Zoom Video Call",
            "Google Meet",
            "Microsoft Teams",
            "Phone Call",
            "Coffee Shop Meeting"
        ]
        
        # Meeting types
        meeting_types = ['in_person', 'video_call', 'phone_call']
        
        # Status choices
        status_choices = ['pending', 'confirmed', 'rejected', 'cancelled']
        
        meetings_created = 0
        
        # Create meetings
        for investor in investors:
            # Each investor schedules 3-6 meetings
            num_meetings = random.randint(3, min(6, len(entrepreneurs)))
            
            # Select random entrepreneurs
            selected_entrepreneurs = random.sample(entrepreneurs, num_meetings)
            
            for entrepreneur in selected_entrepreneurs:
                # Check if meeting already exists
                if not Meeting.objects.filter(organizer=investor, participant=entrepreneur).exists():
                    # Random meeting date within next 3 months
                    meeting_date = timezone.now().date() + timedelta(days=random.randint(1, 90))
                    
                    # Random meeting time (9 AM to 6 PM)
                    hour = random.randint(9, 17)
                    minute = random.choice([0, 15, 30, 45])
                    meeting_time = time(hour, minute)
                    
                    # Random duration (30, 45, 60, 90 minutes)
                    duration = random.choice([30, 45, 60, 90])
                    
                    # Random status (mostly pending, some confirmed)
                    status_weights = {'pending': 0.5, 'confirmed': 0.3, 'rejected': 0.15, 'cancelled': 0.05}
                    status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
                    
                    # Random meeting type
                    meeting_type = random.choice(meeting_types)
                    
                    # Select title and description
                    title = random.choice(meeting_titles)
                    description = random.choice(meeting_descriptions)
                    location = random.choice(meeting_locations)
                    
                    # Create meeting
                    Meeting.objects.create(
                        organizer=investor,
                        participant=entrepreneur,
                        title=title,
                        description=description,
                        date=meeting_date,
                        time=meeting_time,
                        duration=duration,
                        status=status,
                        location=location,
                        meeting_type=meeting_type
                    )
                    meetings_created += 1
                    
                    self.stdout.write(
                        f'  Created meeting: {investor.get_full_name()} → {entrepreneur.get_full_name()} '
                        f'({title}) - {status} on {meeting_date}'
                    )
        
        # Also create some meetings initiated by entrepreneurs
        for entrepreneur in entrepreneurs:
            # Each entrepreneur schedules 1-3 meetings
            num_meetings = random.randint(1, min(3, len(investors)))
            
            # Select random investors
            selected_investors = random.sample(investors, num_meetings)
            
            for investor in selected_investors:
                # Check if meeting already exists (in either direction)
                if not Meeting.objects.filter(
                    Q(organizer=entrepreneur, participant=investor) | 
                    Q(organizer=investor, participant=entrepreneur)
                ).exists():
                    # Random meeting date within next 3 months
                    meeting_date = timezone.now().date() + timedelta(days=random.randint(1, 90))
                    
                    # Random meeting time (9 AM to 6 PM)
                    hour = random.randint(9, 17)
                    minute = random.choice([0, 15, 30, 45])
                    meeting_time = time(hour, minute)
                    
                    # Random duration (30, 45, 60, 90 minutes)
                    duration = random.choice([30, 45, 60, 90])
                    
                    # Random status (mostly pending, some confirmed)
                    status_weights = {'pending': 0.6, 'confirmed': 0.25, 'rejected': 0.1, 'cancelled': 0.05}
                    status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
                    
                    # Random meeting type
                    meeting_type = random.choice(meeting_types)
                    
                    # Select title and description
                    title = random.choice(meeting_titles)
                    description = random.choice(meeting_descriptions)
                    location = random.choice(meeting_locations)
                    
                    # Create meeting
                    Meeting.objects.create(
                        organizer=entrepreneur,
                        participant=investor,
                        title=title,
                        description=description,
                        date=meeting_date,
                        time=meeting_time,
                        duration=duration,
                        status=status,
                        location=location,
                        meeting_type=meeting_type
                    )
                    meetings_created += 1
                    
                    self.stdout.write(
                        f'  Created meeting: {entrepreneur.get_full_name()} → {investor.get_full_name()} '
                        f'({title}) - {status} on {meeting_date}'
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {meetings_created} meetings!'
            )
        )
        
        # Display statistics
        total_meetings = Meeting.objects.count()
        pending_meetings = Meeting.objects.filter(status='pending').count()
        confirmed_meetings = Meeting.objects.filter(status='confirmed').count()
        rejected_meetings = Meeting.objects.filter(status='rejected').count()
        cancelled_meetings = Meeting.objects.filter(status='cancelled').count()
        
        self.stdout.write(f'Total meetings: {total_meetings}')
        self.stdout.write(f'Pending meetings: {pending_meetings}')
        self.stdout.write(f'Confirmed meetings: {confirmed_meetings}')
        self.stdout.write(f'Rejected meetings: {rejected_meetings}')
        self.stdout.write(f'Cancelled meetings: {cancelled_meetings}')
        
        # Show some sample meetings
        self.stdout.write('\nSample meetings:')
        for meeting in Meeting.objects.all()[:5]:
            self.stdout.write(
                f'  {meeting.organizer.get_full_name()} → {meeting.participant.get_full_name()}: '
                f'{meeting.title} ({meeting.status}) on {meeting.date}'
            )
