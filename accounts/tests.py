from datetime import datetime,timedelta
class Profile():
    def __init__(self,opt_created_at=None):
        self.opt_created_at=opt_created_at
    def otp_expiry_remaining(self):
        print(self.opt_created_at)
        if self.opt_created_at is None:
            return 0
        remaining= (self.opt_created_at+timedelta(minutes=5))-datetime.now()
        return  max(int(remaining.total_seconds() / 60), 0)

profile1=Profile(datetime.now())
print("OTP just created:", profile1.otp_expiry_remaining(), "minutes remaining")
profile2=Profile(datetime.now()-timedelta(minutes=3))
print("OTP just created:", profile2.otp_expiry_remaining(), "minutes remaining")