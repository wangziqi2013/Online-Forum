# This is the public view file, which defines the public part of the site

from public.models import * # Data models
# Use to redirect the broser
from django.http import HttpResponseRedirect, HttpResponse
# Used to get a URL from the view method path (as well as argument)
from django.core.urlresolvers import reverse
# Used in CSRF token authentication
from django.template import RequestContext
# Used to render the template; Used to retrieve an object from the model
from django.shortcuts import render_to_response, get_object_or_404
# Used to check password
from django.contrib.auth.hashers import check_password, make_password
# Used to test whether an entry exist in the database, objects.get() will raise
from django.core.exceptions import *
# Raise this exception when it is needed
from django.http import Http404
from datetime import *

###########################
# Debug ###################
###########################

def debug_output(obj):
    return HttpResponse(str(obj),content_type='text/html')

###########################
# User Manipulation #######
###########################

def user_not_login_error_page():
    header_text = 'You have not logged in!'
    tip_text = 'Please login first'

    return user_tip_page(header_text=header_text,tip_text=tip_text,
                        jump_to_login=True)

def user_not_authentic_error_page():
    header_text = 'You did not pass the authentication'
    tip_text = 'Please check your cookie and user identity'
    return user_tip_page(header_text,tip_text,
                         jump_to_logout=True,jump_to_back=True)

def get_user_by_cookie(request):
    """
    Check the cookie of a user, and if the cookie is correct and logged in
    then return the user entity. Else return False
    """
    login = check_login(request)
    if login == False:
        return False
    user = get_user_by_name(login[0])
    if user == False:
        return False
    auth = user_auth(request,login[0])
    # Can return many values, including 'NL'(although impossible here)
    if auth != True:  
        return False
    return user

def get_page_meta(request):
    """
    Returns the common data (meda) needed to render most of the page. It is
    a dictionary with keys being the meta name.
    """
    meta = {}
    meta['user_basic'] = get_user_by_cookie(request)
    meta['now'] = datetime.utcnow()
    meta['colors'] = ColorType.objects.all() # Color table available whole site
    
    return meta
def get_user_by_name(username):
    """
    Provide a username and returns the UserBasic object if that username exists
    or returns False if doesn't exist
    """
    try:
        ub = UserBasic.objects.get(username__exact=username)
    except ObjectDoesNotExist:
        return False
    else:
        return ub
    
def check_password_length(password):
    if len(password) < 6 or len(password) > 15:
        return False
    else:
        return True

def check_username_password_length(username,password):
    username_len = len(username)
    if (check_password_length(password) == False or
        username_len < 6 or username_len > 30):
        return False
    else:
        return True

def user_extend_init(ue):
    """
    Initialize an UserExtend object, setting all integer fields to 0
    uid is not set, you must set it by hand.
    """
    ue.money = 0
    ue.credit = 0
    ue.num_of_posts = 0
    ue.num_of_threads = 0
    ue.privilege = 0
    ue.title = ''
    ue.signature = ''
    return

def user_info_init(ui):
    """
    Iniailize an user info.
    Birthday will not be initialized, also you need to specify the uid by hand
    """
    ui.email = ''
    ui.name = ''
    ui.country = ''
    ui.city = ''
    ui.gender  =''
    return

def make_new_user(username,password):
    """
    Make the new user, including UserBasic, UserExtend, and UserInfo
    """
    ub = UserBasic()
    ue = UserExtend()
    ui = UserInfo()
    ub.username = username
    ub.password = make_password(password)
    ub.save()
    ue.uid = ub
    ui.uid = ub
    user_extend_init(ue)
    user_info_init(ui)
    ui.save()
    ue.save()
    return ub

def check_login(request):
    """
    Return username if logged in, else False

    This will not get you a current user. Just the information from the cookie
    """
    cookie = request.session
    if cookie.has_key('logged_in') and cookie['logged_in'] == True:
        return (cookie['username'],cookie['password'])
    else:
        return False

def record_login(request,username,ency_password,status=True):
    """
    Add a cookie entry if logged in
    The entry will only record the username, password, and then set logged_in as True

    You can use status to command the user to login or logout
    """
    request.session['logged_in'] = status
    request.session['username'] = username
    request.session['password'] = ency_password
    return

def user_auth(request,request_name):
    """
    Compare whether the user password and username in the cookie is the
    same as those recorded in the library, also make sure the requested
    username is the same as the username in the cookie.

    Return True if authenticate success, False if cookie not valie,
    None if requested name is different from the name in the cookie,
    and 'NL' if not login.
    """
    cookie_name_pass = check_login(request)
    if cookie_name_pass == False:
        return 'NL'
    elif cookie_name_pass[0] != request_name:
        return None
    ub = get_user_by_name(request_name) # Read from the database
    if check_password(cookie_name_pass[1],ub.password) == False:
        return False
    else: # Passeds all tests
        return True

###########################
# About login and logout ##
###########################

def userext_config_page(request,username):
    pass

def userinfo_config_page(request,username):
    pass

