# View for the forum
from forum.models import *  # Forum data models
from public.models import * # User data models
from datetime import datetime
# Use to redirect the broser
from django.http import HttpResponseRedirect, HttpResponse
# Used to get a URL from the view method path (as well as argument)
from django.core.urlresolvers import reverse
# Used in CSRF token authentication
from django.template import RequestContext
# Used to render the template; Used to retrieve an object from the model
from django.shortcuts import render_to_response, get_object_or_404, render
# Used to check password
from django.contrib.auth.hashers import check_password, make_password
# Used to test whether an entry exist in the database, objects.get() will raise
from django.core.exceptions import *
# Raise this exception when it is needed
from django.http import Http404
from public.views import check_login, user_tip_page, user_not_login_error_page
from public.views import user_auth, user_not_authentic_error_page
from public.views import get_user_by_cookie, get_page_meta, debug_output
from public.views import record_login, check_password_length
from django import forms
from django.contrib.auth.hashers import check_password

#################################
# Special handling for image ####
#################################

def forum_uploadimage_page(request):
    if request.method == 'POST':
        form = ImageForm(request.POST,request.FILES)
        if form.is_valid():
            ub = get_user_by_cookie(request)
            if ub == False:
                raise Http404
            else:
                ue = ub.userextend
            ue.image = form.cleaned_data['img']
            ue.save()
            return user_tip_page('Image Uploaded Successfuly',
                                 'Now you can refresh the page and see a change',
                                 jump_to_back=True,
                                 meta=get_page_meta(request))
        else:
            raise Http404
    else:
        form = ImageForm()
        return render(request,'forum_upload_image.html',
                      {'form': form})

#################################
# User Profile ##################
#################################

def auth_fail_tip():
    return user_tip_page('Authentication Fail','You need to login first',
                         jump_to_login=True,
                         jump_to_back=True)

def forum_basicprofile_page(request):
    if get_user_by_cookie(request) == False:
        return auth_fail_tip()
    return render(request,'forum_basic_profile.html',
                  {'meta': get_page_meta(request)})

def forum_password_page(request):
    ub = get_user_by_cookie(request)
    if ub == False:
        return auth_fail_tip()
    if request.method == 'GET':
        return render(request,'forum_update_password.html',
                      {'meta': get_page_meta(request)})
    elif request.method == 'POST':
        param = request.POST
        if check_password(param['old_password'],ub.password) == False:
            return user_tip_page('Operation Fail',
                                 'Your old password is not correct',
                                 jump_to_back=True)
        if param['new_password1'] != param['new_password2']:
            return user_tip_page('Operation Fail',
                                 'Two passwords do not match',
                                 jump_to_back=True)
        if check_password_length(param['new_password1']) == False:
            return user_tip_page('Operation Fail',
                                 'Password length must be between 6 and 15',
                                 jump_to_back=True)
        # Use this to logout, just write a false to the cookie
        record_login(request,'','',False)
        return user_tip_page('Operation Successful',
                             'Your password has been updated. Please login again.',
                             jump_to_login=True)

#################################
# Admin Facilities ##############
#################################

def check_forum_system_admin(request):
    """
    Check whether a user is the system admin through the request

    Return None if not login
    Return False if not authentic
    Return True if OK
    """
    user = check_login(request)
    if user == False:
        return None   # Not login
    else:
        username = user[0]
    auth = user_auth(request,username) # requested name is the name returned
    if auth != True:
        return False   # user identity not correct
    try:
        uid = UserBasic.objects.get(username__exact=username).uid
    except ObjectDoesNotExist:
        return False   # No this user (forged cookie?)
    try:
        ForumSystemAdmin.objects.get(uid__exact=uid)
    except ObjectDoesNotExist:
        return False   # Not a system admin
    else:
        return True

def synchronize_board_statistics(request,bid):
    """
    It will get all threads and posts belongs to this board, and calculate
    an aggregration using .objects.all().aggregate(count())

    Do not call this directly, since no user authentication is done
    """
    try:
        board = BoardBasic.objects.get(pk=bid)
    except ObjectDoesNotExist:
        raise Http404
    thread_num = ThreadBasic.objects.filter(bid__exact=bid).count()
    post_num = PostBasic.objects.filter(tid__bid__exact=bid).count()
    # Revised: For now a thread is not more a post
    #post_num += thread_num # Thread is also a post
    board.thread_num = thread_num
    board.post_num = post_num
    board.save()
    return

