from django.shortcuts import (
    render,
    redirect,
    reverse,
    get_object_or_404
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View

from django.http import HttpResponseRedirect
from support.models import TicketModel, CommentModel
from support.forms import TicketForm, CommentForm, EditTicketForm


@login_required()
def support_view(request):
    if request.method == "POST":
        if "submit_ticket" in request.POST:
            ticket_form = TicketForm(request.POST)
            if ticket_form.is_valid():
                new_ticket = ticket_form.save(commit=False)
                new_ticket.user = request.user
                new_ticket.save()
                return redirect("support")
        elif "edit_ticket" in request.POST:
            print(request.POST)
            ticket_id = request.POST.get("ticket_id")
            print(ticket_id)
            try:
                ticket_instance = TicketModel.objects.get(id=ticket_id)
                print(ticket_instance)
            except TicketModel.DoesNotExist:
                pass
            else:
                ticket_form = EditTicketForm(request.POST, instance=ticket_instance)
                print(ticket_form)
                if ticket_form.is_valid():
                    ticket_form.save()
                    return redirect("support")
        elif "submit_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            ticket_id = request.POST.get("ticket_id")
            if comment_form.is_valid() and ticket_id is not None:
                new_comment = comment_form.save(commit=False)
                new_comment.ticket_id = TicketModel.objects.get(id=ticket_id)
                new_comment.user = request.user
                new_comment.save()
                return redirect("support")

    tickets = TicketModel.objects.all()
    ticket_form = TicketForm()
    comment_form = {ticket.id: CommentForm() for ticket in tickets}

    context = {
        "ticket_form": ticket_form,
        "comment_form": comment_form,
        "tickets": tickets
    }

    return render(request, "support/support.html", context=context)


class DeleteTicketView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cost_id = self.kwargs['pk']
        cost = get_object_or_404(TicketModel, pk=cost_id)
        cost.delete()
        return HttpResponseRedirect(reverse('support'))


class SupportView(LoginRequiredMixin, View):
    def get(self, request):

        tickets = TicketModel.objects.all().prefetch_related("ticket_comments")
        ticket_form = TicketForm()
        comment_form = CommentForm()

        context = {
            "tickets": tickets,
            "ticket_form": ticket_form,
            "comment_form": comment_form
        }

        return render(request, "support/support.html", context=context)

    def post(self, request):

        if "submit_ticket" in request.POST:
            ticket_form = TicketForm(request.POST)
            if ticket_form.is_valid():
                new_ticket = ticket_form.save(commit=False)
                new_ticket.user = request.user
                new_ticket.save()

                ticket_form = TicketForm()
                tickets = TicketModel.objects.all().prefetch_related("ticket_comments")
                comment_form = CommentForm()

                context = {
                    "tickets": tickets,
                    "ticket_form": ticket_form,
                    "comment_form": comment_form
                }

                return render(request, "support/support.html", context=context)

        elif "submit_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            ticket_id = request.POST.get("ticket_id")
            if comment_form.is_valid() and ticket_id:
                new_comment = comment_form.save(commit=False)
                new_comment.user = request.user
                new_comment.ticket_id = TicketModel.objects.get(id=ticket_id)
                new_comment.save()

                comment_form = CommentForm()
                ticket_form = TicketForm()
                tickets = TicketModel.objects.all().prefetch_related("ticket_comments")

                context = {
                    "tickets": tickets,
                    "ticket_form": ticket_form,
                    "comment_form": comment_form
                }

                return render(request, "support/support.html", context=context)

        else:
            return redirect("support")

        return self.get(request)