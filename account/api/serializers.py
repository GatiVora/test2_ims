from rest_framework import serializers
from account.models import User

class UserSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('email','first_name','last_name','role','password','password2')
        extra_kwargs = {
            'password': {'write_only': True}, #to hide password field
        }

    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data
    
    def create(self,validated_data):
        validated_data.pop("password2")
        password = validated_data.get('password')
        user = User.objects.create_user(**validated_data)
        return user

    # def save(self):
    #     user = User(
    #         email=self.validated_data['email'],
    #         first_name=self.validated_data['first_name'],
    #         last_name=self.validated_data['last_name'],
    #         role=self.validated_data['role'],                
    #     )
    #     password = self.validated_data['password']
    #     password2 = self.validated_data['password2']
    #     if password != password2:
    #         raise serializers.ValidationError({'password': 'Passwords must match.'})
    #     user.set_password(password)
    #     user.save()
    #     return user
        

