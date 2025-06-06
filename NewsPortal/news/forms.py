from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_type', 'categories', 'title', 'text', 'rating']

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        if description is not None and len(description) < 20:
            raise ValidationError({
                "description": "Описание не может быть менее 20 символов."
            })

        name = cleaned_data.get("name")
        if name == description:
            raise ValidationError(
                "Описание не должно быть идентичным названию."
            )

        return cleaned_data