def sync_all_board(request):
    ret = check_forum_system_admin(request)
    if ret == False:
        return user_not_authentic_error_page()
    elif ret == None:
        return user_not_login_error_page()

    boards = BoardBasic.objects.all()
    for i in boards:
        synchronize_board_statistics(request,i.bid)
        
    return user_tip_page('Operation Successful',
                         "The forum has been synchronized",
                         jump_to_main=True)
    
#######################

def forum_board_page(request):
    """
    Renders the board page. Each catrgory of board is grouped into one element
    in the list
    """
    # forums = BoardBasic.objects.order_by(btype__)
    # This is always passed into the forum template
    board_types = BoardType.objects.order_by('order').all()
    boards = []
    for i in board_types:
        type_name = i.name
        type_board = i.boardbasic_set.all()
        if len(type_board) == 0:
            continue
        else:
            type_dict = {'name': type_name, 'board': type_board}
            boards.append(type_dict)
    user_basic = get_user_by_cookie(request)
    return render_to_response('forum_board.html',{'boards':boards,
                                                  'meta': get_page_meta(request)
                                                  })
def set_thread_per_page(request):
    return set_object_per_page(request)

def set_post_per_page(request):
    return set_object_per_page(request)

def set_object_per_page(request):
    """
    Process the post data of the form on thread/post page. The data contains a page
    string and a thread_per_page string. Both needs to be a numerical string
    so we need to check using int(). If int() throws error then just use the
    hard-coded default
    """
    param = request.POST
    if param.has_key('bid'):
        bid = param['bid']
    elif param.has_key('tid'):
        tid = param['tid']

    try:
        page = int(param['goto_page'])
    except ValueError:  # Either null string or invalid string
        page = 1

    try:
        object_per_page = int(param['object_per_page'])
    except ValueError:  # Either null string or invalid string
        object_per_page = 30

    if param.has_key('bid'):
        return HttpResponseRedirect(reverse('forum.views.forum_thread_page',args=[bid,page,object_per_page]))
    elif param.has_key('tid'):
        return HttpResponseRedirect(reverse('forum.views.forum_post_page',args=[tid,page,object_per_page]))

def forum_profile_page(request):
    ub = get_user_by_cookie(request)
    meta = get_page_meta(request)
    if ub == False:
        return user_tip_page('Authorization Fail','You need to login first',
                             jump_to_back=True,jump_to_main=True)
    pt = ProfileType.objects.all()
    return render(request,'forum_profile_page.html',{'meta': meta,
                                                     'profile_type': pt})

def get_page_range(request_page,object_total,object_per_page):
    """
    This is a simple algorithm for calculating the range of index for paged
    content. If you have many objects and you want to display them or process
    them in pages, each page having a fixed number of dobject, then you can use
    this function. Given the requested page number (current page), total number
    of objects and the number of objects in one page, you can get back a tuple
    the first element of which is the start index, and the second element
    is the index next to the last object. (So that you can use it in slice
    without any modification). The third element is the number of total page

    Page number starts from 1, which is different from python's indexing

    return: tuple as described above. Or False if requested page exceeds the
    total page.
    """
    start_index = (request_page - 1) * object_per_page
    end_next_index = (request_page) * object_per_page
    total_page = (object_total + object_per_page - 1) / object_per_page
    if start_index >= object_total:
        return False
    elif end_next_index > object_total:
        return (start_index,object_total,total_page)
    else:
        return (start_index,end_next_index,total_page)

