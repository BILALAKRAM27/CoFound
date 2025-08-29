from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Investors.models import InvestorProfile, InvestorPortfolio, InvestmentDocument
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 10 investor users with realistic profiles and portfolios'

    def handle(self, *args, **options):
        self.stdout.write('Creating investor users...')
        
        # Sample data for realistic profiles
        firm_names = [
            "Venture Capital Partners", "Innovation Fund", "Tech Growth Capital", 
            "Future Ventures", "Digital Investment Group", "Startup Accelerator Fund", 
            "Emerging Tech Capital", "Sustainable Ventures", "AI Investment Partners", 
            "NextGen Capital"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Boston, MA", "Seattle, WA", 
            "Austin, TX", "Los Angeles, CA", "Chicago, IL", "Denver, CO", 
            "Miami, FL", "Portland, OR"
        ]
        
        industries = [
            'ai', 'fintech', 'healthtech', 'enterprise_saas', 'logistics', 
            'quantum', 'insurtech', 'spacetech', 'creator_tools', 'cleantech'
        ]
        
        investment_stages = ['seed', 'series_a', 'series_b', 'series_c', 'growth', 'late_stage']
        investment_sizes = ['0-50k', '50k-500k', '500k-5m', '5m-50m', '50m+']
        
        # Sample bios
        bios = [
            "Experienced venture capitalist with 15+ years of investing in early-stage technology companies. Focused on AI, fintech, and enterprise SaaS.",
            "Serial investor and former tech executive with a track record of successful exits. Passionate about supporting innovative entrepreneurs.",
            "Venture partner specializing in healthtech and biotech investments. Committed to funding companies that improve human health outcomes.",
            "Investment professional with deep expertise in logistics and supply chain technology. Building the future of global commerce.",
            "Tech investor focused on quantum computing and advanced technologies. Supporting breakthrough innovations that solve complex problems.",
            "Fintech specialist with experience in banking and financial services. Investing in companies that democratize access to financial tools.",
            "Insurtech investor with background in insurance and risk management. Funding the next generation of insurance technology.",
            "Space technology investor passionate about the commercialization of space. Supporting companies that make space accessible.",
            "Creator economy investor and former content creator. Building tools that empower digital creators and influencers.",
            "Clean energy investor committed to sustainable technology solutions. Funding companies that address climate change challenges."
        ]
        
        # Sample portfolio companies
        portfolio_companies = [
            "TechFlow Solutions, DataSphere, CloudBridge",
            "InnovateHub, NextGen Systems, Digital Ventures",
            "FutureTech Labs, HealthTech Innovations, BioTech Solutions",
            "SmartStart Inc, Logistics Pro, Supply Chain Tech",
            "QuantumLeap Tech, Advanced Computing, Research Labs",
            "FinTech Pro, Banking Solutions, Payment Systems",
            "InsureTech Plus, Risk Management, Policy Solutions",
            "SpaceTech Ventures, Satellite Systems, Launch Services",
            "Creator Tools, Content Platform, Monetization Suite",
            "EcoTech Innovations, Green Energy, Sustainable Solutions"
        ]
        
        # Sample notable exits
        notable_exits = [
            "Acquired by Google for $500M in 2022",
            "IPO on NASDAQ in 2021, $2B valuation",
            "Acquired by Microsoft for $800M in 2023",
            "Acquired by Amazon for $300M in 2021",
            "IPO on NYSE in 2022, $1.5B valuation",
            "Acquired by Stripe for $400M in 2023",
            "Acquired by Allstate for $250M in 2022",
            "Acquired by SpaceX for $600M in 2023",
            "Acquired by TikTok for $200M in 2021",
            "Acquired by Tesla for $350M in 2022"
        ]
        
        investors_created = []
        
        for i in range(1, 11):
            # Create user
            email = f"investor{i}@gmail.com"
            first_name = "investor"
            last_name = self._number_to_word(i)
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f'Investor {i} already exists: {email}')
                user = User.objects.get(email=email)
            else:
                user = User.objects.create_user(
                    email=email,
                    password="cofound27",
                    first_name=first_name,
                    last_name=last_name,
                    role='investor'
                )
                self.stdout.write(f'Created investor {i}: {email}')
            
            investors_created.append(user)
            
            # Create or update profile
            profile, created = InvestorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'firm_name': firm_names[i-1],
                    'website': f"https://{firm_names[i-1].lower().replace(' ', '').replace(',', '')}.com",
                    'linkedin_url': f"https://linkedin.com/in/{first_name}{last_name}{i}",
                    'bio': bios[i-1],
                    'location': locations[i-1],
                    'investment_stage': random.choice(investment_stages),
                    'investment_size': random.choice(investment_sizes),
                    'preferred_industries': random.choice(industries),
                    'portfolio_companies': portfolio_companies[i-1],
                    'notable_exits': notable_exits[i-1],
                }
            )
            
            if created:
                self.stdout.write(f'  Created profile for {user.email}')
            else:
                self.stdout.write(f'  Profile already exists for {user.email}')
            
            # Create portfolio
            portfolio, portfolio_created = InvestorPortfolio.objects.get_or_create(
                investor=user,
                defaults={
                    'total_investments': random.randint(1000000, 50000000),
                    'number_of_investments': random.randint(5, 50),
                    'notable_exits': notable_exits[i-1],
                }
            )
            
            if portfolio_created:
                self.stdout.write(f'  Created portfolio for {user.email}')
            else:
                self.stdout.write(f'  Portfolio already exists for {user.email}')
            
            # Create investment document
            if portfolio_created or not InvestmentDocument.objects.filter(investor=user).exists():
                # Create a simulated PDF document (just binary data)
                sample_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Investment Portfolio) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000111 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
                
                InvestmentDocument.objects.create(
                    investor=user,
                    title=f"Investment Portfolio - {profile.firm_name}",
                    file_name=f"{profile.firm_name.lower().replace(' ', '_')}_portfolio.pdf",
                    file_type="application/pdf",
                    file_data=sample_pdf_content
                )
                self.stdout.write(f'  Created investment document for {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(investors_created)} investor users with profiles and portfolios!'
            )
        )
    
    def _number_to_word(self, num):
        """Convert number to word (1 -> 'one', 2 -> 'two', etc.)"""
        words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        return words[num - 1] if 1 <= num <= 10 else str(num)
