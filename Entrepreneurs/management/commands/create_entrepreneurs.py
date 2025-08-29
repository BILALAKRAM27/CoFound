from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import EntrepreneurProfile, Startup, StartupDocument, Industry
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 10 entrepreneur users with realistic profiles and startups'

    def handle(self, *args, **options):
        self.stdout.write('Creating entrepreneur users...')
        
        # Sample data for realistic profiles
        company_names = [
            "TechFlow Solutions", "InnovateHub", "FutureTech Labs", "SmartStart Inc", 
            "Digital Ventures", "NextGen Systems", "EcoTech Innovations", "DataSphere", 
            "CloudBridge", "QuantumLeap Tech"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", 
            "Boston, MA", "Denver, CO", "Miami, FL", "Chicago, IL", 
            "Los Angeles, CA", "Portland, OR"
        ]
        
        industries = [
            'ai', 'fintech', 'healthtech', 'enterprise_saas', 'logistics', 
            'quantum', 'insurtech', 'spacetech', 'creator_tools', 'cleantech'
        ]
        
        company_stages = ['idea', 'mvp', 'early', 'growth', 'scale']
        funding_needs = ['seed', 'series_a', 'series_b', 'series_c', 'other']
        team_sizes = ['1', '2-5', '6-10', '11-25', '26-50']
        revenue_ranges = ['no_revenue', '0-10k', '10k-100k', '100k-1m', '1m-10m']
        funding_ranges = ['no_funding', '0-50k', '50k-500k', '500k-5m', '5m-50m']
        valuation_ranges = ['0-1m', '1m-10m', '10m-100m', '100m-1b', '1b+']
        
        # Sample bios
        bios = [
            "Passionate entrepreneur building the future of technology. Focused on creating innovative solutions that solve real-world problems.",
            "Serial entrepreneur with 10+ years of experience in building and scaling tech companies. Committed to driving positive change.",
            "Tech enthusiast and startup founder dedicated to revolutionizing how businesses operate in the digital age.",
            "Innovation-driven entrepreneur building sustainable technology solutions for tomorrow's challenges.",
            "Experienced founder with a track record of successful exits. Building the next generation of enterprise software.",
            "Visionary entrepreneur focused on AI and machine learning applications that transform industries.",
            "Startup founder passionate about fintech innovation and making financial services accessible to everyone.",
            "Healthcare technology entrepreneur committed to improving patient outcomes through innovative digital solutions.",
            "Clean energy advocate building sustainable technology solutions for a greener future.",
            "Space technology entrepreneur working on the next frontier of human exploration and innovation."
        ]
        
        # Sample startup descriptions
        startup_descriptions = [
            "Revolutionary AI-powered platform that automates complex business processes and increases efficiency by 300%.",
            "Next-generation fintech solution that democratizes access to investment opportunities and financial planning tools.",
            "Cutting-edge healthtech platform that uses machine learning to provide personalized healthcare recommendations.",
            "Enterprise SaaS solution that streamlines workflow management and team collaboration for remote and hybrid teams.",
            "Innovative logistics platform that optimizes supply chain operations and reduces costs by up to 40%.",
            "Quantum computing software that solves complex optimization problems in finance, logistics, and research.",
            "Insurtech platform that uses AI to provide personalized insurance quotes and risk assessment in real-time.",
            "Space technology company developing sustainable propulsion systems for satellite deployment and space exploration.",
            "Creator economy tools that empower content creators to monetize their work and build sustainable businesses.",
            "Clean energy technology that converts waste into renewable energy sources, reducing carbon emissions by 80%."
        ]
        
        entrepreneurs_created = []
        
        for i in range(1, 11):
            # Create user
            email = f"entrepreneur{i}@gmail.com"
            first_name = "entrepreneur"
            last_name = self._number_to_word(i)
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f'Entrepreneur {i} already exists: {email}')
                user = User.objects.get(email=email)
            else:
                user = User.objects.create_user(
                    email=email,
                    password="cofound27",
                    first_name=first_name,
                    last_name=last_name,
                    role='entrepreneur'
                )
                self.stdout.write(f'Created entrepreneur {i}: {email}')
            
            entrepreneurs_created.append(user)
            
            # Create or update profile
            profile, created = EntrepreneurProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': company_names[i-1],
                    'website': f"https://{company_names[i-1].lower().replace(' ', '').replace(',', '')}.com",
                    'linkedin_url': f"https://linkedin.com/in/{first_name}{last_name}{i}",
                    'bio': bios[i-1],
                    'location': locations[i-1],
                    'industries': random.choice(industries),
                    'startup_description': startup_descriptions[i-1],
                    'company_stage': random.choice(company_stages),
                    'funding_need': random.choice(funding_needs),
                    'team_size': random.choice(team_sizes),
                    'revenue': random.choice(revenue_ranges),
                    'funding_raised': random.choice(funding_ranges),
                    'valuation': random.choice(valuation_ranges),
                }
            )
            
            if created:
                self.stdout.write(f'  Created profile for {user.email}')
            else:
                self.stdout.write(f'  Profile already exists for {user.email}')
            
            # Create startup
            startup, startup_created = Startup.objects.get_or_create(
                entrepreneur=user,
                defaults={
                    'name': company_names[i-1],
                    'description': startup_descriptions[i-1],
                    'industry': profile.industries,
                    'website': profile.website,
                    'funding_goal': Decimal(random.randint(100000, 5000000))
                }
            )
            
            if startup_created:
                self.stdout.write(f'  Created startup: {startup.name}')
            else:
                self.stdout.write(f'  Startup already exists: {startup.name}')
            
            # Create startup document
            if startup_created or not StartupDocument.objects.filter(startup=startup).exists():
                # Create a simulated PDF document (just binary data)
                sample_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Startup Pitch Deck) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000111 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
                
                StartupDocument.objects.create(
                    startup=startup,
                    title=f"Pitch Deck - {startup.name}",
                    file_name=f"{startup.name.lower().replace(' ', '_')}_pitch_deck.pdf",
                    file_type="application/pdf",
                    file_data=sample_pdf_content
                )
                self.stdout.write(f'  Created startup document for {startup.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(entrepreneurs_created)} entrepreneur users with profiles and startups!'
            )
        )
    
    def _number_to_word(self, num):
        """Convert number to word (1 -> 'one', 2 -> 'two', etc.)"""
        words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        return words[num - 1] if 1 <= num <= 10 else str(num)
