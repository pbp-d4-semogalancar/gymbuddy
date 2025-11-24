from django.contrib import admin
from .models import Thread, Reply

# Register your models here.

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date_created')
    
    search_fields = ('title', 'content', 'user__username')
    
    list_filter = ('date_created',)
    
    actions = ['delete_selected']

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread', 'date_created')
    search_fields = ('content', 'user__username', 'thread__title')
    list_filter = ('date_created',)