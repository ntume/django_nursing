from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponse
import datetime
import csv
import xlwt
import json

from .models import Category, Survey, QuestionType, Question, Answer, SurveyAnswer
from .forms import SurveyForm, QuestionForm, CategoryForm
from accounts.models import User
from companies.models import CompanyContacts
from students.models import Student


# Create your views here.

class SurveyListView(LoginRequiredMixin,ListView):
    template_name = 'surveys/surveys.html'
    model = Survey
    context_object_name = 'surveys'

    def get_queryset(self):
        return Survey.objects.all().order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_survey = SurveyForm(prefix = 'form_survey')
        form_questions = QuestionForm(prefix = 'form_questions')
        categories = Category.objects.all()
        types = QuestionType.objects.all().order_by('type')
        context['types'] = types
        context['form_survey'] = form_survey
        context['form_questions'] = form_questions
        context['categories'] = categories
        context['survey_menu'] = 'active'
        return context


class SurveyStudentListView(LoginRequiredMixin,ListView):
    template_name = 'surveys/survey_list_student.html'
    model = Survey
    context_object_name = 'surveys'

    def get_queryset(self):
        surveys = Survey.objects.filter(published__exact = 'Yes',role=6).order_by('created_at')
        s = [];
        for survey in surveys:
            _s = {'id':survey.id,'title':survey.title,'description':survey.description,'created_at':survey.created_at}
            check_exists = SurveyAnswer.objects.filter(survey_id = survey.id, user = self.request.user).exists()
            _s['completed'] = check_exists
            s.append(_s)
        return s

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_menu'] = 'active'
        return context


class SurveyCompanyListView(LoginRequiredMixin,ListView):
    template_name = 'surveys/survey_list_company.html'
    model = Survey
    context_object_name = 'surveys'

    def get_queryset(self):
        surveys = Survey.objects.filter(published__exact = 'Yes',role=3).order_by('created_at')
        s = [];
        for survey in surveys:
            _s = {'id':survey.id,'title':survey.title,'description':survey.description,'created_at':survey.created_at}
            check_exists = SurveyAnswer.objects.filter(survey_id = survey.id, user = self.request.user).exists()
            _s['completed'] = check_exists
            s.append(_s)
        return s

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_menu'] = 'active'
        return context


@login_required()
def view_survey_as(request,view_as):
    if view_as == 'student':
        surveys = Survey.objects.filter(published__exact = 'Yes').order_by('created_at')

    return render(request,'surveys/as_student.html',{'surveys':surveys,'view_as':'student'})

@login_required()
def view_as_survey_view(request,pk):

    survey = Survey.objects.get(id = pk)
    return render(request,'surveys/as_student_survey_student.html',{'survey':survey,'view_as':'student'})


@login_required()
def add_survey(request):
    form = SurveyForm(request.POST,prefix = 'form_survey')
    if form.is_valid():
        survey = form.save(commit=False)
        survey.user = request.user
        survey.save()
        messages.success(request,'Successfully added survey')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:surveys')

@login_required()
def edit_survey(request,pk):
    survey_instance = Survey.objects.get(id=pk)
    form = SurveyForm(request.POST,instance=survey_instance)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully edited survey')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:surveys')


@login_required()
def update_status(request,pk):
    try:
        survey_instance = Survey.objects.get(id=pk)
        if survey_instance.published == 'Yes':
            survey_instance.published = 'No'
            survey_instance.save()
            messages.success(request,'Successfully unpublished survey')
        elif survey_instance.published == 'No':
            survey_instance.published = 'Yes'
            survey_instance.save()
            messages.success(request,'Successfully published survey')
    except:
        messages.warning(request,'An error occured, please try again later')

    return redirect('psycad:surveys')


@login_required()
def delete_survey(request,pk):
    try:
        survey_instance = Survey.objects.get(id=pk)
        survey_instance.delete()
        messages.success(request,'Successfully deleted survey')
    except :
        messages.warning(request,'An error occurred, please try again later')

    return redirect('psycad:surveys')


