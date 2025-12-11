
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import DateField
from django.contrib.auth.mixins import LoginRequiredMixin


class FlexibleDateField(LoginRequiredMixin, DateField):
    def to_python(self, value):
        if value is None:
            return None

        # Handle input in YYYY-MM-DD format from the browser
        if len(value) == 10 and value.count('-') == 2:
            year, month, day = value.split('-')
            # Convert to DDMMYYYY or DDMMYY depending on your logic
            # This example converts to DDMMYYYY; adjust as necessary
            value = f"{day}{month}{year}"

        # Check if only day and month are provided
        if len(value) == 4:
            date_str = f"{value[:2]}-{value[2:]}-{timezone.now().year}"
        # Check if day, month and 2-digit year are provided
        elif len(value) == 6:
            date_str = f"{value[:2]}-{value[2:4]}-20{value[4:]}"
        # Check if day, month and 4-digit year are provided
        elif len(value) == 8:
            date_str = f"{value[:2]}-{value[2:4]}-{value[4:]}"
        else:
            raise ValidationError(f"Invalid date: {value}")

        try:
            return super().to_python(date_str)
        except ValidationError:
            raise ValidationError(f"Invalid date: {value}")
