from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with all sample data (users, posts, funding rounds, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating users (use existing ones)',
        )
        parser.add_argument(
            '--skip-posts',
            action='store_true',
            help='Skip creating posts and social activity',
        )
        parser.add_argument(
            '--skip-funding',
            action='store_true',
            help='Skip creating funding rounds and investments',
        )
        parser.add_argument(
            '--skip-connections',
            action='store_true',
            help='Skip creating connections and collaboration requests',
        )
        parser.add_argument(
            '--skip-meetings',
            action='store_true',
            help='Skip creating meetings',
        )
        parser.add_argument(
            '--skip-messages',
            action='store_true',
            help='Skip creating messages',
        )
        parser.add_argument(
            '--skip-notifications',
            action='store_true',
            help='Skip creating notifications and activity logs',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting comprehensive database population...')
        )
        
        # Check if users exist
        user_count = User.objects.count()
        if user_count == 0 and not options['skip_users']:
            self.stdout.write('No users found. Creating users first...')
        elif user_count > 0:
            self.stdout.write(f'Found {user_count} existing users.')
        
        try:
            # Step 1: Create users (if not skipped)
            if not options['skip_users']:
                self.stdout.write('\n📱 Step 1: Creating entrepreneur users...')
                call_command('create_entrepreneurs', verbosity=1)
                
                self.stdout.write('\n💰 Step 2: Creating investor users...')
                call_command('create_investors', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping user creation...')
            
            # Step 3: Create posts and social activity (if not skipped)
            if not options['skip_posts']:
                self.stdout.write('\n📝 Step 3: Creating posts and social activity...')
                call_command('populate_posts', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping post creation...')
            
            # Step 4: Create funding rounds and investments (if not skipped)
            if not options['skip_funding']:
                self.stdout.write('\n💸 Step 4: Creating funding rounds and investments...')
                call_command('populate_funding_rounds', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping funding round creation...')
            
            # Step 5: Create connections and collaboration requests (if not skipped)
            if not options['skip_connections']:
                self.stdout.write('\n🤝 Step 5: Creating connections and collaboration requests...')
                call_command('populate_connections', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping connection creation...')
            
            # Step 6: Create meetings (if not skipped)
            if not options['skip_meetings']:
                self.stdout.write('\n📅 Step 6: Creating meetings...')
                call_command('populate_meetings', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping meeting creation...')
            
            # Step 7: Create messages (if not skipped)
            if not options['skip_messages']:
                self.stdout.write('\n💬 Step 7: Creating messages...')
                call_command('populate_messages', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping message creation...')
            
            # Step 8: Create notifications and activity logs (if not skipped)
            if not options['skip_notifications']:
                self.stdout.write('\n🔔 Step 8: Creating notifications and activity logs...')
                call_command('populate_notifications', verbosity=1)
            else:
                self.stdout.write('⏭️  Skipping notification creation...')
            
            # Final statistics
            self.stdout.write('\n📊 Final Database Statistics:')
            self.stdout.write('=' * 50)
            
            # User statistics
            total_users = User.objects.count()
            entrepreneurs = User.objects.filter(role='entrepreneur').count()
            investors = User.objects.filter(role='investor').count()
            
            self.stdout.write(f'👥 Total Users: {total_users}')
            self.stdout.write(f'🚀 Entrepreneurs: {entrepreneurs}')
            self.stdout.write(f'💰 Investors: {investors}')
            
            # Import models for statistics
            from Entrepreneurs.models import (
                Startup, StartupDocument, Post, Comment, 
                Favorite, CollaborationRequest, Meeting, Message,
                Notification, ActivityLog
            )
            from Investors.models import (
                FundingRound, InvestmentCommitment
            )
            
            # Content statistics
            startups = Startup.objects.count()
            startup_docs = StartupDocument.objects.count()
            posts = Post.objects.count()
            comments = Comment.objects.count()
            favorites = Favorite.objects.count()
            collab_requests = CollaborationRequest.objects.count()
            meetings = Meeting.objects.count()
            messages = Message.objects.count()
            notifications = Notification.objects.count()
            activity_logs = ActivityLog.objects.count()
            funding_rounds = FundingRound.objects.count()
            investments = InvestmentCommitment.objects.count()
            
            self.stdout.write(f'\n🏢 Startups: {startups}')
            self.stdout.write(f'📄 Startup Documents: {startup_docs}')
            self.stdout.write(f'📝 Posts: {posts}')
            self.stdout.write(f'💬 Comments: {comments}')
            self.stdout.write(f'❤️  Favorites (Follows): {favorites}')
            self.stdout.write(f'🤝 Collaboration Requests: {collab_requests}')
            self.stdout.write(f'📅 Meetings: {meetings}')
            self.stdout.write(f'💬 Messages: {messages}')
            self.stdout.write(f'🔔 Notifications: {notifications}')
            self.stdout.write(f'📊 Activity Logs: {activity_logs}')
            self.stdout.write(f'💸 Funding Rounds: {funding_rounds}')
            self.stdout.write(f'💵 Investment Commitments: {investments}')
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(
                self.style.SUCCESS('🎉 Database population completed successfully!')
            )
            
            # Login credentials reminder
            self.stdout.write('\n🔑 Login Credentials:')
            self.stdout.write('Entrepreneurs: entrepreneur1@gmail.com to entrepreneur10@gmail.com (password: cofound27)')
            self.stdout.write('Investors: investor1@gmail.com to investor10@gmail.com (password: cofound27)')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during database population: {str(e)}')
            )
            raise
