from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta,datetime
from django.utils import timezone
# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=10,null=True,blank=True)
    otp_created_at=models.DateTimeField(null=True,blank=True)


    def is_otp_expired(self):
        if not self.otp_created_at:
            return True
        expired_time=self.otp_created_at+timedelta(minutes=5)
        return timezone.now() > expired_time