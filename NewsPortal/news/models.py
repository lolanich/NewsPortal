from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_ratings = self.post_set.aggregate(total=models.Sum('rating'))['total'] or 0
        total_post_rating = post_ratings * 3

        comment_ratings = self.user.comment_set.aggregate(total=models.Sum('rating'))['total'] or 0

        comments_to_posts = Comment.objects.filter(post__author=self).aggregate(total=models.Sum('rating'))['total'] or 0

        self.rating = total_post_rating + comment_ratings + comments_to_posts
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NE'
    POST_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (NEWS, 'News'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'Вы опубликовали:  {self.title}  {self.text}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + ('...' if len(self.text) > 124 else '')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.notify_subscribers()

    def notify_subscribers(self):
        emails = set(
            User.objects.filter(subscribed_categories__in=self.categories.all()).distinct().values_list('email', flat=True))

        html_title = render_to_string('news/title.html', {'title': self.title})
        from django.utils.html import strip_tags
        plain_text_preview = strip_tags(self.text)[:50]

        subject = self.title

        for email in emails:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                username = 'Пользователь'

            send_mail(
                subject=subject,
                message='',
                from_email='t.maill@yandex.ru',
                recipient_list=[email],
                html_message=render_to_string('news/email_template.html', {
                    'title': self.title,
                    'html_title': html_title,
                    'username': username,
                    'preview_text': plain_text_preview,
                }),
            )


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
