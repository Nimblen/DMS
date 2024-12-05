from django.urls import path
from .views import (
    DocumentCreateView,
    EmployeeDocumentListView,
    ManagerDocumentListView,
    AssistantDocumentListView,
    DocumentDetailView,
    AssignDocumentView,
    ManagerReviewDocumentView,
    AssistantReviewDocumentView,
)

app_name = 'documents'

urlpatterns = [
    path('upload/', DocumentCreateView.as_view(), name='upload_document'),
    path('my-documents/', EmployeeDocumentListView.as_view(), name='employee_documents'),
    path('manager/documents/', ManagerDocumentListView.as_view(), name='manager_documents'),
    path('assistant/documents/', AssistantDocumentListView.as_view(), name='assistant_documents'),
    path('document/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('manager/document/<int:pk>/assign/', AssignDocumentView.as_view(), name='assign_document'),
    path('manager/document/<int:pk>/review/', ManagerReviewDocumentView.as_view(), name='manager_review_document'),
    path('assistant/document/<int:pk>/review/', AssistantReviewDocumentView.as_view(), name='assistant_review_document'),
]
