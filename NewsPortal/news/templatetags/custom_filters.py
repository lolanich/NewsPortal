from django import template


register = template.Library()


@register.filter()
def censor(text):
    bad_words = ['Dungeons & Dragons', 'D&D', 'текст']
    for word in bad_words:
        text = text.replace(word, '*' * len(word))
    return text
