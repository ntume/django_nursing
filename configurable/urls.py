from django.urls import path
from . import views

app_name = 'configurable'

urlpatterns = [
    path('ajax/fetch/municiaplities',views.ajax_fetch_municipalities,name='ajax_fetch_municipalities'),
    path('ajax/fetch/cities',views.ajax_fetch_cities,name='ajax_fetch_cities'), 
    path('ajax/fetch/suburbs',views.ajax_fetch_surburbs,name='ajax_fetch_surburbs'),   
    path('ajax/verify/area',views.ajax_verify_area,name='ajax_verify_area'),   
    path('populate/district',views.populate_municipality,name='populate_municipality'),
    path('ajax/fetch/areas',views.ajax_fetech_areas,name='ajax_fetech_areas'),
    path('config/race/',views.RaceList.as_view(),name='races'),
    path('config/race/add',views.add_race,name='add_race'),
    path('config/race/<int:pk>/edit',views.edit_race,name='edit_race'),
    path('config/race/<int:pk>/delete',views.delete_race,name='delete_race'),
    path('config/economic/status/',views.EconomicStatusList.as_view(),name='economic_status'),
    path('config/economic/status/add',views.add_economic_status,name='add_economic_status'),
    path('config/economic/status/<int:pk>/edit',views.edit_economic_status,name='edit_economic_status'),
    path('config/economic/status/<int:pk>/delete',views.delete_economic_status,name='delete_economic_status'),
    path('config/economic/status/etqa/',views.EmploymentEconomicStatusList.as_view(),name='employment_economic_status'),
    path('config/economic/status/etqa/add',views.add_employment_economic_status,name='add_employment_economic_status'),
    path('config/economic/status/etqa/<int:pk>/edit',views.edit_employment_economic_status,name='edit_employment_economic_status'),
    path('config/economic/status/etqa/<int:pk>/delete',views.delete_employment_economic_status,name='delete_employment_economic_status'),
    path('config/gender/',views.GenderList.as_view(),name='gender'),
    path('config/gender/add',views.add_gender,name='add_gender'),
    path('config/gender/<int:pk>/edit',views.edit_gender,name='edit_gender'),
    path('config/gender/<int:pk>/delete',views.delete_gender,name='delete_gender'),
    
    path('config/language/',views.LanguageList.as_view(),name='languages'),
    path('config/language/add',views.add_language,name='add_language'),
    path('config/language/<int:pk>/edit',views.edit_race,name='edit_language'),
    path('config/language/<int:pk>/delete',views.delete_language,name='delete_language'),
    path('config/residential/status/',views.ResidentialStatusList.as_view(),name='residential_status'),
    path('config/residential/status/add',views.add_residential_status,name='add_residential_status'),
    path('config/residential/status/<int:pk>/edit',views.edit_residential_status,name='edit_residential_status'),
    path('config/residential/status/<int:pk>/delete',views.delete_residential_status,name='delete_residential_status'),
    path('config/disabilities/',views.DisabilityList.as_view(),name='disabilities'),
    path('config/disabilities/add',views.add_disability,name='add_disability'),
    path('config/disabilities/<int:pk>/edit',views.edit_disability,name='edit_disability'),
    path('config/disabilities/<int:pk>/delete',views.delete_disability,name='delete_disability'),
    
    path('config/question/types/',views.QuestionTypeList.as_view(),name='question_types'),
    path('config/question/types/add',views.add_question_types,name='add_question_types'),
    path('config/question/types/<int:pk>/edit',views.edit_question_type,name='edit_question_type'),
    path('config/question/types/<int:pk>/delete',views.delete_question_type,name='delete_question_type'),
    path('config/question/types/<int:pk>/add/option',views.question_type_add_option,name='question_type_add_option'),
    path('config/question/types/delete/option/<int:pk>',views.question_types_delete_option,name='question_types_delete_option'),
    
    path('config/countries/',views.CountryListView.as_view(),name='countries'),
    path('config/countries/add',views.add_country,name='add_country'),
    path('config/countries/<int:pk>/edit',views.edit_country,name='edit_country'),
    path('config/countries/<int:pk>/delete',views.delete_country,name='delete_country'),

    path('config/<int:pk>/provinces',views.ProvinceListView.as_view(),name='provinces'),
    path('config/<int:country_pk>/provinces/add',views.add_province,name='add_province'),
    path('config/provinces/<int:pk>/edit',views.edit_province,name='edit_province'),
    path('config/provinces/<int:pk>/delete',views.delete_province,name='delete_province'),

    path('config/<int:pk>/municipalities',views.MunicipalityListView.as_view(),name='municipalities'),
    path('config/<int:province_pk>/municipalities/add',views.add_municipality,name='add_municipality'),
    path('config/municipalities/<int:pk>/edit',views.edit_municipality,name='edit_municipality'),
    path('config/municipalities/<int:pk>/delete',views.delete_municipality,name='delete_municipality'),

    path('config/<int:pk>/districts',views.DistrictListView.as_view(),name='districts'),
    path('config/<int:municipality_pk>/districts/add',views.add_district,name='add_district'),
    path('config/districts/<int:pk>/edit',views.edit_district,name='edit_district'),
    path('config/districts/<int:pk>/delete',views.delete_district,name='delete_district'),

    path('config/<int:pk>/cities',views.CityList.as_view(),name='cities'),
    path('config/<int:district_pk>/cities/add',views.add_city,name='add_city'),
    path('config/cities/<int:pk>/edit',views.edit_city,name='edit_city'),
    path('config/cities/<int:pk>/delete',views.delete_city,name='delete_city'),

    path('config/<int:pk>/suburbs',views.SuburbList.as_view(),name='suburbs'),
    path('config/<int:city_pk>/suburbs/add',views.add_suburb,name='add_suburb'),
    path('config/suburbs/<int:pk>/edit',views.edit_suburb,name='edit_suburb'),
    path('config/suburbs/<int:pk>/delete',views.delete_suburb,name='delete_suburb'),

    path('config/type/of/ids',views.TypeOfIDListView.as_view(),name='type_of_ids'),
    path('config/type/of/ids/add',views.add_type_of_id,name='add_type_of_id'),
    path('config/type/of/ids/<int:pk>/edit',views.edit_type_of_id,name='edit_type_of_id'),
    path('config/type/of/ids/<int:pk>/delete',views.delete_type_of_id,name='delete_type_of_id'),


    path('config/structure/status/ids',views.StructureStatusIDListView.as_view(),name='stucture_status_ids'),
    path('config/structure/status/add',views.add_structure_status_id,name='add_structure_status_id'),
    path('config/structure/status/<int:pk>/edit',views.edit_structure_status_id,name='edit_structure_status_id'),
    path('config/structure/status/<int:pk>/delete',views.delete_structure_status_id,name='delete_structure_status_id'),

    path('config/nationalities',views.NationalityListView.as_view(),name='nationalities'),
    path('config/nationalities/add',views.add_nationality,name='add_nationality'),
    path('config/nationalities/<int:pk>/edit',views.edit_nationality,name='edit_nationality'),
    path('config/nationalities/<int:pk>/delete',views.delete_nationality,name='delete_nationality'),
    
    path('config/leave',views.LeaveList.as_view(),name='type_of_leave'),
    path('config/leave/add',views.type_of_leave_add,name='type_of_leave_add'),
    path('config/leave/<int:pk>/edit',views.type_of_leave_edit,name='type_of_leave_edit'),
    path('config/leave/<int:pk>/delete',views.type_of_leave_delete,name='type_of_leave_delete'),

    path('config/indemnity',views.IndemnityList.as_view(),name='indemnity_list'),
    path('config/indemnity/add',views.indemnity_add,name='indemnity_add'),
    path('config/indemnity/<int:pk>/edit',views.indemnity_edit,name='indemnity_edit'),
    path('config/indemnity/<int:pk>/delete',views.indemnity_delete,name='indemnity_delete'),

    path('config/sponsorship',views.SponsorshipList.as_view(),name='sponsorship_list'),
    path('config/sponsorship/add',views.sponsorship_add,name='sponsorship_add'),
    path('config/sponsorship/<int:pk>/edit',views.sponsorship_edit,name='sponsorship_edit'),
    path('config/sponsorship/<int:pk>/delete',views.sponsorship_delete,name='sponsorship_delete'),
    
    path('config/programme/blocks',views.BlockList.as_view(),name='block_list'),
    path('config/programme/blocks/add',views.block_add,name='block_add'),
    path('config/programme/blocks/<int:pk>/edit',views.block_edit,name='block_edit'),
    path('config/programme/blocks/<int:pk>/delete',views.block_delete,name='block_delete'),

    path('config/demonstrations',views.DemonstrationList.as_view(),name='demonstration_list'),
    path('config/demonstrations/add',views.demonstration_add,name='demonstration_add'),
    path('config/demonstrations/<int:pk>/edit',views.demonstration_edit,name='demonstration_edit'),
    path('config/demonstrations/<int:pk>/delete',views.demonstration_delete,name='demonstration_delete'),

    path('config/disciplines',views.DisciplineList.as_view(),name='discipline_list'),
    path('config/disciplines/add',views.discipline_add,name='discipline_add'),
    path('config/disciplines/<int:pk>/edit',views.discipline_edit,name='discipline_edit'),
    path('config/disciplines/<int:pk>/delete',views.discipline_delete,name='discipline_delete'),
    path('config/disciplines/<int:pk>/add/ward',views.discipline_ward_add,name='discipline_ward_add'),
    path('config/disciplines/<int:pk>/ward/<int:ward_pk>/remove',views.discipline_ward_remove,name='discipline_ward_remove'),
    
    path('config/wards/',views.WardList.as_view(),name='ward_list'),
    path('config/wards/add',views.ward_add,name='ward_add'),
    path('config/wards/<int:pk>/edit',views.ward_edit,name='ward_edit'),
    path('config/wards/<int:pk>/delete',views.ward_delete,name='ward_delete'),

    path('config/clinical/procedures',views.ClinicalProcedureThemeList.as_view(),name='clinical_procedure_list'),
    path('config/clinical/procedures/add',views.clinical_procedure_add,name='clinical_procedure_add'),
    path('config/clinical/procedures/<int:pk>/edit',views.clinical_procedure_edit,name='clinical_procedure_edit'),
    path('config/clinical/procedures/<int:pk>/delete',views.clinical_procedure_delete,name='clinical_procedure_delete'),
    path('config/clinical/procedures/<int:pk>/add/task',views.clinical_procedure_task_add,name='clinical_procedure_task_add'),
    path('config/clinical/procedures/tasks/<int:pk>/edit',views.clinical_procedure_task_edit,name='clinical_procedure_task_edit'),
    path('config/clinical/procedures/tasks/<int:pk>/delete',views.clinical_procedure_task_delete,name='clinical_procedure_task_delete'),

    path('config/clinical/procedures/task/<int:pk>',views.ClinicalProcedureThemeTaskAssessmentList.as_view(),name='clinical_procedure_assessment_list'),
    path('config/clinical/procedures/task/<int:pk>/add',views.clinical_procedure_task_assessment_add,name='clinical_procedure_task_assessment_add'),
    path('config/clinical/procedures/task/<int:pk>/copy',views.clinical_procedure_task_assessment_copy,name='clinical_procedure_task_assessment_copy'),   
    
    path('config/clinical/procedures/task/<int:pk>/assessment/<int:assessment_pk>/edit',views.clinical_procedure_assessment_edit,name='clinical_procedure_assessment_edit'),
    path('config/clinical/procedures/task/<int:pk>/assessment/<int:assessment_pk>/delete',views.clinical_procedure_assessment_delete,name='clinical_procedure_assessment_delete'),

    path('config/clinical/procedures/task/<int:pk>/assessment/bulk/upload',views.clinical_procedure_assessment_bulk_upload,name='clinical_procedure_assessment_bulk_upload'),
    path('config/clinical/procedures/task/<int:pk>/assessment/bulk/upload/excel',views.clinical_procedure_assessment_bulk_upload_excel,name='clinical_procedure_assessment_bulk_upload_excel'),
    

    path('config/shifts',views.ShiftList.as_view(),name='shift_list'),
    path('config/shifts/add',views.shift_add,name='shift_add'),
    path('config/shifts/<int:pk>/edit',views.shift_edit,name='shift_edit'),
    path('config/shifts/<int:pk>/delete',views.shift_delete,name='shift_delete'),
    
    path('config/wil/scale/questions/',views.WILScaleQuestionList.as_view(),name='wil_scale_list'),
    path('config/wil/scale/questions/add',views.wil_scale_add,name='wil_scale_add'),
    path('config/wil/scale/questions/<int:pk>/edit',views.wil_scale_edit,name='wil_scale_edit'),
    path('config/wil/scale/questions/<int:pk>/delete',views.wil_scale_delete,name='wil_scale_delete'),
    
    path('config/registration/blocks',views.RegistrationBlockList.as_view(),name='registration_block_list'),
    path('config/registration/blocks/add',views.registration_block_add,name='registration_block_add'),
    path('config/registration/blocks/<int:pk>/edit',views.registration_block_edit,name='registration_block_edit'),
    path('config/registration/blocks/<int:pk>/delete',views.registration_block_delete,name='registration_block_delete'),

    path('config/register/categories',views.RegisterCategoryList.as_view(),name='register_category_list'),
    path('config/register/categories/add',views.register_category_add,name='register_category_add'),
    path('config/register/categories/<int:pk>/edit',views.register_category_edit,name='register_category_edit'),
    path('config/register/categories/<int:pk>/delete',views.register_category_delete,name='register_category_delete'),

    path('config/dose',views.DoseList.as_view(),name='doses'),
    path('config/dose/add',views.add_dose,name='add_dose'),
    path('config/dose/<int:pk>/edit',views.edit_dose,name='edit_dose'),
    path('config/dose/<int:pk>/delete',views.delete_dose,name='delete_dose'),
    
    
    path('ajax/config/wards',views.ajax_fetch_discipline_wards,name='ajax_fetch_discipline_wards'),
]
