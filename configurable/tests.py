from django.test import TestCase
from .models import *
from .forms import *

# Create your tests here.

class ProvinceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(country="South Africa",country_code="27",id=1)
        cls.province = Province.objects.create(country = cls.country,province='Mpumalanga')
        
    def test_province_creation(self):
        self.assertEqual(f"{self.province.province}","Mpumalanga")
        self.assertEqual(self.country,self.province.country)

    def test_province_valid_form(self):
        data = {'province':self.province.province}
        form = ProvinceForm(data=data)
        self.assertTrue(form.is_valid())

    def test_province_invalid_form(self):
        data = {'province':''}
        form = ProvinceForm(data=data)
        self.assertFalse(form.is_valid())


class MunicipalityTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(country="South Africa",country_code="27",id=1)
        cls.province = Province.objects.create(country = cls.country,province='Mpumalanga')
        cls.municipality = Municipality.objects.create(province=cls.province,municipality="Emalahleni")

    def test_municipality_creation(self):
        self.assertEqual(f"{self.municipality.municipality}","Emalahleni")
        self.assertEqual(self.municipality.province,self.province)

    def test_municipality_valid_form(self):
        data = {'municipality':self.municipality.municipality}
        form = MunicipalityForm(data=data)
        self.assertTrue(form.is_valid())

    def test_municipality_invalid_form(self):
        data = {"municipality":""}
        form = MunicipalityForm(data=data)
        self.assertFalse(form.is_valid())


class CityTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(country="South Africa",country_code="27",id=1)
        cls.province = Province.objects.create(country = cls.country,province='Mpumalanga')
        cls.municipality = Municipality.objects.create(province=cls.province,municipality="Emalahleni")
        cls.city = City.objects.create(municipality=cls.municipality,city="Rietspruit")

    def test_city_creation(self):
        self.assertEqual(f"{self.city.city}","Rietspruit")
        self.assertEqual(self.municipality,self.city.municipality)

    def test_city_valid_form(self):
        data = {'city':"Rietspruit"}
        form = CityForm(data=data)
        self.assertTrue(form.is_valid())

    def test_city_invalid_form(self):
        data = {'city':''}
        form = CityForm(data=data)
        self.assertFalse(form.is_valid())


class LanguageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.language = Language.objects.create(language = "English",id=2)

    def test_language_creation(self):
        self.assertEqual(f"{self.language.language}","English")

    def test_language_form_valid(self):
        data = {"language":'English'}
        form = LanguageForm(data=data)
        self.assertTrue(form.is_valid())

    def test_language_form_invalid(self):
        data = {'language':''}
        form = LanguageForm(data=data)
        self.assertFalse(form.is_valid())


class BankTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.bank = Bank.objects.create(bank = "ABSA")

    def test_bank_creation(self):
        self.assertEqual(f"{self.bank.bank}","ABSA")

    def test_bank_form_valid(self):
        data = {'bank':'ABSA'}
        form = BankForm(data=data)
        self.assertTrue(form.is_valid())

    def test_bank_form_invalid(self):
        data = {'bank':''}
        form = BankForm(data=data)
        self.assertFalse(form.is_valid())

    
class BankAccountTypeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.account_type = BankAccountType.objects.create(type = "Cheque")

    def test_bank_account_type_creation(self):
        self.assertEqual(f"{self.account_type.type}","Cheque")

    def test_bank_account_type_form_valid(self):
        data = {'type':'Savings'}
        form = BankAccountTypeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_bank_account_type_form_invalid(self):
        data = {'type':''}
        form = BankAccountTypeForm(data=data)
        self.assertFalse(form.is_valid())


class GenderTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.gender = Gender.objects.create(gender='Female')

    def test_gender_creation(self):
        self.assertEqual(f"{self.gender.gender}","Female")

    def test_gender_form_valid(self):
        data = {'gender':'Female'}
        form = GenderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_gender_form_invalid(self):
        data = {'gender':''}
        form = GenderForm(data=data)
        self.assertFalse(form.is_valid())
        
        

class RaceTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.race = Race.objects.create(race='African')

    def test_race_creation(self):
        self.assertEqual(f"{self.race.race}","African")

    def test_race_form_valid(self):
        data = {'race':'African'}
        form = RaceForm(data=data)
        self.assertTrue(form.is_valid())

    def test_race_form_invalid(self):
        data = {'race':''}
        form = RaceForm(data=data)
        self.assertFalse(form.is_valid())
        
        
class EconomicStatusTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.status = EconomicStatus.objects.create(status='Employed')

    def test_status_creation(self):
        self.assertEqual(f"{self.status.status}","Employed")

    def test_status_form_valid(self):
        data = {'status':'Employed'}
        form = EconomicStatusForm(data=data)
        self.assertTrue(form.is_valid())

    def test_status_form_invalid(self):
        data = {'status':''}
        form = EconomicStatusForm(data=data)
        self.assertFalse(form.is_valid())





    