def forum_post_page(request,tid,page='1',post_per_page='30'):
    page = int(page)
    post_per_page = int(post_per_page)
    tid = int(tid)
    meta = get_page_meta(request)
    floor_name_num = FloorType.objects.count()

    try:
        thread_basic = ThreadBasic.objects.get(pk=tid)
    except ObjectDoesNotExist:
        return user_tip_page('Thread Does Not Exist',
                             'Please check your URL',
                             jump_to_back=True,
                             meta=meta)
    # Usually this won't happen, just here for safety and completeness
    try:
        board_basic = BoardBasic.objects.get(pk=thread_basic.bid.bid)
    except ObjectDoesNotExist:
        return user_tip_page('Thread Board Does Not Exist, Fatal Error',
                             'Please contact system administrator',
                             jump_to_back=True,
                             meta=meta)
    if thread_basic.hided == True:
        return user_tip_page('Cannot Access Thread',
                             'Thread has been locked',
                             jumo_to_back=True,
                             meta=meta)
    # privilege for the 1st floor is 2, other topped is 1, and normal is 0
    post_set = PostBasic.objects.filter(tid__tid__exact=tid).order_by('-privilege','post_date')
    post_num = post_set.count()
    posts = post_set.all()
    index_range = get_page_range(page,post_num,post_per_page)
    # It is not possible since each thread must at least have one post
    # But we do it for safety and completeness
    if index_range == False and page != 1:
        return user_tip_page('Page Does Not Exist',
                             'Please check your page number',
                             jump_to_back=True,
                             meta=meta)
    elif index_range == False and page == 1:
        total_page = 1
        posts = []
    else:
        total_page = index_range[2]
        posts = posts[index_range[0]:index_range[1]]
    # A dictionary using pid as the key.
    #replies = {}
    #for i in posts:
    #    reply_one_post = ReplyBasic.objects.filter(pid__exact=i.pid).order_by('-post_date').all()
    #    replies[str(i.pid)] = reply_one_post
    
    return render_to_response('forum_post.html',
                              {'board_basic': board_basic,
                               'thread_basic': thread_basic,
                               'posts': posts,
                               'post_per_page': post_per_page,
                               'floor_name_num': floor_name_num,
                               'current_page': page,
                               'total_page': total_page,
                               'meta': meta},
                              context_instance=RequestContext(request))

def forum_thread_page(request,bid,page='1',thread_per_page='30'):
    """
    Display a page of threads, using the given page number and num_of_threads
    per page.
    """
    # Parameters are always passed using Unicode no matter what it is in the
    # regexp
    page = int(page)
    thread_per_page = int(thread_per_page)
    
    meta = get_page_meta(request)
    # We use cached data instead of doing query a each time. So please keep the
    # data synchronized
    try:
        board_basic = BoardBasic.objects.get(pk=bid)
    except ObjectDoesNotExist:
        return user_tip_page('Board Does Not Exist',
                             'Please check your URL',
                             jump_to_back=True,
                             meta=meta)
    else:
        thread_num = board_basic.thread_num
    # Do part of the queries here
    threads = ThreadBasic.objects.filter(bid__bid__exact=bid)
    other = threads.exclude(privilege__exact=-1).filter(hided__exact=False).order_by('-privilege','-last_reply_time').all()
    # Only show these threads when it is the first page
    uppermost_temp = threads.filter(privilege__exact=-1,hided__exact=False).order_by('-last_reply_time')
    hidden_num = threads.filter(hided__exact=True).count()
    normal_thread_num = thread_num - uppermost_temp.count() - hidden_num
    #return debug_output(thread_num)
    if page == 1:
        # Just do the query
        uppermost = uppermost_temp.all()
    else:
        uppermost = []
        # These cannot be counted into the normal threads
    
    page_range = get_page_range(page,normal_thread_num,thread_per_page)
    # If there is no content on the first page then return a null set
    if page_range == False:
        if page == 1:
            other = []
            total_page = 1
        else: # If not requesting page number 1, then just raise an error
            return user_tip_page('Page Does Not Exist',
                                 'Please check your page number',
                                 jump_to_back=True,meta=meta)
    else:
        other = other[page_range[0]:page_range[1]]
        total_page = page_range[2]
        
    #return HttpResponse(str(normal_thread_num),content_type='text/html')
    return render_to_response('forum_thread.html',
                            {'threads':
                             {'uppermost': uppermost,
                              'other': other,}, # Two parts
                             'board_basic': board_basic,
                             'thread_per_page': thread_per_page,
                             'total_page': total_page,
                             'current_page': page,
                             'meta': meta},
                              context_instance=RequestContext(request)) # CSRF 
