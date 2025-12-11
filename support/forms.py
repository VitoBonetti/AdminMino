
from django.forms import ModelForm
from support.models import TicketModel, CommentModel


class TicketForm(ModelForm):

    class Meta:
        model = TicketModel
        fields = [
            "title",
            "subject",
            "description",
            "status",
            "priority",
        ]


class EditTicketForm(ModelForm):

    class Meta:
        model = TicketModel
        fields = [
            "status",
            "priority",
        ]


class CommentForm(ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment']