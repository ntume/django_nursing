from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers



class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user object login token"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type':'password'},
        trim_whitespace = False
    )

    def validate(self,attrs):
        """validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        role = attrs.get('role')

        user = authenticate(
            request  = self.context.get('request'),
            username = email,
            password = password
        )

        if not user:
            msg = _("unable to authenticate user")
            raise serializers.ValidationError(msg,code='authentication')

        attrs['user'] = user
        attrs['role'] = role
        return attrs


class UserSerializer(serializers.ModelSerializer):
    '''
    serializer for the user object
    '''

    class Meta:
        model = get_user_model()
        fields = ['email','password','first_name','last_name']
        extra_kwargs = {'password':{'write_only':True,'min_length':5}}

    def create(self,validate_data):
        '''
        Create and return a user with encrypted password
        '''

        user = get_user_model().objects.create_user(**validate_data)
       
        return user
    
    def update(self,instance,validated_data):
        '''update and return user'''
        password = validated_data.pop('password',None)
        user = super().update(instance,validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
