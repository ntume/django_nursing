import datetime
import threading
from django.shortcuts import render, redirect,HttpResponse,Http404
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from accounts.forms import UserForm
from accounts.models import Role, User
from accounts.views import password_gen
from college.print_master_plan import MyPrintMasterPlan
from configurable.models import ClinicalProcedureThemeTask
from django_nursing.email_functions import send_email_general
from django_nursing.utility_functions import sunday_year_weeks
from students.models import StudentLearningProgrammeRegistration, StudentRegistrationModule
from .models import *
from .forms import *
from decimal import Decimal


# Create your views here.

@login_required()
def moderator_dashboard(request):
    
    return render(request,'college/moderator/dashboard.html',{'dash_menu':'--active'})

class ModeratorLearningProgrammeCohortRegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'college/moderator/learing_programme_cohort_registration_period.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 7:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorLearningProgrammeCohortRegistrationPeriodList, self).get(*args, **kwargs)

    def get_queryset(self):
        today = datetime.date.today()
        moderator = Moderator.objects.get(user = self.request.user)
        learning_programmes = []
        lps = (LearningProgrammeCohortRegistrationPeriod.
                 objects.
                 filter(
                     learning_programme_cohort__learning_programme_id = self.kwargs['pk'],
                     start_date__lte = today, 
                     end_date__gte = today))
        
        for lp in lps:
            lp_map = {'lp':lp,'procedures':False,'modules':False}
            if moderator in lp.summative_procedures_moderators.all():
                lp_map['procedures'] = True
                
            for module in lp.modules.all():
                if module.moderator == moderator:
                    lp_map['modules'] = True
            
            if lp_map['modules'] == True or  lp_map['procedures'] == True:      
                learning_programmes.append(lp_map)     
            
        return learning_programmes
                            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = learning_programme
        context['cohort_menu'] = '--active'
        #check if moderator for procedures
        return context
    
    

    
class ModeratorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList(LoginRequiredMixin,ListView):
    template_name = 'college/moderator/summative_procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 7:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 7:
            #check if added as a moderator, if not return None
            return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    
      

class ModeratorLearningProgrammeCohortRegistrationPeriodModuleList(LoginRequiredMixin,ListView):
    template_name = 'college/moderator/modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 7:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorLearningProgrammeCohortRegistrationPeriodModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'],moderator__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    


class ModeratorLearningProgrammeCohortRegistrationPeriodModuleStudentList(LoginRequiredMixin,ListView):
    template_name = 'college/moderator/modules_students_marks.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 7:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorLearningProgrammeCohortRegistrationPeriodModuleStudentList, self).get(*args, **kwargs)

    def get_queryset(self):
        students = list(StudentRegistrationModule.
                        objects.
                        filter(module_id = self.kwargs['module_pk']).
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id',
                            'summative_assessor1',
                            'summative_assessor2',
                            'year_mark',
                           )
                        )
        return  students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['module'] = CohortRegistrationPeriodModule.objects.get(id = self.kwargs['module_pk'])
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context



@login_required()
def moderator_learning_programme_cohort_module_moderators_report(request,pk):
    
    if request.user.logged_in_role_id == 7:
        
        moderator = None

        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        learning_programme_cohort_period = module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        
        check_moderator = Moderator.objects.filter(user = request.user)
        if check_moderator.exists():
            moderator = check_moderator.first()
                        
        assessment = []
        
        #check if report exists

        check_report_user = CohortRegistrationPeriodModuleModerationReport.objects.filter(module = module)

        if check_report_user.exists():
            report = check_report_user.first()
        else:
            report = CohortRegistrationPeriodModuleModerationReport.objects.create(module = module,moderator=moderator)
        
        assessments = list(LearningProgrammePeriodModerationCriteria.
                           objects.
                           filter(
                               learning_programme_period = module.cohort_registration_period.period,                               
                           ).values('criteria','id','question_type','number','role'))
       
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'criteria':ass['criteria'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number'],
                       'role':ass['role']}
            
            
            check_answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                filter(
                                    report = report,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.remarks
                
            
            
            assessment.append(ass_map)

        return render(request,'college/moderator/theory_module_moderation.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'module':module,
                                                                          'report':report,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def moderator_learning_programme_cohort_module_moderators_report_answer(request,pk,report_pk,assessment_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 7:
        
        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        learning_programme_cohort_period = module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        

        assessment = (LearningProgrammePeriodModerationCriteria.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        attempt = CohortRegistrationPeriodModuleModerationReport.objects.get(id = report_pk)
        
        #check if assessment exists:
        check_answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    report_id = report_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.answer = request.GET['answer']
            answer.save()
            messages.success(request,'Successfully edited criteria')
        else:
            answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    report_id = report_pk,
                                    answer = request.GET['answer']
                                ))
            messages.success(request,'Successfully Completed Criteria')
        
            
        return render(request,
                      'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        

@login_required()
def moderator_learning_programme_cohort_module_moderators_report_comment(request,pk,report_pk,assessment_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 7:
        
        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        learning_programme_cohort_period = module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        

        assessment = (LearningProgrammePeriodModerationCriteria.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        attempt = CohortRegistrationPeriodModuleModerationReport.objects.get(id = report_pk)
        
        #check if assessment exists:
        check_answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    report_id = report_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.remarks = request.GET['comment']
            answer.save()
            messages.success(request,'Successfully edited Remarks')
        else:
            answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    report_id = report_pk,
                                    remarks = request.GET['comment']
                                ))
            messages.success(request,'Successfully added Remarks')
            
        
            
        return render(request,'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        

@login_required()
def moderator_learning_programme_cohort_module_moderators_report_moderators_final_comment(request,pk,report_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 7:
        
        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        
        
        report = CohortRegistrationPeriodModuleModerationReport.objects.get(id = report_pk)
        
        report.comment = request.GET['comment']
        report.save()
        messages.success(request,'Successfully saved Comments')
         
        return render(request,'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def moderator_learning_programme_cohort_module_moderators_report_moderators_feedback(request,pk,report_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 7:
        
        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        
        
        report = CohortRegistrationPeriodModuleModerationReport.objects.get(id = report_pk)
        
        report.moderators_feedback = request.GET['moderators_feedback']
        report.save()
        messages.success(request,'Successfully saved Moderators Feedback')
         
        return render(request,'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def moderator_learning_programme_cohort_module_moderators_report_recommendations(request,pk,report_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 7:
        
        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        
        
        report = CohortRegistrationPeriodModuleModerationReport.objects.get(id = report_pk)
        
        report.recommendations = request.GET['recommendations']
        report.save()
        messages.success(request,'Successfully saved recommendations')
         
        return render(request,'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')