from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from public.models import *

@dajaxice_register
def test_username(request,username):
    cnt = UserBasic.objects.filter(username__exact=username).count()
    if cnt == 0:
        no_clash = True
    else:
        no_clash = False
    print no_clash
    return simplejson.dumps({'no_clash': no_clash,
                             })
