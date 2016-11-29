import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from pumas.views.base_view import BaseView
from pumas.choices import DOCUMENT_TYPES
from pumas.models.document import ProjectDocument, Journal, ConferencePreceeding, BookChapter, Dessertation, Thesis,\
    Document
from pumas.models.user_profiles import Student, Lecture
from plagiarism.check_plagiarism import Plagiarism
from django.conf import settings


class UploadView(BaseView):

    def __init__(self):
        self.context = {}
        self.template_name = 'upload.html'
        self.title = 'PUMAS'

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = None
        is_student = False
        is_student_undergraduate = False
        is_student_graduate = False
        is_lecture = False
        supervisor = False
        if request.user.is_authenticated():
            try:
                lecture = Lecture.objects.get(user=request.user)
                supervisor = lecture.is_supervisor
            except Lecture.DoesNotExist:
                pass
        try:
            user_profile = Student.objects.get(user=user)
            is_student = True
            print("Got in here")
            if user.groups.all()[0].name == 'undergraduate':
                is_student_undergraduate = True
            elif user.groups.all()[0].name == "graduate":
                is_student_graduate = True
        except:
            pass
        try:
            user_profile = Lecture.objects.get(user=user)
            is_lecture = True
        except Lecture.DoesNotExist:
            pass
        project_documents = ProjectDocument.objects.filter(user_created=user.username)
        journals = Journal.objects.filter(user_created=user.username)
        conference_preceedings = ConferencePreceeding.objects.filter(user_created=user.username)
        bookchapters = BookChapter.objects.filter(user_created=user.username)
        dessertations = Dessertation.objects.filter(user_created=user.username)
        thesis = Thesis.objects.filter(user_created=user.username)
        self.context.update({
            'form_class': self.form_class,
            'document_types': DOCUMENT_TYPES,
            'project_documents': project_documents,
            'journals': journals,
            'conference_preceedings': conference_preceedings,
            'bookchapters': bookchapters,
            'dessertations': dessertations,
            'thesiss': thesis,
            'user_profile': user_profile,
            'is_lecture': is_lecture,
            'is_student': is_student,
            'is_student_undergraduate': is_student_undergraduate,
            'is_student_graduate': is_student_graduate,
            'supervisor': supervisor})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        user = request.user
        project_documents = ProjectDocument.objects.filter(user_created=user.username)
        journals = Journal.objects.filter(user_created=user.username)
        conference_preceedings = ConferencePreceeding.objects.filter(user_created=user.username)
        bookchapters = BookChapter.objects.filter(user_created=user.username)
        dessertations = Dessertation.objects.filter(user_created=user.username)
        thesis = Thesis.objects.filter(user_created=user.username)
        self.context.update({
            'form_class': self.form_class,
            'document_types': DOCUMENT_TYPES,
            'project_documents': project_documents,
            'journals': journals,
            'conference_preceedings': conference_preceedings,
            'bookchapters': bookchapters,
            'dessertations': dessertations,
            'thesis': thesis})
        return render(request, self.template_name, self.context)

    def get_context_data(self, **kwargs):
        return super(UploadView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)


class SupervisorUploadView(BaseView):

    def __init__(self):
        self.context = {}
        self.template_name = 'supervisor_uploiad_view.html'
        self.title = 'PUMAS'

    def get(self, request, *args, **kwargs):
        user = request.user
        lecture = Lecture.objects.filter(user=user)
        students = Student.objects.filter(supervisor=lecture)
        approval_status = request.GET.get('approval_status')
        document_id = request.GET.get('document_id')
        if document_id:
            doc = Document.objects.get(id=document_id)
            if approval_status == 'approved':
                doc.approved = True
                doc.save()
            elif approval_status == 'rejected':
                doc.approved = False
                doc.save()
        print(approval_status, document_id)
        documents = []
        supervisor = False
        if request.user.is_authenticated():
            try:
                lecture = Lecture.objects.get(user=request.user)
                supervisor = lecture.is_supervisor
            except Lecture.DoesNotExist:
                pass
        for student in students:
            project_documents = ProjectDocument.objects.filter(author=student.user)
            for proj_doc in project_documents:
                documents.append([student.student_id, proj_doc.title, proj_doc.source_code, proj_doc.category, proj_doc.id, proj_doc.approved])
            journals = Journal.objects.filter(author=student.user)
            for journal in journals:
                documents.append([student.student_id, journal.title, 'No source code', journal.category, proj_doc.id, proj_doc.approved])
            conference_preceedings = ConferencePreceeding.objects.filter(author=student.user)
            for conference_preceeding in conference_preceedings:
                documents.append([student.student_id, conference_preceeding.title, 'No source code', conference_preceeding.category, proj_doc.id, proj_doc.approved])
            for journal in journals:
                documents.append([student.student_id, journal.title, 'No source code', journal.category, proj_doc.id, proj_doc.approved])
            bookchapters = BookChapter.objects.filter(author=student.user)
            for bookchapter in bookchapters:
                documents.append([student.student_id, bookchapter.title, 'No source code', bookchapter.category, proj_doc.id, proj_doc.approved])
            dessertations = Dessertation.objects.filter(author=student.user)
            for dessertation in dessertations:
                documents.append([student.student_id, dessertation.title, 'No source code', dessertation.category, proj_doc.id, proj_doc.approved])
            thesiss = Thesis.objects.filter(author=student.user)
            for thesis in thesiss:
                documents.append([student.student_id, thesis.title, 'No source code', thesis.category, proj_doc.id, proj_doc.approved])
        self.context.update({
            'form_class': self.form_class,
            'document_types': DOCUMENT_TYPES,
            'documents': documents,
            'supervisor': supervisor})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context.update({
            'title': self.title
        })
        return render(request, self.template_name, self.context)

    def get_context_data(self, **kwargs):
        return super(SupervisorUploadView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SupervisorUploadView, self).dispatch(*args, **kwargs)


class ApproveDocument(BaseView):

    def __init__(self):
        self.context = {}
        self.template_name = 'approve_document.html'
        self.title = 'PUMAS'

    def uploaded_docs(self):
        files = os.path.join(settings.MEDIA_ROOT, 'documents')
        return os.listdir(files)

    def get(self, request, *args, **kwargs):
        user = request.user
        lecture = Lecture.objects.filter(user=user)
        documents = []
        document_id = kwargs.get('id')
        document = None
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            pass
        plagiarism_results_list = []
        files_path = os.path.join(settings.MEDIA_ROOT, 'documents')
        if document:
            plagiarism = Plagiarism()
            file1 = document.document.path
            for file2 in self.uploaded_docs():
                file2 = files_path + '/' + file2
                plagiarism_results_list.append([file2, plagiarism.plagiarism_results(file1, file2)])
        supervisor = False
        if request.user.is_authenticated():
            try:
                lecture = Lecture.objects.get(user=request.user)
                supervisor = lecture.is_supervisor
            except Lecture.DoesNotExist:
                pass
        self.context.update({
            'form_class': self.form_class,
            'document_types': DOCUMENT_TYPES,
            'documents': documents,
            'document': document,
            'supervisor': supervisor,
            'plagiarism_results_list': plagiarism_results_list})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context.update({
            'title': self.title
        })
        return render(request, self.template_name, self.context)

    def get_context_data(self, **kwargs):
        return super(ApproveDocument, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApproveDocument, self).dispatch(*args, **kwargs)
