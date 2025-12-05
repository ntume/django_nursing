from django.urls import path

from students import generate_student_card, views_lp
from students.print_excel import print_learner_wil_hours_list_excel
from students.print_vaccination_list import print_cohort_vaccination_list_excel
from students.views_leave import LeaveLearningProgrammeCohortList, LeaveLearningProgrammeCohortRegistrationPeriodList, RequestedLeaveList, requested_leave_cohorts_registrations_leave_filter, requested_leave_edit, requested_leave_list_filter, student_leave, student_leave_request_submission,RequestedLeaveReportList
from students.views_lp import FacilityWardStudents, StudentLearningProgrammeList, StudentLearningProgrammeRegistrationList, StudentLearningProgrammeRegistrationModuleAssessmentsList, StudentLearningProgrammeRegistrationModuleList, StudentLearningProgrammeRegistrationModuleRegisterList, StudentLearningProgrammeRegistrationModuleUnitsList, StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetList, StudentLearningProgrammeRegistrationSimulatedWILLogsheetList, add_logsheet, ajax_student_fetch_facility_discipline_wards, delete_logsheet, edit_learners_shifts, edit_logsheet, facility_ward_students, facility_ward_students_competency, fetch_students_ward_shifts, student_learning_programme_registrations_module_register_sign, student_view_logsheet, view_learners_shift_days, wil_logsheet_hours
from students.views_student import add_profile_next_of_kin_details, delete_profile_next_of_kin_details, edit_profile_address_details, edit_profile_education_details, edit_profile_next_of_kin_details, edit_profile_personal_details, edit_profile_picture, student_dashboard, student_profile
from . import views

app_name = 'students'

