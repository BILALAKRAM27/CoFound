from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Post, Comment, PostMedia
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate posts, comments, likes, and saved posts for all users'

    def handle(self, *args, **options):
        self.stdout.write('Populating posts and social activity...')
        
        # Sample post content
        post_contents = [
            "Just launched our MVP! The feedback from early users has been incredible. Building the future of AI-powered business automation.",
            "Excited to announce our Series A funding round! Huge thanks to our investors for believing in our vision.",
            "Looking for talented developers to join our team. We're building something revolutionary in the fintech space.",
            "Had an amazing meeting with potential partners today. The startup ecosystem is truly collaborative and supportive.",
            "Our platform just hit 10,000 users! This milestone means so much to our team. Onward and upward!",
            "Attending the TechCrunch Disrupt conference next week. Anyone else going? Let's connect!",
            "Just published our technical blog post on the challenges of scaling AI infrastructure. Check it out!",
            "Our team is growing! Welcome to our new CTO who brings 15+ years of experience from Google and Facebook.",
            "Customer success story: Our solution helped a client reduce operational costs by 40%. This is why we do what we do.",
            "Working on some exciting new features that will revolutionize how businesses handle data. Can't wait to share more!",
            "The startup journey is a rollercoaster, but every challenge makes us stronger. Grateful for this amazing community.",
            "Just closed our biggest deal yet! Enterprise sales take time, but the results are worth the effort.",
            "Our AI model accuracy just hit 99.2%! The engineering team has been working tirelessly on this optimization.",
            "Excited to be speaking at the upcoming AI conference in San Francisco. Will share insights on building scalable ML systems.",
            "Customer feedback is everything! We've implemented 15 new features based on user requests this quarter.",
            "The future of work is remote-first. Our platform is helping teams collaborate seamlessly across the globe.",
            "Sustainability isn't just a buzzword for us. We're building technology that helps businesses reduce their carbon footprint.",
            "Innovation happens at the intersection of different fields. That's why we're exploring quantum computing applications.",
            "Team retreat this weekend! Building great products starts with building great teams and relationships.",
            "Just hit profitability! The path from startup to sustainable business is challenging but incredibly rewarding."
        ]
        
        # Sample comment content
        comment_contents = [
            "Congratulations! This is a huge milestone.",
            "Love the vision! How can I get involved?",
            "The AI integration looks really promising.",
            "Great work on the user experience!",
            "This could revolutionize the industry.",
            "Impressive growth! What's your secret?",
            "The technical architecture is solid.",
            "Customer-centric approach is key to success.",
            "Looking forward to seeing what's next!",
            "The market timing couldn't be better.",
            "Your team is doing amazing work.",
            "This is exactly what the market needs.",
            "The scalability potential is enormous.",
            "Great to see innovation in this space.",
            "The user feedback is really positive.",
            "This could be a game-changer.",
            "The execution has been flawless.",
            "Excited to follow your journey!",
            "The business model is really smart.",
            "This is the future of the industry."
        ]
        
        # Get all users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        posts_created = 0
        comments_created = 0
        
        # Create posts for each user
        for user in users:
            # Create 5 posts per user
            for i in range(5):
                # Random post date within last 30 days
                post_date = timezone.now() - timedelta(days=random.randint(0, 30))
                
                post_content = random.choice(post_contents)
                
                # Create post
                post = Post.objects.create(
                    author=user,
                    content=post_content,
                    created_at=post_date
                )
                posts_created += 1
                
                # Add random likes (0-8 likes per post)
                num_likes = random.randint(0, min(8, len(users) - 1))
                if num_likes > 0:
                    # Get random users (excluding the author)
                    potential_likers = [u for u in users if u != user]
                    likers = random.sample(potential_likers, min(num_likes, len(potential_likers)))
                    post.likes.add(*likers)
                
                # Add random saves (0-5 saves per post)
                num_saves = random.randint(0, min(5, len(users) - 1))
                if num_saves > 0:
                    potential_savers = [u for u in users if u != user]
                    savers = random.sample(potential_savers, min(num_saves, len(potential_savers)))
                    post.saved_by.add(*savers)
                
                # Add random comments (0-4 comments per post)
                num_comments = random.randint(0, min(4, len(users) - 1))
                if num_comments > 0:
                    potential_commenters = [u for u in users if u != user]
                    commenters = random.sample(potential_commenters, min(num_comments, len(potential_commenters)))
                    
                    for commenter in commenters:
                        comment_date = post_date + timedelta(hours=random.randint(1, 48))
                        Comment.objects.create(
                            post=post,
                            author=commenter,
                            content=random.choice(comment_contents),
                            created_at=comment_date
                        )
                        comments_created += 1
                
                # Occasionally add media to posts (20% chance)
                if random.random() < 0.2:
                    # Create a simulated image file (just binary data)
                    sample_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178\xea\x00\x00\x00\x00IEND\xaeB`\x82'
                    
                    PostMedia.objects.create(
                        post=post,
                        media_type='image',
                        file_name=f"post_image_{post.id}.png",
                        file_type="image/png",
                        file_data=sample_image_content,
                        file_size=len(sample_image_content),
                        position=0
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {posts_created} posts and {comments_created} comments!'
            )
        )
        
        # Display some statistics
        total_posts = Post.objects.count()
        total_comments = Comment.objects.count()
        total_likes = sum(post.likes.count() for post in Post.objects.all())
        total_saves = sum(post.saved_by.count() for post in Post.objects.all())
        
        self.stdout.write(f'Total posts in database: {total_posts}')
        self.stdout.write(f'Total comments in database: {total_comments}')
        self.stdout.write(f'Total likes across all posts: {total_likes}')
        self.stdout.write(f'Total saves across all posts: {total_saves}')
