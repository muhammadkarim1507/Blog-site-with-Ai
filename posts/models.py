from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Tavsif")
    color = models.CharField(max_length=7, default='#6366f1', verbose_name="Rang (HEX)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_posts', kwargs={'slug': self.slug})

    def get_post_count(self):
        return self.posts.filter(is_published=True).count()


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('published', 'Chop etilgan'),
    ]

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts', verbose_name="Muallif"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts', verbose_name="Kategoriya"
    )
    title = models.CharField(max_length=250, verbose_name="Sarlavha")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    excerpt = models.TextField(
        max_length=500, blank=True,
        verbose_name="Qisqa tavsif",
        help_text="Bo'sh qoldirilsa, kontentdan avtomatik olinadi"
    )
    content = RichTextUploadingField(verbose_name="Kontent")
    cover_image = models.ImageField(
        upload_to='posts/covers/%Y/%m/',
        blank=True, null=True,
        verbose_name="Muqova rasmi"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='draft', verbose_name="Holat"
    )
    is_published = models.BooleanField(default=False, verbose_name="Chop etilganmi")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Postlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Slug yaratish
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Excerpt avtomatik
        if not self.excerpt and self.content:
            import re
            clean = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = clean[:300] + '...' if len(clean) > 300 else clean

        # is_published status bilan sinxron
        self.is_published = (self.status == 'published')

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.filter(is_active=True).count()

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='likes', verbose_name="Foydalanuvchi"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='likes', verbose_name="Post"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likelar"
        unique_together = ('user', 'post')  # bir user bir postga bir marta like

    def __str__(self):
        return f"{self.user.username} → {self.post.title}"


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name="Muallif"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments', verbose_name="Post"
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='replies', verbose_name="Asosiy izoh"
    )  # ← nested comment shu yerda
    text = models.TextField(verbose_name="Izoh matni")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.text[:50]}"

    def is_reply(self):
        """Bu izoh javob (reply) mi?"""
        return self.parent is not None

    def get_replies(self):
        """Ushbu izohga javoblar"""
        return self.replies.filter(is_active=True)