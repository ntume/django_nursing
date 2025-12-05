from datetime import date
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class UserFunction(models.Model):
    '''
    Table of functions
    '''

    function = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Role(models.Model):
    '''
    The Role entries are managed by the system,
    automatically created via a Django data migration.
    '''

    role = models.CharField(max_length=60)
    functions = models.ManyToManyField(UserFunction)
    internal = models.CharField(max_length=3)
    description = models.CharField(max_length=256)
    active = models.CharField(max_length=3,default='No')

    def __str__(self):
        return self.role

    def fetch_staff(self):
        '''
        Fecth specific staff members
        '''
        role = Role.objects.get(id = self.id) 
        return role.user_set.all()
    
    def fetch_active_announcements(self):
        '''
        Fetch all active announcements        
        '''
        role = Role.objects.get(id = self.id) 
        return role.announcements.filter(published = 'Yes')
    
    
  

class User(AbstractUser):
  roles = models.ManyToManyField(Role)
  username = None
  email = models.EmailField(_('email address'), unique=True)
  logged_in_role = models.ForeignKey(Role,null=True,on_delete=models.SET_NULL,related_name='logged_in_roles')
  password_change_date = models.DateField(default=date.today())

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  objects = UserManager()

class LoginHistory(models.Model):
    '''
    Table to record all logins
    '''

    choices_medium = (('Mobile','Mobile'),('Web','Web'))

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='logins')
    medium = models.CharField(max_length=6,choices=choices_medium,default='Web')
    created_at = models.DateTimeField(auto_now_add=True)

class EmailTemplates(models.Model):
    '''
    table for email templates
    '''

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='email_templates')
    subject = models.CharField(max_length=256)
    email = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserForgetPasswordToken(models.Model):
    '''
    table for forget password token
    '''

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='forgot_password_tokens')
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    done = models.CharField(max_length=3,default='No')

class UserEmail(models.Model):
    '''
    user email table
    '''
    recipient = models.ForeignKey(User,on_delete=models.CASCADE,related_name='recipient_emails')
    recipient_role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='recipient_emails')    
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender_emails')
    sender_role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='sender_emails')
    title = models.CharField(max_length = 255)
    email_body = models.TextField()
    read = models.CharField(max_length=3,default='No')
    created_at = models.DateTimeField(auto_now_add=True)



