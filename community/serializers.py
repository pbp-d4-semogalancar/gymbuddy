from rest_framework import serializers
from .models import Thread

class ThreadSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='user.username')
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ('id', 'title', 'content', 'user', 'author_username', 'date_created', 'is_mine')
        read_only_fields = ('user',)

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False