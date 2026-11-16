from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest


class ServiceRequestTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tester", password="x")
        self.category = Category.objects.create(name="ICT")

    def make(self, **kw):
        data = dict(requester=self.user, category=self.category,
                    title="t", description="d", location="Lab")
        data.update(kw)
        return ServiceRequest(**data)

    def test_resolved_or_closed_requires_date_and_summary(self):
        for status in (ServiceRequest.Status.RESOLVED, ServiceRequest.Status.CLOSED):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError) as ctx:
                    self.make(status=status).full_clean()
                self.assertIn("resolved_at", ctx.exception.message_dict)
                self.assertIn("resolution_summary", ctx.exception.message_dict)

    def test_whitespace_summary_rejected(self):
        req = self.make(status="resolved", resolved_at=timezone.now(), resolution_summary="   ")
        with self.assertRaises(ValidationError) as ctx:
            req.full_clean()
        self.assertIn("resolution_summary", ctx.exception.message_dict)

    def test_valid_resolved_passes(self):
        self.make(status="resolved", resolved_at=timezone.now(), resolution_summary="Fixed").full_clean()

    def test_open_request_needs_no_resolution(self):
        self.make().full_clean()

    def test_priority_constraint_enforced_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make(priority=9).save()

    def test_due_before_filter(self):
        now = timezone.now()
        self.make(title="soon", due_at=now + timedelta(hours=1)).save()
        self.make(title="later", due_at=now + timedelta(days=5)).save()
        self.make(title="none").save()
        titles = [r.title for r in ServiceRequest.objects.filter(due_at__lt=now + timedelta(days=1))]
        self.assertEqual(titles, ["soon"])

    def test_category_in_use_is_protected(self):
        self.make().save()
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_duplicate_category_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="ICT")
