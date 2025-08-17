from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, Group, Permission


# -----------------------------
# Core / Accounts / Shared
# -----------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('entrepreneur', 'Entrepreneur'),
    ]

    # We’ll use email as username
    username = None
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    # Avoid reverse name collisions with auth models
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='entrepreneurs_user_set',
        related_query_name='entrepreneurs_user',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='entrepreneurs_user_set',
        related_query_name='entrepreneurs_user',
        help_text='Specific permissions for this user.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role', 'first_name', 'last_name']

    def __str__(self):
        full = self.get_full_name().strip()
        return f"{full or self.email} ({self.role})"


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Industries"
        ordering = ['name']

    def __str__(self):
        return self.name


# -----------------------------
# Entrepreneurs domain
# -----------------------------
class EntrepreneurProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="entrepreneur_profile",
        limit_choices_to={'role': 'entrepreneur'}
    )

    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True, null=True, unique=True)

    # Store profile picture as BLOB
    image = models.BinaryField(editable=True,blank=True, null=True)

    # Tags
    industries = models.ManyToManyField(Industry, related_name='entrepreneurs', blank=True)

    # Company/Startup Info
    company_name = models.CharField(max_length=255, blank=True, unique=True)
    startup_description = models.TextField(blank=True, null=True)
    company_stage = models.CharField(
        max_length=50,
        choices=[
            ('idea', 'Idea Stage'),
            ('mvp', 'MVP'),
            ('early', 'Early Stage'),
            ('growth', 'Growth Stage'),
            ('scale', 'Scale Up')
        ],
        default='idea'
    )
    funding_need = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pitch_deck_url = models.URLField(blank=True, null=True)  # optional external link
    team_size = models.PositiveIntegerField(default=1)

    # Metrics
    revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    funding_raised = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valuation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Social
    website = models.URLField(blank=True, null=True, unique=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    github_profile = models.URLField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def image_base64(self):
        if self.image:
            import base64
            return base64.b64encode(self.image).decode('utf-8')
        return None

    @property
    def image_data(self):
        """Property to access image as base64 string for templates"""
        return self.image_base64()

    def __str__(self):
        return f"Entrepreneur Profile: {self.user.get_full_name() or self.user.email}"


class Startup(models.Model):
    entrepreneur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="startups",
        limit_choices_to={'role': 'entrepreneur'}
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    logo = models.BinaryField(editable=True,blank=True, null=True)  # BLOB logo

    funding_goal = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def logo_base64(self):
        if self.logo:
            import base64
            return base64.b64encode(self.logo).decode('utf-8')
        return None

    @property
    def logo_data(self):
        """Property to access logo as base64 string for templates"""
        return self.logo_base64()

    class Meta:
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class StartupDocument(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)

    # BLOB file storage
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)  # e.g., "application/pdf" or "video/mp4"
    file_data = models.BinaryField(editable=True,blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def file_base64(self):
        if self.file_data:
            import base64
            return base64.b64encode(self.file_data).decode('utf-8')
        return None

    @property
    def file_data_display(self):
        """Property to access file data as base64 string for templates"""
        return self.file_base64()

    def __str__(self):
        return f"{self.title} - {self.startup.name}"


# -----------------------------
# Social / Reviews / Requests
# -----------------------------
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    entrepreneur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_reviews",
        limit_choices_to={'role': 'entrepreneur'}
    )
    rating = models.PositiveSmallIntegerField()  # 1-5 scale
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'entrepreneur')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.entrepreneur} ({self.rating})"


class CollaborationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    investor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_requests",
        limit_choices_to={'role': 'investor'}
    )
    entrepreneur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_requests",
        limit_choices_to={'role': 'entrepreneur'}
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Allow multiple requests over time, but only one *pending* at a time
        constraints = [
            models.UniqueConstraint(
                fields=['investor', 'entrepreneur'],
                condition=Q(status='pending'),
                name='unique_pending_collaboration_request'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.investor} → {self.entrepreneur} ({self.status})"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} - {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} favorited {self.target_user}"


class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('login', 'Login'),
        ('view_profile', 'Viewed Profile'),
        ('send_request', 'Sent Collaboration Request'),
        ('accept_request', 'Accepted Collaboration Request'),
        ('send_message', 'Sent Message'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()

    # Post image as BLOB
    image = models.BinaryField(editable=True,null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def image_base64(self):
        if self.image:
            import base64
            return base64.b64encode(self.image).decode('utf-8')
        return None

    def __str__(self):
        return f"{self.author.get_full_name() or self.author.email}'s post @ {self.created_at:%Y-%m-%d}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.get_full_name() or self.author.email} on {self.post_id}"
