from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import Category, Comment, ServiceRequest, WorkOrder


class OverdueFilter(admin.SimpleListFilter):
    title = "due date"
    parameter_name = "due"

    def lookups(self, request, model_admin):
        return (("overdue", "Overdue"), ("today", "Due today"), ("none", "No due date"))

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "overdue":
            return queryset.filter(due_at__lt=now).exclude(status__in=["resolved", "closed"])
        if self.value() == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(due_at__gte=start, due_at__lt=start + timedelta(days=1))
        if self.value() == "none":
            return queryset.filter(due_at__isnull=True)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "requester", "priority", "status", "due_at", "resolved_at", "created_at")
    list_filter = ("status", "priority", "category", OverdueFilter)
    search_fields = ("title", "description", "location", "resolution_summary")
    inlines = [CommentInline]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("service_request", "technician", "started_at", "completed_at")
    search_fields = ("service_request__title", "technician__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("service_request", "author", "is_internal", "created_at")
    list_filter = ("is_internal",)
