from django.urls import path

from college import views_co_assessor, views_lecturer
from college.views_facility import co_assessor_dashboard, facility_hod_dashboard
from college.views_moderator import ModeratorLearningProgrammeCohortRegistrationPeriodList, ModeratorLearningProgrammeCohortRegistrationPeriodModuleList, ModeratorLearningProgrammeCohortRegistrationPeriodModuleStudentList, ModeratorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList, moderator_dashboard, moderator_learning_programme_cohort_module_moderators_report, moderator_learning_programme_cohort_module_moderators_report_answer, moderator_learning_programme_cohort_module_moderators_report_comment, moderator_learning_programme_cohort_module_moderators_report_moderators_feedback, moderator_learning_programme_cohort_module_moderators_report_moderators_final_comment, moderator_learning_programme_cohort_module_moderators_report_recommendations
from . import views
from . import views

app_name = 'college'

urlpatterns = [
    path('campuses',views.CollegeCampusList.as_view(),name='college_campuses'),
    path('campuses/add',views.college_campus_add,name='college_campus_add'),
    path('campuses/<int:pk>/edit',views.college_campus_edit,name='college_campus_edit'),
    path('campuses/<int:pk>/delete',views.college_campus_delete,name='college_campus_delete'),
    
    path('healthcare/facilities/',views.HealthcareFacilitiesList.as_view(),name='health_care_facilities'),
    path('healthcare/facilities/add',views.health_care_facility_add,name='health_care_facility_add'),
    path('healthcare/facilities/<int:pk>/edit',views.health_care_facility_edit,name='health_care_facility_edit'),
    path('healthcare/facilities/<int:pk>/delete',views.health_care_facility_delete,name='health_care_facility_delete'),
    path('healthcare/facilities/<int:pk>/learning/programme/add',views.health_care_facility_learning_programme_add,name='health_care_facility_learning_programme_add'),
    path('healthcare/facilities/<int:pk>/learning/programme/<int:lp_pk>/edit',views.health_care_facility_learning_programme_edit,name='health_care_facility_learning_programme_edit'),
    path('healthcare/facilities/learning/programme/<int:pk>/delete',views.health_care_facility_learning_programme_delete,name='health_care_facility_learning_programme_delete'),
    
    path('healthcare/facilities/<int:pk>/discipline/add',views.health_care_facility_discipline_add,name='health_care_facility_discipline_add'),
    path('healthcare/facilities/<int:pk>/discipline/<int:lp_pk>/edit',views.health_care_facility_discipline_edit,name='health_care_facility_discipline_edit'),
    path('healthcare/facilities/discipline/<int:pk>/delete',views.health_care_facility_discipline_delete,name='health_care_facility_discipline_delete'),
    
    path('healthcare/facilities/<int:pk>/ward/add',views.health_care_facility_wards_add,name='health_care_facility_wards_add'),
    path('healthcare/facilities/ward/<int:pk>/delete',views.health_care_facility_ward_delete,name='health_care_facility_ward_delete'),
    
    path('healthcare/facility/<int:pk>/hods/',views.HealthcareFacilityHODList.as_view(),name='health_care_facility_hods'),
    path('healthcare/facility/<int:pk>/hods/add',views.health_care_facility_hod_add,name='health_care_facility_hod_add'),
    path('healthcare/facility/<int:pk>/hod/<int:hod_pk>/edit',views.health_care_facility_hod_edit,name='health_care_facility_hod_edit'),
    path('healthcare/facility/<int:pk>/hod/<int:hod_pk>/delete',views.health_care_facility_hod_delete,name='health_care_facility_hod_delete'),
    path('healthcare/facility/<int:pk>/hod/<int:hod_pk>/reset',views.health_care_facility_hod_reset_password,name='health_care_facility_hod_reset_password'),
    path('healthcare/facility/<int:pk>/hod/<int:hod_pk>/wards/add',views.health_care_facility_hod_ward_add,name='health_care_facility_hod_ward_add'),
    path('healthcare/facility/<int:pk>/hod/<int:hod_pk>/wards/<int:ward_pk>/remove',views.health_care_facility_hod_ward_remove,name='health_care_facility_hod_ward_remove'),
    
    
    path('moderator/list/',views.ModeratorsList.as_view(),name='moderators'),
    path('moderator/list/add',views.moderator_add,name='moderator_add'),
    path('moderator/list/<int:pk>/edit',views.moderator_edit,name='moderator_edit'),
    path('moderator/list/<int:pk>/delete',views.moderator_delete,name='moderator_delete'),
    path('moderator/list/<int:pk>/reset',views.moderator_reset_password,name='moderator_reset_password'),
     
    path('registration/periods/',views.RegistrationPeriodList.as_view(),name='registration_period_list'),
    path('registration/period/add',views.registration_period_add,name='registration_period_add'),
    path('registration/period/<int:pk>/edit',views.registration_period_edit,name='registration_period_edit'),
    path('registration/period/<int:pk>/delete',views.registration_period_delete,name='registration_period_delete'),
    path('registration/period/<int:pk>/add/learning/programme',views.registration_period_learning_programme_period_add,name='registration_period_learning_programme_period_add'),
    path('registration/period/learning/programme/<int:pk>/delete',views.registration_period_learning_programme_period_delete,name='registration_period_learning_programme_period_delete'),
    
    
    path('registration/periods/programme/<int:pk>/modules',views.LearningProgrammeRegistrationModulesList.as_view(),name='learning_programme_registration_modules'),
    path('registration/periods/programme/<int:pk>/modules/add',views.learning_programme_registration_modules_add,name='learning_programme_registration_modules_add'),
    path('registration/periods/programme/<int:pk>/modules/<int:module_pk>/edit',views.learning_programme_registration_modules_edit,name='learning_programme_registration_modules_edit'),
    path('registration/periods/programme/<int:pk>/modules/<int:module_pk>/delete',views.learning_programme_registration_modules_delete,name='learning_programme_registration_modules_delete'),
    path('registration/periods/programme/<int:pk>/modules/copy/assessments',views.copy_registration_modules_assessments,name='copy_registration_modules_assessments'),
    path('registration/periods/programme/<int:pk>/modules/<int:module_pk>/add/assessment',views.learning_programme_registration_module_formative_add,name='learning_programme_registration_module_formative_add'),
    path('registration/periods/programme/<int:pk>/modules/<int:module_pk>/add/assessment/<int:assessment_pk>/edit',views.learning_programme_registration_module_formative_edit,name='learning_programme_registration_module_formative_edit'),
    path('registration/periods/programme/<int:pk>/modules/<int:module_pk>/add/assessment/<int:assessment_pk>/delete',views.learning_programme_registration_module_formative_delete,name='learning_programme_registration_module_formative_delete'),
    path('staff',views.StaffList.as_view(),name='staff_list'),
    path('staff/add',views.staff_add,name='staff_add'),
    path('staff/<int:pk>/edit',views.staff_edit,name='staff_edit'),
    path('staff/<int:pk>/delete',views.staff_delete,name='staff_delete'),
    path('staff/<int:pk>/role/add',views.add_staff_role,name='add_staff_role'),
    path('staff/<int:pk>/role/<int:role_pk>',views.remove_staff_role,name='remove_staff_role'),
    path('learning/programme/',views.LearningProgrammeList.as_view(),name='learning_programmes'),
    path('learning/programme/add',views.learning_programme_add,name='learning_programme_add'),
    path('learning/programme/<int:pk>/edit',views.learning_programme_edit,name='learning_programme_edit'),
    path('learning/programme/<int:pk>/deactivate',views.learning_programme_toggle,name='learning_programme_toggle'),
    path('learning/programme/<int:pk>/period/add',views.learning_programme_period_add,name='learning_programme_period_add'),
    path('learning/programme/<int:pk>/period/<int:period_pk>/edit',views.learning_programme_period_edit,name='learning_programme_period_edit'),
    path('learning/programme/<int:pk>/period/<int:period_pk>/delete',views.learning_programme_period_delete,name='learning_programme_period_delete'),
    
    path('learning/programme/period/<int:pk>/wil/requirements',views.LearningProgrammePeriodWilRequirementsList.as_view(),name='learning_programme_period_wil_requirements'),
    path('learning/programme/period/<int:pk>/wil/requirements/add',views.learning_programme_period_wil_requirement_add,name='learning_programme_period_wil_requirement_add'),
    path('learning/programme/period/<int:pk>/wil/requirements/<int:wil_pk>/edit',views.learning_programme_period_wil_requirement_edit,name='learning_programme_period_wil_requirement_edit'),
    path('learning/programme/period/<int:pk>/wil/requirements/<int:wil_pk>/delete',views.learning_programme_period_wil_requirement_delete,name='learning_programme_period_wil_requirement_delete'),
    
    path('learning/programme/period/<int:pk>/block/hours',views.LearningProgrammePeriodBlockRequirementsList.as_view(),name='learning_programme_period_block_requirements'),
    path('learning/programme/period/<int:pk>/block/hours/add',views.learning_programme_period_wil_block_add,name='learning_programme_period_wil_block_add'),
    path('learning/programme/period/<int:pk>/block/hours/<int:wil_pk>/edit',views.learning_programme_period_wil_block_edit,name='learning_programme_period_wil_block_edit'),
    path('learning/programme/period/<int:pk>/block/hours/<int:wil_pk>/delete',views.learning_programme_period_wil_block_delete,name='learning_programme_period_wil_block_delete'),
    
    path('learning/programme/period/<int:pk>/modules',views.LearningProgrammePeriodModuleList.as_view(),name='learning_programme_period_modules'),
    path('learning/programme/period/<int:pk>/modules/add',views.learning_programme_period_module_add,name='learning_programme_period_module_add'),
    path('learning/programme/period/<int:pk>/modules/<int:module_pk>/delete',views.learning_programme_period_module_delete,name='learning_programme_period_module_delete'),

    path('learning/programme/period/<int:pk>/sessions',views.LearningProgrammePeriodSessionList.as_view(),name='learning_programme_period_sessions'),
    path('learning/programme/period/<int:pk>/sessions/add',views.learning_programme_period_session_add,name='learning_programme_period_session_add'),
    path('learning/programme/period/<int:pk>/sessions/<int:session_pk>/edit',views.learning_programme_period_session_edit,name='learning_programme_period_session_edit'),
    path('learning/programme/period/<int:pk>/sessions/<int:session_pk>/delete',views.learning_programme_period_session_delete,name='learning_programme_period_session_delete'),
    
    
    path('learning/programme/period/<int:pk>/moderation/criteria/theory',views.LearningProgrammePeriodModeratorCriteriaReportList.as_view(),name='learning_programme_period_moderation_criteria'),
    path('learning/programme/period/<int:pk>/moderation/criteria/theory/add',views.learning_programme_period_moderator_criteria_report_add,name='learning_programme_period_moderator_criteria_report_add'),
    path('learning/programme/period/<int:pk>/moderation/criteria/theory/<int:criteria_pk>/edit',views.learning_programme_period_moderator_criteria_report_edit,name='learning_programme_period_moderator_criteria_report_edit'),
    path('learning/programme/period/<int:pk>/moderation/criteria/theory/<int:criteria_pk>/delete',views.learning_programme_period_moderator_criteria_report_delete,name='learning_programme_period_moderator_criteria_report_delete'),
    
    path('learning/programme/period/<int:pk>/moderation/criteria/wil',views.LearningProgrammePeriodModeratorCriteriaWILReportList.as_view(),name='learning_programme_period_moderation_criteria_wil'),
    path('learning/programme/period/<int:pk>/moderation/criteria/wil/add',views.learning_programme_period_moderator_criteria_wil_report_add,name='learning_programme_period_moderator_criteria_wil_report_add'),
    path('learning/programme/period/<int:pk>/moderation/criteria/wil/<int:criteria_pk>/edit',views.learning_programme_period_moderator_criteria_wil_report_edit,name='learning_programme_period_moderator_criteria_wil_report_edit'),
    path('learning/programme/period/<int:pk>/moderation/criteria/wil/<int:criteria_pk>/delete',views.learning_programme_period_moderator_criteria_wil_report_delete,name='learning_programme_period_moderator_criteria_wil_report_delete'),
    
    
    path('learning/programme/<int:pk>/documents',views.LearningProgrammeDocumentList.as_view(),name='learning_programme_documents'),
    path('learning/programme/<int:pk>/documents/add',views.learning_programme_document_add,name='learning_programme_document_add'),
    path('learning/programme/<int:pk>/documents/<int:doc_pk>/edit',views.learning_programme_document_edit,name='learning_programme_document_edit'),
    path('learning/programme/<int:pk>/documents/<int:doc_pk>/toggle',views.toggle_learning_programme_document,name='toggle_learning_programme_document'),
    path('learning/programme/<int:pk>/documents/<int:doc_pk>/delete',views.learning_programme_document_delete,name='learning_programme_document_delete'),
    path('learning/programme/<int:pk>/elos',views.LearningProgrammeELOList.as_view(),name='learning_programme_elos'),
    path('learning/programme/<int:pk>/elos/add',views.learning_programme_elo_add,name='learning_programme_elo_add'),
    path('learning/programme/<int:pk>/elos/<int:elo_pk>/edit',views.learning_programme_elo_edit,name='learning_programme_elo_edit'),
    path('learning/programme/<int:pk>/elos/<int:elo_pk>/delete',views.learning_programme_elo_delete,name='learning_programme_elo_delete'),
    path('learning/programme/<int:pk>/elos/<int:elo_pk>/assesment/criteria/add',views.learning_programme_elo_assessment_criteria_add,name='learning_programme_elo_assessment_criteria_add'),
    path('learning/programme/<int:pk>/elos/<int:elo_pk>/assesment/criteria/<int:assessment_pk>/edit',views.learning_programme_elo_assessment_criteria_edit,name='learning_programme_elo_assessment_criteria_edit'),
    path('learning/programme/<int:pk>/elos/<int:elo_pk>/assesment/criteria/<int:assessment_pk>/delete',views.learning_programme_elo_assessment_criteria_delete,name='learning_programme_elo_assessment_criteria_delete'),
    path('learning/programme/<int:pk>/competencies',views.LearningProgrammeCompetencyList.as_view(),name='learning_programme_competencies'),
    path('learning/programme/<int:pk>/competencies/add',views.learning_programme_competency_add,name='learning_programme_competency_add'),
    path('learning/programme/<int:pk>/competencies/<int:competency_pk>/edit',views.learning_programme_competency_edit,name='learning_programme_competency_edit'),
    path('learning/programme/<int:pk>/competencies/<int:competency_pk>/delete',views.learning_programme_competency_delete,name='learning_programme_competency_delete'),
    path('learning/programme/<int:pk>/competencies/<int:competency_pk>/breakdown',views.learning_programme_competency_breakdown_add,name='learning_programme_competency_breakdown_add'),
    path('learning/programme/<int:pk>/competencies/<int:competency_pk>/breakdown/<int:breakdown_pk>/edit',views.learning_programme_competency_breakdown_edit,name='learning_programme_competency_breakdown_edit'),
    path('learning/programme/<int:pk>/competencies/<int:competency_pk>/breakdown/<int:breakdown_pk>/delete',views.learning_programme_competency_breakdown_delete,name='learning_programme_competency_breakdown_delete'),
    path('learning/programme/<int:pk>/modules',views.LearningProgrammeModuleList.as_view(),name='learning_programme_modules'),
    path('learning/programme/<int:pk>/modules/add',views.learning_programme_module_add,name='learning_programme_module_add'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/edit',views.learning_programme_module_edit,name='learning_programme_module_edit'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/delete',views.learning_programme_module_delete,name='learning_programme_module_delete'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/prerequisite/add',views.learning_programme_module_prerequisite_add,name='learning_programme_module_prerequisite_add'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/prerequisite/<int:prerequisite_pk>/delete',views.learning_programme_module_prerequisite_delete,name='learning_programme_module_prerequisite_delete'),
    
    path('learning/programme/<int:pk>/modules/<int:module_pk>/assessment/add',views.learning_programme_module_formative_add,name='learning_programme_module_formative_add'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/assessment/<int:assessment_pk>/edit',views.learning_programme_module_formative_edit,name='learning_programme_module_formative_edit'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/assessment/<int:assessment_pk>/delete',views.learning_programme_module_formative_delete,name='learning_programme_module_formative_delete'),
    
    
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit',views.LearningProgrammeModuleStudyUnitList.as_view(),name='learning_programme_module_studyunits'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/add',views.learning_programme_module_studyunit_add,name='learning_programme_module_studyunit_add'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/<int:unit_pk>/edit',views.learning_programme_module_studyunit_edit,name='learning_programme_module_studyunit_edit'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/<int:unit_pk>/delete',views.learning_programme_module_studyunit_delete,name='learning_programme_module_studyunit_delete'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/<int:unit_pk>/section/add',views.learning_programme_module_studyunit_section_add,name='learning_programme_module_studyunit_section_add'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/<int:unit_pk>/section/<int:section_pk>/edit',views.learning_programme_module_studyunit_section_edit,name='learning_programme_module_studyunit_section_edit'),
    path('learning/programme/<int:pk>/modules/<int:module_pk>/study/unit/<int:unit_pk>/section/<int:section_pk>/delete',views.learning_programme_module_studyunit_section_delete,name='learning_programme_module_studyunit_section_delete'),
    path('learning/programme/<int:pk>/cohorts',views.LearningProgrammeCohortList.as_view(),name='learning_programme_cohorts'),
    path('learning/programme/<int:pk>/cohorts/add',views.learning_programme_cohort_add,name='learning_programme_cohort_add'),
    path('learning/programme/<int:pk>/cohorts/<int:cohort_pk>/edit',views.learning_programme_cohort_edit,name='learning_programme_cohort_edit'),
    path('learning/programme/<int:pk>/cohorts/<int:cohort_pk>/delete',views.learning_programme_cohort_delete,name='learning_programme_cohort_delete'),    
    
    path('learning/programme/cohorts/<int:pk>/registration/periods/',views.LearningProgrammeCohortRegistrationPeriodList.as_view(),name='learning_programme_cohort_registration_periods'),
    path('learning/programme/cohorts/<int:pk>/registration/period/add',views.learning_programme_cohort_registration_period_add,name='learning_programme_cohort_registration_period_add'),
    path('learning/programme/cohorts/<int:pk>/registration/period/<int:period_pk>/edit',views.learning_programme_cohort_registration_period_edit,name='learning_programme_cohort_registration_period_edit'),
    path('learning/programme/cohorts/<int:pk>/registration/period/<int:period_pk>/delete',views.learning_programme_cohort_registration_period_delete,name='learning_programme_cohort_registration_period_delete'),
    path('learning/programme/cohorts/<int:pk>/registration/period/<int:period_pk>/programme/coordinator',views.learning_programme_cohort_registration_period_programme_coordinator,name='learning_programme_cohort_registration_period_programme_coordinator'),


    path('learning/programme/cohorts/registration/periods/<int:pk>/procedures/compulsory',views.LearningProgrammeCohortRegistrationCompulsoryProceduresList.as_view(),name='learning_programme_cohort_registration_compulsory_procedures'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/compulsory/add',views.learning_programme_cohort_registration_compulsory_procedures_add,name='learning_programme_cohort_registration_compulsory_procedures_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/compulsory/<int:procedure_pk>/edit',views.learning_programme_cohort_registration_compulsory_procedures_edit,name='learning_programme_cohort_registration_compulsory_procedures_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/compulsory/<int:procedure_pk>/delete',views.learning_programme_cohort_registration_compulsory_procedures_delete,name='learning_programme_cohort_registration_compulsory_procedures_delete'),


    path('learning/programme/cohorts/registration/periods/<int:pk>/modules',views.LearningProgrammeCohortRegistrationModulesList.as_view(),name='learning_programme_cohort_registration_modules'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/add',views.learning_programme_cohort_registration_modules_add,name='learning_programme_cohort_registration_modules_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/<int:module_pk>/edit',views.learning_programme_cohort_registration_modules_edit,name='learning_programme_cohort_registration_modules_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/<int:module_pk>/delete',views.learning_programme_cohort_registration_modules_delete,name='learning_programme_cohort_registration_modules_delete'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/copy/assessments',views.copy_modules_assessments,name='copy_modules_assessments'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/<int:module_pk>/assessments/add',views.learning_programme_cohort_registration_module_formative_add,name='learning_programme_cohort_registration_module_formative_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/<int:module_pk>/assessments/<int:assessment_pk>/edit',views.learning_programme_cohort_registration_module_formative_edit,name='learning_programme_cohort_registration_module_formative_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/modules/<int:module_pk>/assessments/<int:assessment_pk>/delete',views.learning_programme_cohort_registration_module_formative_delete,name='learning_programme_cohort_registration_module_formative_delete'),
    
    path('learning/programme/cohorts/registration/periods/<int:pk>/modules/staff',views.LearningProgrammeCohortRegistrationModulesStaffList.as_view(),name='learning_programme_cohort_registration_modules_staff'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/modules/staff/assign',views.assign_module_staff,name='assign_module_staff'),
    
    path('learning/programme/cohorts/registration/periods/<int:pk>/modules/moderator',views.LearningProgrammeCohortRegistrationModulesModeratorList.as_view(),name='learning_programme_cohort_registration_modules_moderator'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/modules/moderator/assign',views.assign_module_moderator,name='assign_module_moderator'),
    
    path('learning/programme/cohorts/registration/periods/<int:pk>/module/<int:module_pk>/students',views.LearningProgrammeCohortRegistrationModuleStudentList.as_view(),name='learning_programme_cohort_registration_module_students'),
    path('learning/programme/cohorts/registration/periods/module/<int:pk>/moderation',views.learning_programme_cohort_module_moderators_report_view,name='learning_programme_cohort_module_moderators_report_view'),
    
    path('learning/programme/cohorts/registration/periods/module/student/<int:pk>/marks/edit',views.learning_programme_cohort_module_student_edit_final_mark,name='learning_programme_cohort_module_student_edit_final_mark'),
    
    path('learning/programme/cohorts/registration/periods/<int:pk>/procedures',views.LearningProgrammeCohortRegistrationProceduresList.as_view(),name='learning_programme_cohort_registration_procedures'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/add',views.learning_programme_cohort_registration_procedures_add,name='learning_programme_cohort_registration_procedures_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/<int:procedure_pk>/edit',views.learning_programme_cohort_registration_procedures_edit,name='learning_programme_cohort_registration_procedures_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/<int:procedure_pk>/delete',views.learning_programme_cohort_registration_procedures_delete,name='learning_programme_cohort_registration_procedures_delete'),
    path('learning/programme/cohorts/registration/period/<int:pk>/procedures/copy/assessments',views.copy_procedure_tasks_assessments,name='copy_procedure_tasks_assessments'),
    path('learning/programme/cohorts/registration/period/procedure/<int:pk>/assessments',views.LearningProgrammeCohortRegistrationProcedureAssessmentList.as_view(),name='procedure_tasks_assessments'),
    path('learning/programme/cohorts/registration/period/procedure/<int:pk>/assessments/add',views.registration_procedure_tasks_assessments_add,name='registration_procedure_tasks_assessments_add'),
    path('learning/programme/cohorts/registration/period/procedure/<int:pk>/assessments/<int:assessment_pk>/edit',views.registration_procedure_tasks_assessments_edit,name='registration_procedure_tasks_assessments_edit'),
    path('learning/programme/cohorts/registration/period/procedure/<int:pk>/assessments/<int:assessment_pk>/delete',views.registration_procedure_tasks_assessments_delete,name='registration_procedure_tasks_assessments_delete'),

    path('learning/programme/cohorts/registration/periods/<int:pk>/procedures/staff',views.LearningProgrammeCohortRegistrationProceduresStaffList.as_view(),name='learning_programme_cohort_registration_procedures_staff'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/procedures/staff/assign',views.assign_procedure_staff,name='assign_procedure_staff'),



    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures',views.LearningProgrammeCohortRegistrationProceduresSummativeList.as_view(),name='learning_programme_cohort_registration_procedures_summative'),
    path('learning/programme/cohorts/registration/period/<int:pk>/summative/procedures/add',views.learning_programme_cohort_registration_procedures_summative_add,name='learning_programme_cohort_registration_procedures_summative_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/summative/procedures/<int:procedure_pk>/edit',views.learning_programme_cohort_registration_procedures_summative_edit,name='learning_programme_cohort_registration_procedures_summative_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/summative/procedures/<int:procedure_pk>/delete',views.learning_programme_cohort_registration_procedures_summative_delete,name='learning_programme_cohort_registration_procedures_summative_delete'),
    path('learning/programme/cohorts/registration/period/<int:pk>/summative/procedures/copy/assessments',views.copy_procedure_summative_tasks_assessments,name='copy_procedure_summative_tasks_assessments'),

    path('learning/programme/cohorts/registration/period/summative/procedure/<int:pk>/assessments',views.LearningProgrammeCohortRegistrationProcedureSummativeAssessmentList.as_view(),name='procedure_summative_tasks_assessments'),
    path('learning/programme/cohorts/registration/period/summative/procedure/<int:pk>/assessments/add',views.registration_procedure_summative_tasks_assessments_add,name='registration_procedure_summative_tasks_assessments_add'),
    path('learning/programme/cohorts/registration/period/summative/procedure/<int:pk>/assessments/<int:assessment_pk>/edit',views.registration_procedure_summative_tasks_assessments_edit,name='registration_procedure_summative_tasks_assessments_edit'),
    path('learning/programme/cohorts/registration/period/summative/procedure/<int:pk>/assessments/<int:assessment_pk>/delete',views.registration_procedure_summative_tasks_assessments_delete,name='registration_procedure_summative_tasks_assessments_delete'),

    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures/staff',views.LearningProgrammeCohortRegistrationProceduresSummativeStaffList.as_view(),name='learning_programme_cohort_registration_procedures_summative_staff'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures/staff/assign',views.assign_procedure_summative_staff,name='assign_procedure_summative_staff'),

    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures/moderators',views.LearningProgrammeCohortRegistrationProceduresSummativeModeratorList.as_view(),name='learning_programme_cohort_registration_procedures_summative_moderators'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures/moderators/assign',views.assign_procedure_summative_moderators,name='assign_procedure_summative_moderators'),
    path('learning/programme/cohorts/registration/periods/<int:pk>/summative/procedures/moderators/<int:moderator_pk>/remove',views.delete_procedure_summative_moderators,name='delete_procedure_summative_moderators'),

    
    path('learning/programme/cohorts/registration/<int:pk>/education/plan',views.LearningProgrammeCohortPeriodEducationList.as_view(),name='learning_programme_cohort_education_plan'),
    #    path('learning/programme/cohorts/registration/<int:pk>/education/plan/copy/template',views.learning_programme_cohort_education_plan_copy_template,name='learning_programme_cohort_education_plan_copy_template'),
    
    path('learning/programme/cohorts/registration/<int:pk>/education/plan/add',views.learning_programme_cohort_education_plan_add,name='learning_programme_cohort_education_plan_add'),
    path('learning/programme/cohorts/registration/<int:pk>/education/plan/print',views.print_education_plan,name='print_education_plan'),

    path('learning/programme/<int:pk>/block/template/period/<int:period_pk>',views.LearningProgrammeBlockTemplateList.as_view(),name='lp_block_template'),
    path('learning/programme/<int:pk>/block/template/period/<int:period_pk>/add',views.learning_programme_block_template_add,name='learning_programme_block_template_add'),
    path('learning/programme/<int:pk>/block/template/period/<int:period_pk>/<int:block_pk>/edit',views.learning_programme_block_template_edit,name='learning_programme_block_template_edit'),
    path('learning/programme/<int:pk>/block/template/period/<int:period_pk>/<int:block_pk>/delete',views.learning_programme_block_template_delete,name='learning_programme_block_template_delete'),    
    
    path('education/year/plans/<int:pk>',views.EducationPlanYearList.as_view(),name='education_plans'),
    path('education/year/plans/<int:pk>/add',views.education_plan_add,name='education_plan_add'),
    path('education/year/plans/<int:pk>/edit',views.education_plan_edit,name='education_plan_edit'),
    path('education/year/plans/<int:pk>/delete',views.education_plan_delete,name='education_plan_delete'),
    
    path('education/year/plans/<int:pk>/section/add',views.education_plan_section_add,name='education_plan_section_add'),
    path('education/year/plans/section/<int:pk>/edit',views.education_plan_section_edit,name='education_plan_section_edit'),
    path('education/year/plans/section/<int:pk>/delete',views.education_plan_section_delete,name='education_plan_section_delete'),
    
    path('education/year/plans/<int:pk>/weeks/create',views.education_plan_weeks_create,name='education_plan_weeks_create'),
    path('education/year/plans/<int:pk>/section/<int:section_pk>/weeks',views.EducationPlanYearSectionWeeksList.as_view(),name='education_plan_section_weeks'),
    path('education/year/plans/<int:pk>/weeks',views.EducationPlanYearWeeksList.as_view(),name='education_plan_weeks'),
    path('education/year/plans/<int:pk>/weeks/copy/template',views.education_plan_year_copy_template,name='education_plan_year_copy_template'),
    path('education/year/plans/<int:pk>/weeks/<int:week_pk>/edit',views.education_plan_year_edit,name='education_plan_year_edit'),
    path('education/year/plans/<int:pk>/weeks/<int:week_pk>/delete',views.education_plan_year_delete,name='education_plan_year_delete'),

    path('education/year/plans/weeks/<int:pk>/days',views.view_education_plan_days,name='view_education_plan_days'),
    path('education/year/plans/weeks/<int:pk>/days/add/session',views.save_education_plan_day_session,name='save_education_plan_day_session'),
    path('education/year/plans/weeks/<int:pk>/days/delete/session/<int:session_pk>',views.delete_education_plan_day_session,name='delete_education_plan_day_session'),
    path('education/year/plans/weeks/<int:pk>/days/edit/session/<int:session_pk>',views.edit_education_plan_day_session,name='edit_education_plan_day_session'),
    path('education/year/plans/week/<int:pk>/print',views.print_education_plan_week,name='print_education_plan_week'),
    
    
    path('education/year/plans/<int:pk>/section/<int:section_pk>/wil/requirements',views.EducationPlanYearSectionWilRequirementsList.as_view(),name='education_plan_year_section_wil_requirements'),
    path('education/year/plans/<int:pk>/section/<int:section_pk>/wil/requirements/add',views.education_plan_year_section_wil_requirement_add,name='education_plan_year_section_wil_requirement_add'),
    path('education/year/plans/<int:pk>/section/<int:section_pk>/wil/requirements/<int:wil_pk>/edit',views.education_plan_year_section_wil_requirement_edit,name='education_plan_year_section_wil_requirement_edit'),
    path('education/year/plans/<int:pk>/section/<int:section_pk>/wil/requirements/<int:wil_pk>/delete',views.education_plan_year_section_wil_requirement_delete,name='education_plan_year_section_wil_requirement_delete'),
    

    path('learning/programme/cohorts/registration/periods/<int:pk>/attendance/registers',views.LearningProgrammeCohortRegistrationAttendanceRegisterList.as_view(),name='learning_programme_cohort_registration_attendance_registers'),
    path('learning/programme/cohorts/registration/period/<int:pk>/attendance/registers/add',views.learning_programme_cohort_registration_attendance_register_add,name='learning_programme_cohort_registration_attendance_register_add'),
    path('learning/programme/cohorts/registration/period/<int:pk>/attendance/registers/<int:register_pk>/edit',views.learning_programme_cohort_registration_attendance_register_edit,name='learning_programme_cohort_registration_attendance_register_edit'),
    path('learning/programme/cohorts/registration/period/<int:pk>/attendance/registers/<int:register_pk>/delete',views.learning_programme_cohort_registration_attendance_register_delete,name='learning_programme_cohort_registration_attendance_register_delete'),
    

    path('learning/programme/cohorts/registration/periods/attendance/register/<int:pk>/students',views.LearningProgrammeCohortRegistrationAttendanceRegisterStudentList.as_view(),name='learning_programme_cohort_registration_attendance_register_students'),
    path('learning/programme/cohorts/registration/period/attendance/registers/<int:pk>/students/add',views.learning_programme_cohort_registration_attendance_register_student_add,name='learning_programme_cohort_registration_attendance_register_student_add'),
    path('learning/programme/cohorts/registration/period/attendance/registers/<int:pk>/students/<int:student_pk>/delete',views.learning_programme_cohort_registration_attendance_register_student_delete,name='learning_programme_cohort_registration_attendance_register_student_delete'),
    


    path('ajax/facility/ward/fetch/disciplines',views.ajax_fetch_facility_ward_disciplines,name='ajax_fetch_facility_ward_disciplines'),
]
#lecturer paths

lecturerpatterns = [
    path('lecturer/learning/programme/<int:pk>/cohorts',views_lecturer.LecturerLearningProgrammeCohortList.as_view(),name='lecturer_learning_programme_cohorts'),
    path('lecturer/learning/programme/cohorts/<int:pk>/registration/periods/',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodList.as_view(),name='lecturer_learning_programme_cohort_registration_periods'),
    path('lecturer/education/year/plans/<int:pk>',views_lecturer.LecturerEducationPlanYearList.as_view(),name='lecturer_education_plans'),
    path('lecturer/education/year/plans/<int:pk>/weeks',views_lecturer.LecturerEducationPlanYearWeeksList.as_view(),name='lecturer_education_plan_weeks'),
    path('lecturer/learning/programme/<int:pk>/procedures/',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodProcedureList.as_view(),name='lecturer_procedure_list'),
    path('lecturer/learning/programme/<int:pk>/procedures/formative/assessors',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodProcedureStaffCoAssessorList.as_view(),name='lecturer_learning_programme_cohort_registration_procedures_formative_co_assessor'),
    path('lecturer/learning/programme/<int:pk>/procedures/formative/assessors/assign',views_lecturer.assign_procedure_formative_assessment_co_assessor,name='assign_procedure_formative_assessment_co_assessor'),
    path('lecturer/learning/programme/<int:pk>/procedures/summative',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeList.as_view(),name='lecturer_procedure_summative_list'),
    path('lecturer/learning/programme/<int:pk>/procedures/summative/assessors',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeStaffCoAssessorList.as_view(),name='lecturer_learning_programme_cohort_registration_procedures_summative_co_assessor'),
    path('lecturer/learning/programme/<int:pk>/procedures/summative/assessors/assign',views_lecturer.assign_procedure_summative_assessment_co_assessor,name='assign_procedure_summative_assessment_co_assessor'),
    
    
    path('lecturer/learning/programme/<int:pk>/formative/modules/',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodModuleList.as_view(),name='lecturer_module_list'),
    path('lecturer/learning/programme/<int:pk>/summative/modules/',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodSummativeModuleList.as_view(),name='lecturer_summative_module_list'),

    path('ajax/learning/programme/period/study/units',views.ajax_fetch_study_units,name='ajax_fetch_study_units'),

    path('lecturer/learning/programme/<int:pk>/modules/all',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodALLModulesList.as_view(),name='lecturer_view_all_modules_list'),
    path('lecturer/learning/programme/modules/<int:pk>/register',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodModuleRegistersList.as_view(),name='lecturer_module_rosters'),
    path('lecturer/learning/programme/modules/<int:pk>/register/add',views_lecturer.cohort_registration_module_register_add,name='cohort_registration_module_register_add'),
    path('lecturer/learning/programme/modules/<int:pk>/register/<int:roster_pk>/edit',views_lecturer.cohort_registration_module_register_edit,name='cohort_registration_module_register_edit'),
    path('lecturer/learning/programme/modules/<int:pk>/register/<int:roster_pk>/delete',views_lecturer.cohort_registration_module_register_delete,name='cohort_registration_module_register_delete'),

    path('lecturer/learning/programme/modules/register/<int:pk>/students',views_lecturer.LecturerLearningProgrammeCohortRegistrationPeriodModuleRegisterStudentsList.as_view(),name='lecturer_module_register_students'),
    path('lecturer/learning/programme/modules/register/<int:pk>/students/bulk/approve',views_lecturer.cohort_registration_module_register_student_bulk_approve,name='cohort_registration_module_register_student_bulk_approve'),
]

coassessorpatterns = [
    path('coassessor/learning/programme/<int:pk>/cohorts',views_co_assessor.CoAssessorLearningProgrammeCohortList.as_view(),name='co_assessor_learning_programme_cohorts'),
    path('coassessor/learning/programme/cohorts/<int:pk>/registration/periods/',views_co_assessor.CoAssessorLearningProgrammeCohortRegistrationPeriodList.as_view(),name='co_assessor_learning_programme_cohort_registration_periods'),
    path('coassessor/learning/programme/<int:pk>/procedures/',views_co_assessor.CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureList.as_view(),name='co_assessor_procedure_list'),
    path('coassessor/learning/programme/<int:pk>/procedures/summative',views_co_assessor.CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList.as_view(),name='co_assessor_procedure_summative_list'),
]

facilityhodpatterns = [
    path('healthcare/facility/hod/dashboard',facility_hod_dashboard,name='facility_hod_dashboard'),
    path('healthcare/coassessor/dashboard',co_assessor_dashboard,name='co_assessor_dashboard'),
]

moderatorpatterns = [
    path('moderator/dashboard',moderator_dashboard,name='moderator_dashboard'),    
    path('moderator/learning/programme/cohorts/<int:pk>/registration/periods/',ModeratorLearningProgrammeCohortRegistrationPeriodList.as_view(),name='moderator_learning_programme_cohort_registration_periods'),
    path('moderator/learning/programme/<int:pk>/procedures/summative',ModeratorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList.as_view(),name='moderator_procedure_summative_list'),
    path('moderator/learning/programme/<int:pk>/summative/modules/',ModeratorLearningProgrammeCohortRegistrationPeriodModuleList.as_view(),name='moderator_summative_module_list'),
    path('moderator/learning/programme/cohort/registration/<int:pk>/module/<int:module_pk>/summative/assessor/students',ModeratorLearningProgrammeCohortRegistrationPeriodModuleStudentList.as_view(),name='moderator_summative_module_list_students'),   
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report',moderator_learning_programme_cohort_module_moderators_report,name='moderator_learning_programme_cohort_module_moderators_report'),     
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report/<int:report_pk>/answer/<assessment_pk>/save',moderator_learning_programme_cohort_module_moderators_report_answer,name='moderator_learning_programme_cohort_module_moderators_report_answer'), 
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report/<int:report_pk>/comment/<assessment_pk>/save',moderator_learning_programme_cohort_module_moderators_report_comment,name='moderator_learning_programme_cohort_module_moderators_report_comment'), 
    
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report/<int:report_pk>/comments/save',moderator_learning_programme_cohort_module_moderators_report_moderators_final_comment,name='moderator_learning_programme_cohort_module_moderators_report_moderators_final_comment'), 
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report/<int:report_pk>/feedback/save',moderator_learning_programme_cohort_module_moderators_report_moderators_feedback,name='moderator_learning_programme_cohort_module_moderators_report_moderators_feedback'),     
    path('moderator/learning/programme/cohort/registration/module/<int:pk>/moderation/report/<int:report_pk>/recommendations/save',moderator_learning_programme_cohort_module_moderators_report_recommendations,name='moderator_learning_programme_cohort_module_moderators_report_recommendations'), 
    
     
]

urlpatterns = urlpatterns + lecturerpatterns + facilityhodpatterns + coassessorpatterns + moderatorpatterns