urlpatterns = [
    #path('signup/',views.StudentCreateView.as_view(),name='signup'),
    path('learning/programme/cohort/<int:pk>/',views.CohortLearnerList.as_view(),name='cohort_learners'),
    path('learning/programme/cohort/<int:pk>/group/onboarding',views.request_group_on_boarding,name='request_group_on_boarding'),
    path('learning/programme/cohort/<int:pk>/add/learner',views.add_learner_programme_cohort,name='add_learner_programme_cohort'),
    path('learning/programme/cohort/<int:pk>/learner/<int:learner_pk>/remove',views.remove_learner_programme,name='remove_learner_programme'),
    path('ajax/fetch/id/number',views.ajax_validate_id_number,name='ajax_validate_id_number'),
    path('ajax/fetch/highschools',views.ajax_fetch_highschools,name='ajax_fetch_highschools'),
    path('learning/programme/cohort/learner/<int:pk>/view/<int:page>/',views.view_learner_programme,name='view_learner_programme'),
    path('learning/programme/cohort/learner/<int:pk>/view/details',views.edit_learner_programme_details,name='edit_learner_programme_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/address',views.edit_learner_address_details,name='edit_learner_address_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/education',views.edit_learner_education_details,name='edit_learner_education_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/next/kin',views.edit_learner_next_of_kin_details,name='edit_learner_next_of_kin_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/attachments',views.learner_attachment_bulk_upload,name='learner_attachment_bulk_upload'),
    path('learning/programme/cohort/learner/<int:pk>/view/check/learner',views.check_learner_form_details,name='check_learner_form_details'),

    path('learning/programme/cohort/learner/<int:pk>/vaccinations',views.CohortLearnerVaccinationList.as_view(),name='cohort_learner_vaccinations'),
    path('learning/programme/cohort/learner/<int:pk>/vaccinations/add',views.add_learner_programme_cohort_student_vaccination,name='add_learner_programme_cohort_student_vaccination'),
    path('learning/programme/cohort/learner/<int:pk>/vaccinations/<int:dose_pk>/edit',views.edit_learner_programme_cohort_student_vaccination,name='edit_learner_programme_cohort_student_vaccination'),
    path('learning/programme/cohort/learner/<int:pk>/vaccinations/<int:dose_pk>/delete',views.delete_learner_programme_cohort_student_vaccination,name='delete_learner_programme_cohort_student_vaccination'),
    path('learning/programme/cohort/<int:pk>/vaccinations',views.CohortAllLearnersVaccinationsList.as_view(),name='cohort_all_learners_vaccinations'),
    path('learning/programme/cohort/<int:pk>/vaccinations/print',print_cohort_vaccination_list_excel,name='print_cohort_vaccination_list_excel'),
    

    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:period_pk>/view',views.view_learner_programme_registration,name='view_learner_programme_registration'),
    
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/module/<int:module_pk>/registration',views.learner_programme_registration_module_add,name='learner_programme_registration_module_add'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/module/<int:module_pk>/remove',views.learner_programme_registration_module_remove,name='learner_programme_registration_module_remove'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/check/form',views.check_learner_registration_form_details,name='check_learner_registration_form_details'),
    
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/submit',views.learner_registration_form_submit,name='learner_registration_form_submit'),
    
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:period_pk>/kin/add',views.add_lp_next_of_kin_details,name='add_lp_next_of_kin_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:period_pk>/kin/<int:next_of_kin_pk>/edit',views.edit_lp_next_of_kin_details,name='edit_lp_next_of_kin_details'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:period_pk>/kin/<int:next_of_kin_pk>/delete',views.delete_lp_next_of_kin_details,name='delete_lp_next_of_kin_details'),
    
    
    path('learning/programme/cohort/<int:pk>/registration/period/<int:period_pk>/students',views.learning_programme_cohort_registrations,name='learning_programme_cohort_registrations'),
    path('learning/programme/cohort/<int:pk>/registration/period/<int:period_pk>/students/wil/hours',views.students_wil_logsheet_hours,name='students_wil_logsheet_hours'),
    path('learning/programme/cohort/<int:pk>/registration/period/<int:period_pk>/students/wil/hours/print',print_learner_wil_hours_list_excel,name='print_learner_wil_hours_list_excel'),

    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/education/plan',views.view_learner_educational_plan,name='view_learner_educational_plan'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/education/plan/assign/hospital',views.assign_learner_educational_plan_hospital,name='assign_learner_educational_plan_hospital'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/education/plan/assign/phc',views.assign_learner_educational_plan_phc,name='assign_learner_educational_plan_phc'),
    path('learning/programme/cohort/learner/<int:pk>/view/registration/<int:registration_pk>/education/plan/<int:week_pk>/edit',views.edit_learner_educational_plan,name='edit_learner_educational_plan'),
    
    path('learning/programme/cohort/learner/view/registration/education/plan/<int:pk>',views.view_learners_days,name='view_learners_days'),
    path('learning/programme/cohort/learner/view/registration/education/plan/assign/ward/<int:pk>',views.edit_learners_days,name='edit_learners_days'),
    
    path('learning/programme/cohort/learner/view/registration/education/plan/<int:pk>/week/<int:week_pk>/daily/timetable',views.view_learners_days_timetable,name='view_learners_days_timetable'),
    
    
    path('learning/programme/cohort/learner/view/registration/<int:pk>/education/plan/sections',views.view_learner_educational_plan_sections,name='view_learner_educational_plan_sections'),
    path('learning/programme/cohort/learner/view/registration/<int:pk>/education/plan/sections/add/wil/requirement',views.view_learner_educational_plan_sections_add_wil_requirement,name='view_learner_educational_plan_sections_add_wil_requirement'),
    path('learning/programme/cohort/learner/view/registration/<int:pk>/education/plan/sections/wil/requirement/<int:wil_pk>/edit',views.view_learner_educational_plan_sections_edit_wil_requirement,name='view_learner_educational_plan_sections_edit_wil_requirement'),
    path('learning/programme/cohort/learner/view/registration/<int:pk>/education/plan/sections/wil/requirement/<int:wil_pk>/delete',views.view_learner_educational_plan_sections_delete_wil_requirement,name='view_learner_educational_plan_sections_delete_wil_requirement'),
    
    
    path('profile/learning/programmes',views.learner_learning_programmes,name='learner_learning_programmes'),
    path('profile/modules',views.learner_registered_modules,name='learner_registered_modules'),
    
    path('dashboard',student_dashboard,name='student_dashboard'),
    path('leave/request/',student_leave,name='student_leave'),
    path('leave/request/<int:pk>/submit',student_leave_request_submission,name='student_leave_request_submission'),
    
    path('admin/leave/requests/cohort/<int:pk>',RequestedLeaveReportList.as_view(),name='requested_leave_report_list'),
    path('admin/leave/requests/cohort/<int:pk>/filter',requested_leave_list_filter,name='requested_leave_list_filter'),

    path('leave/requests/cohort/<int:pk>',LeaveLearningProgrammeCohortList.as_view(),name='leave_learning_programme_cohorts'),
    path('leave/requests/cohort/<int:pk>/registrations/',LeaveLearningProgrammeCohortRegistrationPeriodList.as_view(),name='requested_leave_cohorts_registrations'),
    path('leave/requests/cohort/registrations/<int:pk>/leave',RequestedLeaveList.as_view(),name='requested_leave_cohorts_registrations_leave'),
    path('leave/requests/cohort/registrations/<int:pk>/leave/filter',requested_leave_cohorts_registrations_leave_filter,name='requested_leave_cohorts_registrations_leave_filter'),
    path('leave/requests/cohort/registrations/<int:pk>/leave/<int:leave_pk>/edit',requested_leave_edit,name='requested_leave_edit'),
    
    path('profile/<int:page>',student_profile,name='student_profile'),
    path('profile/<int:pk>/personal/details/save',edit_profile_personal_details,name='edit_profile_personal_details'),
    path('profile/<int:pk>/education/save',edit_profile_education_details,name='edit_profile_education_details'),
    path('profile/<int:pk>/address/save',edit_profile_address_details,name='edit_profile_address_details'),
    path('profile/<int:pk>/profile/picture/save',edit_profile_picture,name='edit_profile_picture'),
    path('profile/<int:pk>/nextofkin/add',add_profile_next_of_kin_details,name='add_profile_next_of_kin_details'),
    path('profile/<int:pk>/nextofkin/<int:next_of_kin_pk>/edit',edit_profile_next_of_kin_details,name='edit_profile_next_of_kin_details'),
    path('profile/<int:pk>/nextofkin/<int:next_of_kin_pk>/delete',delete_profile_next_of_kin_details,name='delete_profile_next_of_kin_details'),

    path('student/learning/programmes',StudentLearningProgrammeList.as_view(),name='student_learning_programmes'),
    path('student/learning/programme/<int:pk>/registrations',StudentLearningProgrammeRegistrationList.as_view(),name='student_learning_programme_registrations'),
    path('student/learning/programme/registrations/<int:pk>/modules',StudentLearningProgrammeRegistrationModuleList.as_view(),name='student_learning_programme_registrations_modules'),
    path('student/learning/programme/registrations/<int:pk>/module/<int:module_pk>/units',StudentLearningProgrammeRegistrationModuleUnitsList.as_view(),name='student_learning_programme_registrations_module_units'),
    path('student/learning/programme/registrations/<int:pk>/module/<int:module_pk>/assessments',StudentLearningProgrammeRegistrationModuleAssessmentsList.as_view(),name='student_learning_programme_registrations_module_assessments'),
    path('student/learning/programme/registrations/<int:pk>/module/<int:module_pk>/registers',StudentLearningProgrammeRegistrationModuleRegisterList.as_view(),name='student_learning_programme_registrations_module_registers'),
    path('student/learning/programme/registrations/<int:pk>/module/<int:module_pk>/register/<int:register_pk>',student_learning_programme_registrations_module_register_sign,name='student_learning_programme_registrations_module_register_sign'),
    
    
    
    
    path('student/learning/programme/<int:pk>/registrations/logsheets',student_view_logsheet,name='student_view_logsheet'),
    
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/<int:block_pk>/<int:month_pk>/simulated',StudentLearningProgrammeRegistrationSimulatedWILLogsheetList.as_view(),name='simulated_wil_logsheets'),
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/<int:block_pk>/<int:month_pk>/non-simulated',StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetList.as_view(),name='non_simulated_wil_logsheets'),
    
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/<int:block_pk>/<int:month_pk>/add',add_logsheet,name='add_logsheet'),
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/<int:block_pk>/<int:month_pk>/edit/<int:entry_pk>',edit_logsheet,name='edit_logsheet'),
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/<int:block_pk>/<int:month_pk>/delete/<int:entry_pk>',delete_logsheet,name='delete_logsheet'),
    path('student/learning/programme/registration/<int:pk>/registrations/logsheets/wil/hours/summary',wil_logsheet_hours,name='wil_logsheet_hours'),
    path('ajax/student/learning/programme/registration/<int:pk>/fetch/wards',ajax_student_fetch_facility_discipline_wards,name='ajax_student_fetch_facility_discipline_wards'),   
    path('generate/student/card/<int:pk>',generate_student_card.generate_student_card,name='generate_student_card'),
    path('generate/cohort/<int:pk>/student/cards',generate_student_card.generate_cohort_student_cards,name='generate_cohort_student_cards'),
    
    
]

