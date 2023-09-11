from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile


# created is true if user is created else false
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        # print('create the user profile')
        UserProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
            print('user is updated')
        except:
            # create user profile if not exists
            UserProfile.objects.create(user=instance)
            print('User profile was not there, so created it')

#pre_save does not take created signal
@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(instance.username, "user is being saved")
# post_save.connect(post_save_create_profile_receiver, sender=User) #one way to connect sender to receiver or using decorator