@login_required()
def survey_view_staff(request,pk):
    survey_instance = Survey.objects.get(id=pk)
    form_questions = QuestionForm(prefix = 'form_questions')
    categories = Category.objects.all()
    types = QuestionType.objects.all().order_by('type')
    survey_menu = 'active'

    questions = Question.objects.filter(survey = survey_instance)
    
    qn_stats = []
    qn_question = []

    for qn in questions :
        qn_map = {'question':qn.question,'id':qn.id}
        qn_question.append(qn_map)

        if qn.type.options == 'Yes' and qn.answers.count() > 0:
            qn_dict = {'qn':qn.question}
            choices = []

            for o in qn.type.type_options.all():

                count_true = 0
                for answer in qn.answers.all():
                    if answer.answer == o.option:
                        count_true = count_true + 1
                percentage = (count_true / qn.answers.count()) * 100
                choices_dict = {'option':o.option,'value':count_true,'total':qn.answers.count(),'percentage':percentage}
                print(choices_dict)

                choices.append(choices_dict)

            qn_dict['options'] = choices
            print(qn_dict)
            qn_stats.append(qn_dict)


    respondents = []
    for r in survey_instance.survey_answers.all():
        resp = {'id':r.id,'date':r.created_at,'user':r.user,'name':f'{r.user.first_name} {r.user.last_name}'}
        if r.user.roles_id == 3 or r.user.roles_id == 12:
            resp['type'] = "Company Representative"
            contact = CompanyContacts.objects.filter(user_id = r.user.id)
            if contact.exists():
                c = contact.first()
            resp['designation'] = c.company.company_name
        elif r.user.roles_id == 4 or r.user.roles_id == 6:
            resp['type'] = "Student"
            student = Student.objects.filter(user_id = r.user.id)
            if student.exists():
                stud = student.first()
                resp['designation'] = stud.department.department

        answers = Answer.objects.filter(surveyanswer = r).order_by('question_id')
        answer_list = []
        for q_l in qn_question:
            a  = answers.filter(question_id = q_l['id'])
            if a.exists():
                b = a.first()
                ans = {'answer':b.answer,'question':q_l['question']}
            else:
                ans = {'answer':"",'question':q_l['question']}
            answer_list.append(ans)

        resp['answers'] = answer_list

        respondents.append(resp)

    question_list = survey_instance.questions.order_by('question_number')

    return render(request,'surveys/survey_view.html',{'survey':survey_instance,'form_questions':form_questions,'categories':categories,'types':types,'survey_menu':survey_menu,'qn_stats':qn_stats,'respondents':respondents,'question_list':question_list})


@login_required()
def delete_survey_response_answer(request,survey_pk,pk):
    try:
        resp = SurveyAnswer.objects.get(id = pk)
        resp.delete()
        messages.success(request,'Successfully deleted response')
    except Exception as e:
        messages.warning(request, str(e))

    return redirect('psycad:survey_view_staff',pk=survey_pk)

@login_required()
def add_surveyquestion(request,pk):
    survey_instance = Survey.objects.get(id=pk)
    form = QuestionForm(request.POST,prefix='form_questions')
    if form.is_valid():
        question = form.save(commit=False)
        question.survey = survey_instance
        #question.tone_analyzer = request.POST['tone_analyzer']

        if request.POST['question_number'] != "":
            question.question_number = request.POST['question_number']
        question.save()
        messages.success(request,'Successfully added question')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:survey_view_staff',pk=pk)

@login_required()
def edit_surveyquestion(request,pk):
    question_instance = Question.objects.get(id = pk)
    form = QuestionForm(request.POST,instance = question_instance)
    if form.is_valid():
        question = form.save()
        if request.POST['question_number'] != "":
            question.question_number = request.POST['question_number']
        question.save()
        messages.success(request,'Successfully edited question')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:survey_view_staff',pk=question_instance.survey_id)


@login_required()
def delete_surveyquestion(request,pk):
    try:
        qn_instance = Question.objects.get(id=pk)
        qn_instance.delete()
        messages.success(request,'Successfully deleted question')
    except :
        messages.warning(request,'An error occurred, please try again later')

    return redirect('psycad:survey_view_staff',pk=qn_instance.survey_id)


@login_required()
def survey_categories(request):
    categories = Category.objects.all()
    form = CategoryForm()
    return render(request,'surveys/categories.html',{'categories':categories,'form':form})