lecturerpatterns = [
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/<int:period_pk>/students/',views_lp.lecturer_learning_programme_cohort_students,name='lecturer_learning_programme_cohort_students'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures',views_lp.lecturer_learning_programme_cohort_students_view_wil_procedures,name='lecturer_learning_programme_cohort_students_view_wil_procedures'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/attendance/capture',views_lp.lecturer_learning_programme_cohort_procedure_student_attendance,name='lecturer_learning_programme_cohort_procedure_student_attendance'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/attendance/save',views_lp.lecturer_learning_programme_cohort_procedure_student_attendance_save,name='lecturer_learning_programme_cohort_procedure_student_attendance_save'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/attendance/groups',views_lp.LecturerLearningProgrammeCohortProcedureAssessmentAttendanceList.as_view(),name='lecturer_learning_programme_cohort_procedure_student_assessment_attendance_group'),
    path('lecturer/learning/programme/cohort/registration/procedure/attendance/groups/<int:pk>',views_lp.LecturerLearningProgrammeCohortProcedureStudentAsessmentList.as_view(),name='lecturer_learning_programme_cohort_procedure_student_attendance_group_students'),
    path('lecturer/learning/programme/cohort/registration/procedure/attendance/groups/<int:pk>/competency',views_lp.lecturer_learning_programme_cohort_procedure_student_attendance_group_students_competency,name='lecturer_learning_programme_cohort_procedure_student_attendance_group_students_competency'),   
    
    path('lecturer/learning/programme/cohort/registration/<int:pk>/module/<int:module_pk>/assessment/<int:assessment_pk>',views_lp.lecturer_learning_programme_cohort_module_student_assessment_list,name='lecturer_learning_programme_cohort_module_student_assessment_list'),
    path('lecturer/learning/programme/cohort/registration/<int:pk>/module/assessment/<int:assessment_pk>/save',views_lp.lecturer_learning_programme_cohort_module_student_assessment_save,name='lecturer_learning_programme_cohort_module_student_assessment_save'),    
    path('lecturer/learning/programme/cohort/registration/<int:pk>/module/<int:module_pk>/assessment/students',views_lp.lecturer_learning_programme_cohort_module_students,name='lecturer_learning_programme_cohort_module_students'),

    path('lecturer/learning/programme/cohort/registration/<int:pk>/module/<int:module_pk>/summative/assessor/students',views_lp.lecturer_learning_programme_cohort_module_summative_student_assessment_list,name='lecturer_learning_programme_cohort_module_summative_student_assessment_list'),    
    path('lecturer/learning/programme/cohort/registration/module/<int:pk>/summative/assessor/<int:assessor>/save',views_lp.lecturer_learning_programme_cohort_module_summative_student_assessment_save,name='lecturer_learning_programme_cohort_module_summative_student_assessment_save'),
    

    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/formative/assessment/students',views_lp.LecturerLearningProgrammeCohortProcedureStudentFormativeAsessmentList.as_view(),name='lecturer_learning_programme_cohort_procedure_student_formative_assessment_list'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/formative/assessment/students/attempt/add',views_lp.lecturer_learning_programme_cohort_procedure_formative_student_attempt_add,name='lecturer_learning_programme_cohort_procedure_formative_student_attempt_add'),
    
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/assessment',views_lp.lecturer_learning_programme_cohort_students_view_wil_procedures_assessment,name='lecturer_learning_programme_cohort_students_view_wil_procedures_assessment'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/<int:assessment_pk>/save/answer',views_lp.save_procedure_answer,name='save_procedure_answer'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/<int:assessment_pk>/save/comment',views_lp.save_procedure_comment,name='save_procedure_comment'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/process/final/mark',views_lp.process_procedure_formative_assessment_final_mark,name='process_procedure_formative_assessment_final_mark'),
    
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/summative/assessment/students',views_lp.LecturerLearningProgrammeCohortProcedureStudentSummativeAsessmentList.as_view(),name='lecturer_learning_programme_cohort_procedure_student_summative_assessment_list'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/summative/assessment/students/attempt/add',views_lp.lecturer_learning_programme_cohort_procedure_summative_student_attempt_add,name='lecturer_learning_programme_cohort_procedure_summative_student_attempt_add'),
    
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/assessment',views_lp.lecturer_learning_programme_cohort_students_view_wil_procedures_summative_assessment,name='lecturer_learning_programme_cohort_students_view_wil_procedures_summative_assessment'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/<int:assessment_pk>/save/answer',views_lp.save_procedure_summative_answer,name='save_procedure_summative_answer'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/<int:assessment_pk>/save/comment',views_lp.save_procedure_summative_comment,name='save_procedure_summative_comment'),
    path('lecturer/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/process/final/mark',views_lp.process_procedure_summative_assessment_final_mark,name='process_procedure_summative_assessment_final_mark'),
    
]

