from django.contrib import admin
from support.models import TicketModel, CommentModel

admin.site.register(TicketModel)
admin.site.register(CommentModel)