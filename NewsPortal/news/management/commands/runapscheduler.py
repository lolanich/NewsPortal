import logging
from datetime import timedelta

from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone

from news.models import Post, Category

logger = logging.getLogger(__name__)


def my_job():
    one_week_ago = timezone.now() - timedelta(days=7)
    users = User.objects.all()
    for user in users:
        categories = Category.objects.filter(subscribers=user)
        if not categories.exists():
            continue

        posts = Post.objects.filter(
            categories__in=categories,
            created_at__gte=one_week_ago
        ).distinct()

        if not posts.exists():
            continue
        post_list = ""
        for post in posts:
            post_list += f"<li><a href='{post.id}'>{post.title}</a></li>"

        message_html = f"<h2>Новые посты за последнюю неделю</h2><ul>{post_list}</ul>"

        send_mail(
            subject='Новые посты за неделю',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message_html,
        )


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week='sat', hour=10, minute=0),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

