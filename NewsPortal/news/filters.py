from django.forms import DateTimeInput
from django_filters import FilterSet, DateTimeFilter
from .models import Post


class NewsFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='created_at',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Post
        fields = ['categories', 'title', 'author', 'created_at']
