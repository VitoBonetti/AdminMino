from django.shortcuts import render
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
    Q,
    Sum,
    DecimalField
)
from collections import defaultdict

today_date = timezone.now().date()

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            "today": today_date,
        }
        return render(request, "main/home.html", context=context)
