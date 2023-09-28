from vendor.models import Vendor

# to make this data accessible from all of the HTML pages, we use context processors.
# the definition of the context processor is it is a function that takes only one argument that is request.
# and returns a dictionary that gets added to the request context.
# to add this dictionary, inside the request context, you need to simply go
# to the settings.py and inside the template section, go to context processors, here you need to register the new function that you created.
# on logout vendor becomes None and there is no user
def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)