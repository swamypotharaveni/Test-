from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta,datetime
from django.utils import timezone
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=10,null=True,blank=True)
    otp_created_at=models.DateTimeField(null=True,blank=True)
    last_otp_request_date = models.DateField(null=True, blank=True)
    otp_request_count = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    OTP_EXPIRY_MINUTES = 5
    OTP_DAILY_LIMIT = 5
    def is_otp_expired(self):
        if not self.otp_created_at:
            return True
        expired_time=self.otp_created_at+timedelta(minutes=5)
        return timezone.now() > expired_time
    def otp_expiry_remaining(self):
        if self.otp_created_at is None:
            return 0
        remaining = (self.otp_created_at + timedelta(minutes=5)) - datetime.now()
        return max(int(remaining.total_seconds() / 60), 0)
    def increment_otp_count(self):
        self.otp_request_count +=1
        self.last_otp_request_date=timezone.now().date()
        self.save()
    def can_request_otp(self):
        today=timezone.now().date()
        if self.last_otp_request_date != today:
             self.otp_request_count = 0
             self.last_otp_request_date = today
             self.save()
        return self.otp_request_count < self.OTP_DAILY_LIMIT