def user_tip_page(header_text='',tip_text='',more_text=[],jump_to_register=False,
                  jump_to_login=False,jump_to_logout=False,
                  jump_to_back=False,jump_to_main=False,default_username='',
                  meta=False):
    return render_to_response('user_tip.html',
                              {'header_text': header_text,
                               'tip_text': tip_text,
                               'more_text': more_text,
                               'jump_to_register': jump_to_register,
                               'jump_to_login': jump_to_login,
                               'jump_to_logout': jump_to_logout,
                               'jump_to_back': jump_to_back,
                               'jump_to_main': jump_to_main,
                               'default_username': default_username,
                               'meta': meta})

def user_check_register(request):
    param = request.POST
    default_username = ''
    meta = get_page_meta(request)
    if (param.has_key('username') and param.has_key('password')
        and param.has_key('password2')):
        # Used for remdering error page (both)
        default_username = param['username']
        # If error happens the error meesage is always this
        header_text = 'Registration Fail'
        # Frequently used Variables
        username = param['username']
        password = param['password']
        # Check length
        if check_username_password_length(username,password) == False:
            more_text = ['Password length must be between 6 and 15 characters']
            more_text.append('And user name length must be between 6 to 30 characters')
            return user_tip_page(header_text=header_text,more_text=more_text,
                                 jump_to_register=True,
                                 default_username=username,
                                 meta=meta,)
        # See if the username has been used
        if get_user_by_name(username) != False:
            tip_text = 'User name already exists. Please Pick another one'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_register=True,
                                 default_username=username,
                                 meta=meta)
            
        # Check password equality
        if param['password'] != param['password2']:
            tip_text = 'Your passwords does not match'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_register=True,
                                 default_username=username,
                                 meta=meta)
        else:
            ub = make_new_user(username,password)
            header_text = 'Register Successfully'
            tip_text = 'You can now login using the user name and password'
            more_text = ['Username: ' + param['username']]
            more_text.append('UID: ' + str(ub.uid))
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 more_text=more_text,
                                 jump_to_login=True,
                                 default_username=username,
                                 meta=meta)     
    else:
        header_text = 'Register Fail'
        tip_text = 'Please complete your registration data'
        return user_tip_page(header_text=header_text,tip_text=tip_text,
                             jump_to_register=True,
                             default_username=default_username,
                             meta=meta)

def user_check_login(request):
    """
    Check whether a user input pair of username and password is qualified
    If it is then we direct it to the successful page.
    """
    param = request.POST
    meta = get_page_meta(request)
    # Common one for login fail
    header_text = 'Login Fail'
    if param.has_key('username') and param.has_key('password'):
        username = param['username']
        password = param['password']
        # Check completeness
        if username == '' or password == '':
            tip_text = 'Please complete login information'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_login=True,
                                 meta=meta)   
        # Common
        default_username = username
        ub = get_user_by_name(username)
        # No such user, get_user_by_name() returns False
        if ub == False:
            tip_text = 'User name does not exist'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_login=True,
                                 default_username=default_username,
                                 meta=meta)
        elif check_password(password,ub.password) == False:
            tip_text = 'Password is incorrect. Please try again'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_login=True,
                                 default_username=default_username,
                                 meta=meta)
        else:
            header_text = 'Login Successfully' # Override the 'login fail' one
            tip_text = 'Enjoy yourself'
            record_login(request,username,password)
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_main=True,
                                 meta=meta,)
    else:
            tip_text = 'Please complete login information'
            return user_tip_page(header_text=header_text,tip_text=tip_text,
                                 jump_to_login=True,meta=meta)        

        
        
def user_login_page(request,default_username=''):
    """
    Display the user login page. CSRF used.

    The default_username will be rendered as the username field in the form.
    This is mainly used when you have some errors during register and you want
    to go back to try again.
    """
    if check_login(request) != False:
        return user_tip_page(header_text='Login Fail',
                             tip_text='You have already logged in',
                             jump_to_back=True,jump_to_logout=True,
                             meta=get_page_meta(request))
    return render_to_response('user_login.html',{'default_username':default_username},
                              context_instance=RequestContext(request))

def user_logout_page(request):
    """
    Let the user to logout.

    Clear cookie: logged_in, username
    """
    username = check_login(request) # Returns a tuple
    if username != False:
        request.session['logged_in'] = False
        header_text = 'You have successfully logged out!'
        tip_text = 'Now you can login as a new user'
        return user_tip_page(header_text=header_text,tip_text=tip_text,
                             jump_to_login=True,meta=get_page_meta(request))
    else:
        return user_not_login_error_page()

def user_register_page(request,default_username=''):
    """
    Display the user register page. CSRF prevension used.
    Check cookie: logged_in
    """
    username = check_login(request)
    
    if username != False: # Already logged in
        header_text = 'Sorry'
        tip_text = 'You should logout first!'
        return user_tip_page(header_text=header_text,tip_text=tip_text,
                             jump_to_logout=True,
                             default_username=username,
                             meta=get_page_meta(request))
    else: # Allow register
        return render_to_response('user_register.html',{'default_username': default_username},
                                  context_instance=RequestContext(request))
