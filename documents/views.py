from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied


from documents.models import Document
from documents.forms import DocumentForm
from documents.mixins import RoleRequiredMixin


from notifications.utils import NotificationService


class DocumentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "documents/upload_document.html"
    success_url = reverse_lazy("documents:employee_documents")
    required_role = "employee"

    def form_valid(self, form):
        form.instance.employee = self.request.user
        messages.success(
            self.request, "Документ успешно загружен и отправлен на рассмотрение."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return self.render_to_response(self.get_context_data(form=form))


class EmployeeDocumentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """
    A view for displaying the documents created by the current user.

    The view displays all the documents that are created by the current user and
    are in the "pending" status.
    """

    model = Document
    template_name = "documents/employee_documents.html"
    context_object_name = "documents"
    paginate_by = 5
    required_role = "employee"

    def get_queryset(self):
        """
        Returns a queryset of documents that are created by the current user and
        are in the "pending" status.
        """
        return Document.objects.filter(employee=self.request.user)


class ManagerDocumentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """
    A view for displaying the documents that are available for assignment.

    The view displays all the documents that are in the "pending" status and are
    not assigned to any assistant.
    """

    model = Document
    template_name = "documents/manager_documents.html"
    context_object_name = "documents"
    paginate_by = 5
    required_role = "manager"

    def get_queryset(self):
        """
        Returns a queryset of documents that are in the "pending" status and are
        not assigned to any assistant.
        """
        return Document.objects.filter(
            status=Document.STATUS_PENDING, assigned_to__isnull=True
        )


class AssistantDocumentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """
    A view for displaying the documents assigned to the assistant.

    The view displays all the documents that are assigned to the assistant and
    are in the "pending" status.
    """

    model = Document
    template_name = "documents/assistant_documents.html"
    context_object_name = "documents"
    paginate_by = 5
    required_role = "assistant"

    def get_queryset(self):
        """
        Returns a queryset of documents that are assigned to the assistant and
        are in the "pending" status.
        """
        return Document.objects.filter(
            status=Document.STATUS_PENDING, assigned_to=self.request.user
        )


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """
    A view for displaying the details of a document.

    Employees can only see their own documents, while managers and assistants can see all documents.
    """

    model = Document
    template_name = "documents/document_detail.html"
    context_object_name = "document"

    def get_queryset(self):
        """
        Returns a queryset of documents that the current user can see.

        If the user is an employee, only their own documents are returned.
        If the user is a manager or assistant, all documents are returned.
        If the user has another role, an empty queryset is returned.
        """
        queryset = super().get_queryset()
        if self.request.user.is_employee:
            # Employees can only see their own documents
            queryset = queryset.filter(employee=self.request.user)
        elif self.request.user.is_manager or self.request.user.is_assistant:
            # Managers and assistants can see all documents
            queryset = queryset
        else:
            # Other roles can't see any documents
            queryset = queryset.none()
        return queryset


class AssignDocumentView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Document
    fields = []
    template_name = "documents/assign_document.html"
    success_url = reverse_lazy("documents:manager_documents")
    required_role = "manager"

    def form_valid(self, form):
        assistant_id = self.request.POST.get("assistant")
        if not assistant_id:
            messages.error(self.request, "Вы должны выбрать помощника.")
            return self.form_invalid(form)
        self.object = form.save(commit=False)
        self.object.assigned_to_id = assistant_id
        self.object.save()
        messages.success(self.request, "Документ назначен помощнику.")
        notification_service = NotificationService()
        notification_service.notify_user(
            assistant_id, f"Вам назначен документ: {self.object.document_type}"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assistants"] = self.get_assistants()
        return context

    def get_assistants(self):
        return self.request.user.__class__.objects.filter(role="assistant")


class ReviewDocumentView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    """
    View for reviewing a document.

    This view is used by managers and assistants to review documents. The view
    handles GET and POST requests. The GET request is used to display the form
    for reviewing the document, while the POST request is used to update the
    status of the document and send a notification to the user.

    Attributes:
        model (Document): The model for the view.
        fields (list): The fields to display in the form.
        template_name (str): The name of the template for the view.
        required_role (str): The role required for the user to access the view.
    """

    model = Document
    fields = []
    template_name = "documents/review_document.html"
    required_role = None

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.

        This method is called when the user requests the page with the form for
        reviewing the document.

        Args:
            request (Request): The request object.
            *args (list): Additional arguments.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            Response: The response object.
        """
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request.

        This method is called when the user submits the form with the new status
        of the document.

        Args:
            request (Request): The request object.
            *args (list): Additional arguments.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            Response: The response object.
        """
        self.object = self.get_object()
        action = request.POST.get("action")
        user_id = self.object.employee.id

        if action == "accept":
            self.object.status = Document.STATUS_ACCEPTED
            message_text = "Ваш документ был принят."
        elif action == "reject":
            self.object.status = Document.STATUS_REJECTED
            message_text = "Ваш документ был отклонен."
        else:
            raise PermissionDenied

        self.object.save()

        notification_service = NotificationService()
        notification_service.notify_user(user_id, message_text)

        messages.success(request, "Статус документ был обновлен.")
        return HttpResponseRedirect(self.get_success_url())


class ManagerReviewDocumentView(ReviewDocumentView):
    success_url = reverse_lazy("documents:manager_documents")
    required_role = "manager"


class AssistantReviewDocumentView(ReviewDocumentView):
    success_url = reverse_lazy("documents:assistant_documents")
    required_role = "assistant"
