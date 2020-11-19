from django import forms
from .models import Hub, Post

#
#
class HabForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = [
            'id',
            'name',
            'description',
            'link',
            'poll',
            'poll_interval',
            'last_poll_date_time'
        ]



# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = [
#             'id',
#             'title',
#             'date',
#             'author_link',
#             'author_name',
#             'link',
#             'body'
#         ]