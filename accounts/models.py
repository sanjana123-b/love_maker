from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class InterestTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=30, blank=True, help_text='Emoji or Bootstrap icon class')
    category = models.CharField(max_length=30, default='General')

    class Meta:
        ordering = ['name']
        verbose_name = 'Interest Tag'
        verbose_name_plural = 'Interest Tags'

    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    LOOKING_FOR_CHOICES = [
        ('male', 'Men'),
        ('female', 'Women'),
        ('everyone', 'Everyone'),
    ]
    ZODIAC_CHOICES = [
        ('Aries', 'Aries ♈'),
        ('Taurus', 'Taurus ♉'),
        ('Gemini', 'Gemini ♊'),
        ('Cancer', 'Cancer ♋'),
        ('Leo', 'Leo ♌'),
        ('Virgo', 'Virgo ♍'),
        ('Libra', 'Libra ♎'),
        ('Scorpio', 'Scorpio ♏'),
        ('Sagittarius', 'Sagittarius ♐'),
        ('Capricorn', 'Capricorn ♑'),
        ('Aquarius', 'Aquarius ♒'),
        ('Pisces', 'Pisces ♓'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    city = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')
    education = models.CharField(max_length=100, blank=True, default='')
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Height in cm')
    zodiac_sign = models.CharField(max_length=20, choices=ZODIAC_CHOICES, blank=True, default='Leo')
    
    interests = models.CharField(
        max_length=500, blank=True, default='',
        help_text='Comma-separated interests, e.g. hiking, cooking, music',
    )
    interests_tags = models.ManyToManyField(InterestTag, blank=True, related_name='profiles')
    
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default='')
    looking_for = models.CharField(max_length=10, choices=LOOKING_FOR_CHOICES, default='everyone')
    
    # Trust & Privacy Settings
    is_verified = models.BooleanField(default=False)
    is_incognito = models.BooleanField(default=False, help_text='Hide profile from public browse deck')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['gender']),
            models.Index(fields=['looking_for']),
            models.Index(fields=['birth_date']),
        ]

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def interests_list(self):
        if self.interests:
            return [i.strip() for i in self.interests.split(',') if i.strip()]
        if self.interests_tags.exists():
            return [tag.name for tag in self.interests_tags.all()]
        return []

    @property
    def profile_strength(self):
        """Calculate profile completeness score (0-100%)."""
        score = 0
        if self.profile_pic:
            score += 25
        if self.bio and len(self.bio) >= 20:
            score += 20
        if self.birth_date:
            score += 15
        if self.city:
            score += 15
        if self.interests:
            score += 15
        if self.occupation or self.education:
            score += 10
        return min(100, score)

    def is_blocked_by(self, other_user):
        """Check if other_user has blocked this profile's user."""
        return BlockRecord.objects.filter(blocker=other_user, blocked_user=self.user).exists()

    def is_blocking(self, other_user):
        """Check if this profile's user has blocked other_user."""
        return BlockRecord.objects.filter(blocker=self.user, blocked_user=other_user).exists()


class ProfilePhoto(models.Model):
    """Multi-photo gallery supporting up to 6 photos per user."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery_photos/')
    caption = models.CharField(max_length=150, blank=True, default='')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.profile.user.username} - Photo #{self.id}"


class ProfilePrompt(models.Model):
    """Prompt answers (e.g., 'A non-negotiable for me is...', 'My ideal Sunday...')."""
    PROMPT_CHOICES = [
        ('My ideal first date is...', 'My ideal first date is...'),
        ('A non-negotiable for me is...', 'A non-negotiable for me is...'),
        ('The most spontaneous thing I have done...', 'The most spontaneous thing I have done...'),
        ('Two truths and a lie...', 'Two truths and a lie...'),
        ('My favorite way to spend a rainy day...', 'My favorite way to spend a rainy day...'),
        ('I get way too excited about...', 'I get way too excited about...'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='prompts')
    question = models.CharField(max_length=100, choices=PROMPT_CHOICES)
    answer = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['profile', 'question']

    def __str__(self):
        return f"{self.profile.user.username}: {self.question}"


class BlockRecord(models.Model):
    """User block model ensuring safety and blocking of abusive accounts."""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_initiated')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_received')
    reason = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['blocker', 'blocked_user']
        indexes = [
            models.Index(fields=['blocker', 'blocked_user']),
        ]

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked_user.username}"


class UserReport(models.Model):
    """Trust & Safety User Reporting System with moderation review status."""
    CATEGORY_CHOICES = [
        ('harassment', 'Harassment or Bullying'),
        ('inappropriate_content', 'Inappropriate Photos or Bio'),
        ('fake_profile', 'Fake Account or Impersonation'),
        ('spam', 'Spam or Commercial Solicitation'),
        ('other', 'Other Reason'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed / Resolved'),
        ('action_taken', 'Action Taken (Warning/Ban)'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='harassment')
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id}: {self.reporter.username} -> {self.reported_user.username} ({self.category})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
