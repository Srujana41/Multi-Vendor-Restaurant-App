from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import sendNotificationEmail

# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license') 
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.vendor_name
    
    # args and kwargs should be used when you don't know what arguments a function takes
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update
            originalValue = Vendor.objects.get(pk=self.pk)
            if originalValue.is_approved != self.is_approved:
                email_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    mail_subject = "Congratulation! Your restaurant is approved."
                    sendNotificationEmail(mail_subject, email_template, context)
                else:
                    mail_subject= "We are sorry!"
                    sendNotificationEmail(mail_subject, email_template, context)
        return super(Vendor, self).save(*args, **kwargs);