from django.contrib import admin
from .models import TelegramUser, BotText, TelegramAccount

# Register your models here.


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "first_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("telegram_id", "first_name")


@admin.register(BotText)
class BotTextAdmin(admin.ModelAdmin):
    list_display = ("name", "text")
    search_fields = ("name",)


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ("phone", "is_active", "last_used")
    list_filter = ("is_active",)
    search_fields = ("phone",)
