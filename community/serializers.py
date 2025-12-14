# community/serializers.py
from rest_framework import serializers
from .models import Thread

class ThreadSerializer(serializers.ModelSerializer):
    # Field author_username (ReadOnlyField) mengambil dari thread.user.username
    author_username = serializers.ReadOnlyField(source='user.username') # Menggunakan 'user'

    class Meta:
        model = Thread
        # Sertakan field yang dibutuhkan Flutter
        fields = ('id', 'title', 'content', 'user', 'author_username', 'date_created')
        # 'user' akan diisi di View
        read_only_fields = ('user',)