facilitypatterns = [
    path('unit/manager/<int:pk>',FacilityWardStudents.as_view(),name='facility_ward_students'),
    path('unit/manager/<int:pk>/mentor/approval',facility_ward_students_competency,name='facility_ward_students_competency'),
    path('unit/manager/shifts/month/<str:month>',fetch_students_ward_shifts,name='fetch_students_ward_shifts'),
    path('unit/manager/shifts/student/<int:pk>/month/<str:month>',view_learners_shift_days,name='view_learners_shift_days'),   
    path('unit/manager/shifts/student/<int:pk>/month/<str:month>/edit/shifts',edit_learners_shifts,name='edit_learners_shifts'), 
]


coassessorpatterns = [
    

    path('coassessor/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/formative/assessment/students',views_lp.CoAssessorLearningProgrammeCohortProcedureStudentFormativeAsessmentList.as_view(),name='co_assessor_learning_programme_cohort_procedure_student_formative_assessment_list'),
    
    path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/assessment',views_lp.co_assessor_learning_programme_cohort_students_view_wil_procedures_assessment,name='co_assessor_learning_programme_cohort_students_view_wil_procedures_assessment'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/<int:assessment_pk>/save/answer',views_lp.save_procedure_answer,name='save_procedure_answer'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/<int:assessment_pk>/save/comment',views_lp.save_procedure_comment,name='save_procedure_comment'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/entry/process/final/mark',views_lp.process_procedure_formative_assessment_final_mark,name='process_procedure_formative_assessment_final_mark'),
    
    path('coassessor/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/summative/assessment/students',views_lp.CoAssessorLearningProgrammeCohortProcedureStudentSummativeAsessmentList.as_view(),name='co_assessor_learning_programme_cohort_procedure_student_summative_assessment_list'),
    
    path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/assessment',views_lp.co_assessor_learning_programme_cohort_students_view_wil_procedures_summative_assessment,name='co_assessor_learning_programme_cohort_students_view_wil_procedures_summative_assessment'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/<int:assessment_pk>/save/answer',views_lp.save_procedure_summative_answer,name='save_procedure_summative_answer'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/<int:assessment_pk>/save/comment',views_lp.save_procedure_summative_comment,name='save_procedure_summative_comment'),
    #path('coassessor/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/entry/process/final/mark',views_lp.process_procedure_summative_assessment_final_mark,name='process_procedure_summative_assessment_final_mark'),
    
]


