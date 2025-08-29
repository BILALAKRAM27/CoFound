from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Message
import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate messages between users'

    def handle(self, *args, **options):
        self.stdout.write('Populating messages...')
        
        # Get all users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        entrepreneurs = [u for u in users if u.role == 'entrepreneur']
        investors = [u for u in users if u.role == 'investor']
        
        if not entrepreneurs or not investors:
            self.stdout.write(self.style.ERROR('Need both entrepreneurs and investors to create messages.'))
            return
        
        # Sample message content for different scenarios
        investor_to_entrepreneur_messages = [
            "Hi! I came across your startup and I'm really impressed with your vision. Would love to learn more about your business model and discuss potential investment opportunities.",
            "Your company's approach to solving market problems is innovative. I'd like to schedule a call to discuss your growth strategy and funding needs.",
            "I'm actively investing in your industry and would love to explore partnership opportunities. Can we set up a meeting to discuss this further?",
            "Your startup shows great potential in the market. I'm interested in learning more about your team and technology. Would you be available for a call this week?",
            "I've been following your company's progress and I'm excited about your growth trajectory. Let's discuss how we can support your expansion plans.",
            "Your product looks really promising! I'd like to understand more about your market positioning and competitive advantages. Can we chat?",
            "I'm looking to invest in companies like yours. Your innovative approach to the market really stands out. Would love to discuss potential collaboration.",
            "Your startup's technology is impressive. I'm interested in learning more about your development roadmap and funding requirements.",
            "I'm excited about the potential of your company. Let's discuss your business model and see how we can work together.",
            "Your company's mission aligns perfectly with our investment thesis. Would love to explore investment opportunities and discuss your growth plans."
        ]
        
        entrepreneur_to_investor_messages = [
            "Hi! Thank you for your interest in our startup. I'd love to share more about our vision and discuss potential investment opportunities.",
            "We're currently raising our Series A round and would love to discuss this with you. Our platform has shown strong growth and market validation.",
            "Thank you for reaching out! We're looking for strategic investors who can help us scale. Would love to schedule a call to discuss our business model.",
            "We're excited about the opportunity to work with you. Our startup is at a critical growth stage and we're looking for the right partners.",
            "Hi! We're actively seeking investment to accelerate our growth. I'd love to share our pitch deck and discuss how we can work together.",
            "Thank you for your interest! We're building something revolutionary in the market and would love to discuss potential partnership opportunities.",
            "We're looking for investors who share our vision for the future. Would love to discuss our technology and growth strategy with you.",
            "Hi! We're at an exciting stage in our journey and looking for strategic investors. Let's discuss how we can collaborate.",
            "Thank you for reaching out! We're passionate about our mission and would love to discuss investment opportunities with you.",
            "We're building the future of our industry and looking for partners who share our vision. Would love to discuss potential collaboration."
        ]
        
        follow_up_messages = [
            "Looking forward to our meeting next week! I'll prepare a detailed presentation of our business model and financial projections.",
            "Thanks for the great conversation yesterday. I'm excited about the potential partnership and looking forward to next steps.",
            "I've sent over our updated pitch deck as discussed. Let me know if you need any additional information or have questions.",
            "Great meeting today! I'm looking forward to discussing the investment terms and moving forward with our partnership.",
            "Thanks for your time today. I'll follow up with the additional financial data you requested by the end of the week.",
            "I appreciate your feedback on our pitch. We're working on addressing the points you raised and will share updates soon.",
            "Looking forward to introducing you to our team next week. They're excited about the potential partnership opportunity.",
            "Thanks for the insightful questions during our call. I'm confident we can address all your concerns and move forward.",
            "Great discussion today! I'm excited about the potential investment and looking forward to finalizing the details.",
            "I've reviewed your investment proposal and I'm very interested. Let's schedule a follow-up call to discuss the terms."
        ]
        
        general_conversation_messages = [
            "How's everything going with your startup? Any exciting developments to share?",
            "I saw your recent post about the new feature launch. Congratulations! How are users responding?",
            "The market seems to be heating up in your space. How are you positioning yourself against the competition?",
            "I'm attending the tech conference next month. Will you be there? It would be great to meet in person.",
            "How's the fundraising process going? Any interesting conversations with other investors?",
            "I'm impressed with your team's growth. How are you managing the scaling challenges?",
            "The industry trends are really interesting right now. What's your take on the current market conditions?",
            "I enjoyed reading your latest blog post about industry insights. Very thought-provoking analysis.",
            "How are you finding the current investment climate? Any advice for other entrepreneurs in your space?",
            "I'm curious about your expansion plans. Which markets are you targeting next?"
        ]
        
        messages_created = 0
        
        # Create conversations between investors and entrepreneurs
        for investor in investors:
            # Each investor messages 3-5 entrepreneurs
            num_conversations = random.randint(3, min(5, len(entrepreneurs)))
            selected_entrepreneurs = random.sample(entrepreneurs, num_conversations)
            
            for entrepreneur in selected_entrepreneurs:
                # Create initial message from investor
                initial_message = random.choice(investor_to_entrepreneur_messages)
                message_date = timezone.now() - timedelta(days=random.randint(1, 30))
                
                Message.objects.create(
                    sender=investor,
                    receiver=entrepreneur,
                    content=initial_message,
                    timestamp=message_date,
                    is_read=random.choice([True, False]),
                    message_type='text'
                )
                messages_created += 1
                
                # Entrepreneur responds (80% chance)
                if random.random() < 0.8:
                    response_date = message_date + timedelta(hours=random.randint(1, 24))
                    response_message = random.choice(entrepreneur_to_investor_messages)
                    
                    Message.objects.create(
                        sender=entrepreneur,
                        receiver=investor,
                        content=response_message,
                        timestamp=response_date,
                        is_read=random.choice([True, False]),
                        message_type='text'
                    )
                    messages_created += 1
                    
                    # Follow-up message from investor (60% chance)
                    if random.random() < 0.6:
                        follow_up_date = response_date + timedelta(hours=random.randint(2, 48))
                        follow_up_message = random.choice(follow_up_messages)
                        
                        Message.objects.create(
                            sender=investor,
                            receiver=entrepreneur,
                            content=follow_up_message,
                            timestamp=follow_up_date,
                            is_read=random.choice([True, False]),
                            message_type='text'
                        )
                        messages_created += 1
                        
                        # Entrepreneur responds to follow-up (70% chance)
                        if random.random() < 0.7:
                            final_response_date = follow_up_date + timedelta(hours=random.randint(1, 12))
                            final_response = random.choice(follow_up_messages)
                            
                            Message.objects.create(
                                sender=entrepreneur,
                                receiver=investor,
                                content=final_response,
                                timestamp=final_response_date,
                                is_read=random.choice([True, False]),
                                message_type='text'
                            )
                            messages_created += 1
                
                # Occasionally add some general conversation messages
                if random.random() < 0.3:
                    conversation_date = message_date + timedelta(days=random.randint(2, 7))
                    conversation_message = random.choice(general_conversation_messages)
                    
                    # Random sender (either investor or entrepreneur)
                    sender = random.choice([investor, entrepreneur])
                    receiver = entrepreneur if sender == investor else investor
                    
                    Message.objects.create(
                        sender=sender,
                        receiver=receiver,
                        content=conversation_message,
                        timestamp=conversation_date,
                        is_read=random.choice([True, False]),
                        message_type='text'
                    )
                    messages_created += 1
        
        # Also create some messages initiated by entrepreneurs
        for entrepreneur in entrepreneurs:
            # Each entrepreneur initiates 1-3 conversations
            num_conversations = random.randint(1, min(3, len(investors)))
            selected_investors = random.sample(investors, num_conversations)
            
            for investor in selected_investors:
                # Check if conversation already exists
                if not Message.objects.filter(
                    Q(sender=entrepreneur, receiver=investor) | 
                    Q(sender=investor, receiver=entrepreneur)
                ).exists():
                    # Create initial message from entrepreneur
                    initial_message = random.choice(entrepreneur_to_investor_messages)
                    message_date = timezone.now() - timedelta(days=random.randint(1, 30))
                    
                    Message.objects.create(
                        sender=entrepreneur,
                        receiver=investor,
                        content=initial_message,
                        timestamp=message_date,
                        is_read=random.choice([True, False]),
                        message_type='text'
                    )
                    messages_created += 1
                    
                    # Investor responds (70% chance)
                    if random.random() < 0.7:
                        response_date = message_date + timedelta(hours=random.randint(2, 48))
                        response_message = random.choice(investor_to_entrepreneur_messages)
                        
                        Message.objects.create(
                            sender=investor,
                            receiver=entrepreneur,
                            content=response_message,
                            timestamp=response_date,
                            is_read=random.choice([True, False]),
                            message_type='text'
                        )
                        messages_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {messages_created} messages!'
            )
        )
        
        # Display statistics
        total_messages = Message.objects.count()
        unread_messages = Message.objects.filter(is_read=False).count()
        read_messages = Message.objects.filter(is_read=True).count()
        
        self.stdout.write(f'Total messages: {total_messages}')
        self.stdout.write(f'Read messages: {read_messages}')
        self.stdout.write(f'Unread messages: {unread_messages}')
        
        # Show some sample messages
        self.stdout.write('\nSample messages:')
        for message in Message.objects.all()[:5]:
            self.stdout.write(
                f'  {message.sender.get_full_name()} → {message.receiver.get_full_name()}: '
                f'{message.content[:50]}{"..." if len(message.content) > 50 else ""} '
                f'({"read" if message.is_read else "unread"})'
            )