@login_required()
def add_surveycategory(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully added a category')
    else:
        messages.warning(request, form.errors)

    return redirect('psycad:config_survey_categories')

@login_required()
def edit_surveycategory(request,pk):
    category_instance = Category.objects.get(id=pk)
    form = CategoryForm(request.POST,instance=category_instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully edited category')
    else:
        messages.warning(request, form.errors)

    return redirect('psycad:config_survey_categories')

@login_required()
def delete_surveycategory(request,pk):
    try:
        category_instance = Category.objects.get(id=pk)
        category_instance.delete()
        messages.success(request, 'Successfully deleted category')
    except :
        messages.warning(request, 'An error occurred, please try again later')

    return redirect('psycad:config_survey_categories')


@login_required()
def export_survey_csv(request,pk):
    survey_instance = Survey.objects.get(id=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{survey_instance.title}.csv"'

    writer = csv.writer(response)
    questions = []
    qn_id = []
    questions.append('Date')
    questions.append('Email')
    questions.append('Name')
    if survey_instance.role == 3:
        questions.append('Company')
    else:
        questions.append('Department')
    for qn in survey_instance.questions.order_by('id').all():
        questions.append(qn.question)
        qn_id.append(qn.id)
    writer.writerow(questions)

    surveyanswers = SurveyAnswer.objects.filter(survey = survey_instance)
    for s in surveyanswers:
        row = []
        row.append(s.created_at.strftime("%m/%d/%Y, %H:%M:%S"))
        row.append(f'{s.user.first_name} {s.user.last_name}')
        row.append(s.user.email)
        if s.user.roles_id == 3:
            contact = CompanyContacts.objects.filter(user_id = s.user.id)
            if contact.exists():
                c = contact.first()
                row.append(c.company.company_name)
            else:
                row.append('')

        elif s.user.roles_id == 6 or s.user.roles_id == 4:
            student = Student.objects.filter(user_id = s.user.id)
            if student.exists():
                stud = student.first()
                row.append(f'{stud.department.department}')
            else:
                row.append('')

        answers = Answer.objects.filter(surveyanswer = s).order_by('question_id')
        for id in qn_id:
            a  = answers.filter(question_id = id)
            if a.exists():
                b = a.first()
                ans = b.answer
            else:
                ans = ""
            row.append(ans)
        writer.writerow(row)

    return response


def export_survey_xls(request,pk):
    survey_instance = Survey.objects.get(id=pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{survey_instance.title}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('survey responses')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    questions = []
    qn_id = []

    questions.append('Date')
    questions.append('Email')
    questions.append('Name')
    if survey_instance.role == 3:
        questions.append('Company')
    else:
        questions.append('Department')
    for qn in survey_instance.questions.order_by('id').all():
        questions.append(qn.question)
        qn_id.append(qn.id)

    for col_num in range(len(questions)):
        ws.write(row_num, col_num, questions[col_num], font_style)

     # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    surveyanswers = SurveyAnswer.objects.filter(survey = survey_instance)
    for s in surveyanswers:
        row_num = row_num + 1
        row = []
        row.append(s.created_at.strftime("%m/%d/%Y, %H:%M:%S"))
        row.append(f'{s.user.first_name} {s.user.last_name}')
        row.append(s.user.email)
        if s.user.roles_id == 3:
            contact = CompanyContacts.objects.filter(user_id = s.user.id)
            if contact.exists():
                c = contact.first()
                row.append(c.company.company_name)
            else:
                row.append('')

        elif s.user.roles_id == 6 or s.user.roles_id == 4:
            student = Student.objects.filter(user_id = s.user.id)
            if student.exists():
                stud = student.first()
                row.append(f'{stud.department.department}')
            else:
                row.append('')
        answers = Answer.objects.filter(surveyanswer = s).order_by('question_id')
        for id in qn_id:
            a  = answers.filter(question_id = id)

            if a.exists():
                b = a.first()
                ans = b.answer
            else:
                ans = ""
            row.append(ans)

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response


@login_required()
def survey_view(request,pk):
    s = Survey.objects.filter(id = pk,published='Yes')
    if s.exists():
        survey = s.first()
        questions = Question.objects.filter(survey = survey).order_by('question_number')
        if request.user.roles_id == 6 or request.user.roles_id == 4:
            return render(request,'surveys/survey_student.html',{'survey':survey,'survey_menu':'active','questions':questions})
        if request.user.roles_id == 12 or request.user.roles_id == 3:
            return render(request,'surveys/survey_company.html',{'survey':survey,'survey_menu':'active','questions':questions})
    else:
        messages.warning(request,'Sorry the survey does not exist')
        if request.user.roles_id == 6 or request.user.roles_id == 4:
            return redirect('student:surveys')
        if request.user.roles_id == 12 or request.user.roles_id == 3:
            return redirect('contact:surveys')

    messages.warning(request,'Sorry you are not logged on')
    return redirect('accounts:logout')

@login_required()
def survey_view_add(request,pk):
    survey_instance = Survey.objects.get(id = pk)

    if request.method == 'POST':

        surveyanswer = SurveyAnswer.objects.create(survey = survey_instance, user = request.user)
        surveyanswer.save()

        for qn in survey_instance.questions.all():
            if qn.choice == 'one':
                if '{}'.format(qn.id) in request.POST:
                    a = request.POST['{}'.format(qn.id)]
                    answer = Answer.objects.create(answer=a,question=qn,surveyanswer=surveyanswer)
                    answer.save()
            else:
                if '{}[]'.format(qn.id) in request.POST:
                    a = ",".join(request.POST.getlist('{}[]'.format(qn.id)))
                    answer = Answer.objects.create(answer=a,question=qn,surveyanswer=surveyanswer)
          
                    answer.save()


        messages.success(request,'Successfully saved survey')

        if request.user.roles_id == 4 or request.user.roles_id == 6:
            return redirect('student:surveys')
        if request.user.roles_id == 3 or request.user.roles_id == 12:
            return redirect('contact:surveys')

@login_required()
def survey_analyze(request,pk):
    survey = Survey.objects.get(id=pk)
    ok = Answer.objects.filter(question__survey = survey).annotate(frequency=Count("answer"))
    print(ok)
    return redirect('student:surveys')


@login_required()
def survey_copy(request,pk):
    try:
        survey = Survey.objects.get(id=pk)
        survey_copy = Survey.objects.create(
            title = request.POST['title'],
            description = request.POST['description'],
            user = request.user,
            category = survey.category,
            role = survey.role,
        )

        for qn in survey.questions.all():
            Question.objects.create(
                question = qn.question,
                type = qn.type,
                choice = qn.choice,
                survey = survey_copy,
                question_number = qn.question_number
            )
        messages.success(request,"Successfully copied survey")
    except Exception as e:
        messages.warning(request,f"An error has occurred: {str(e)}")

    return redirect('psycad:surveys')