moderatorpatterns = [
    
    path('moderator/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/summative/assessment/students',views_lp.ModeratorLearningProgrammeCohortProcedureStudentSummativeAsessmentList.as_view(),name='moderator_learning_programme_cohort_procedure_student_summative_assessment_list'),    
    path('moderator/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/assessment',views_lp.moderator_learning_programme_cohort_students_view_wil_procedures_summative_assessment,name='moderator_learning_programme_cohort_students_view_wil_procedures_summative_assessment'),
        
]

programmecoordinatorpatterns = [
    
    path('programme/coordinator/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/summative/assessment/students',views_lp.ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentSummativeAsessmentList.as_view(),name='programme_coordinator_learning_programme_cohort_procedure_student_summative_assessment_list'),
    path('programme/coordinator/learning/programme/cohort/<int:pk>/registration/procedure/<int:procedure_pk>/formative/assessment/students',views_lp.ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentFormativeAsessmentList.as_view(),name='programme_coordinator_learning_programme_cohort_procedure_student_formative_assessment_list'),
    path('programme/coordinator/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/assessment',views_lp.programme_coordinator_learning_programme_cohort_students_view_wil_procedures_assessment,name='programme_coordinator_learning_programme_cohort_students_view_wil_procedures_assessment'),
    path('programme/coordinator/learning/programme/cohort/<int:pk>/registration/period/students/procedures/<int:attempt_pk>/summative/assessment',views_lp.programme_coordinator_learning_programme_cohort_students_view_wil_procedures_summative_assessment,name='programme_coordinator_learning_programme_cohort_students_view_wil_procedures_summative_assessment'),
       
]


 
urlpatterns = urlpatterns + lecturerpatterns + facilitypatterns + coassessorpatterns + moderatorpatterns + programmecoordinatorpatterns