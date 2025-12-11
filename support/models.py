
from django.db import models
from django.contrib.auth.models import User


class TicketModel(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("solved", "Solved"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    title = models.CharField(max_length=200, null=False, blank=False)
    subject = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, default="low")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="ticket_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject}: {self.title} - {self.user}"

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"


class CommentModel(models.Model):
    ticket_id = models.ForeignKey(TicketModel, related_name="ticket_comment", on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="ticket_comment_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ticket_id}: {self.comment} - {self.user}"
