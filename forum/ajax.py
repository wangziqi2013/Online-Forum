from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from forum.models import *
from forum.views import get_page_range, auth_fail_tip
from django.http import Http404
from datetime import datetime
from public.templatetags.string_convert import readable_delta, get_range
from django.core.exceptions import *
from public.views import get_user_by_cookie, user_auth, get_page_meta
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.utils.html import escape
from public.templatetags.string_convert import post_text_render 
from django.core.urlresolvers import resolve, reverse
import forum.views

@dajaxice_register
def render_tag_text(request,tag_text,tid):
    text = post_text_render(tag_text,tid)
    return simplejson.dumps({'success': True,
                             'text': text})

@dajaxice_register
def make_new_reply(request,post_id,reply_text):
    ub = get_user_by_cookie(request)
    meta = get_page_meta(request)
    if ub == False:
        return simplejson.dumps({'success': False,
                                 'reason': 'You have not logged in'})
    pb_count = PostBasic.objects.filter(pid__exact=post_id).count()
    if pb_count == 0:
        return simplejson.dumps({'success': False,
                                 'reason': 'Post does not exist'})
    else:
        pb = PostBasic.objects.get(pk=post_id)
    new_reply = ReplyBasic()
    new_reply.pid = pb
    new_reply.uid = ub
    new_reply.text = reply_text
    new_reply.save()
    # Each reply will get you 1 point of money
    ub.userextend.money += 1
    ub.userextend.save()
    # TODO: SEND MESSAGE TO THE OWNER
    return get_post_details(request,post_id,1)

def make_quote_post_text(text,tid,quote_floor):
    pb = PostBasic.objects.filter(tid__exact=tid,floor__exact=quote_floor)
    if pb.count() == 0:
        return text
    pt = pb.all()[0].text
    if len(pt) > 80:
        pt = pt[:80] + '...'
    text = '[quote=' + str(quote_floor) + ']' + pt + '[/quote]' + text
    return text

@dajaxice_register
def get_page(request,page_view):
    meta = get_page_meta(request)
    #try:
    #page = render(request,page_name,{'meta': meta})
    #except:
    #    return simplejson.dumps({'success': False})
    url = reverse(page_view)
    func = eval(page_view)
    request.method = 'GET' # Make sure we are doing the right thing
    page = func(request)
    return simplejson.dumps({'success': True,
                             'content': page.content})

@dajaxice_register
def update_title(request,new_title):
    ub = get_user_by_cookie(request)
    if ub == False:
        return simplejson.dumps({'success': False,
                                 'reason': 'Not logged in'})
    if len(new_title) > 20:
        return simplejson.dumps({'success': False,
                                 'reason': 'Fail: Too Long'})
    ub.userextend.title = new_title
    ub.userextend.save()
    return simplejson.dumps({'success': True,
                             'content': new_title})


@dajaxice_register
def update_signature(request,new_signature):
    ub = get_user_by_cookie(request)
    if ub == False:
        return simplejson.dumps({'success': False,
                                 'reason': 'Not logged in'})
    if len(new_signature) > 50:
        return simplejson.dumps({'success': False,
                                 'reason': 'Fail: Too Long'})
    ub.userextend.signature = new_signature
    ub.userextend.save()
    return simplejson.dumps({'success': True,
                             'content': new_signature})


@dajaxice_register
def make_new_post(request,thread_id,text,privilege=0,quote_floor=None):
    ub = get_user_by_cookie(request)
    meta = get_page_meta(request)
    if ub == False:
        return simplejson.dumps({'success': False,
                                 'reason': 'You have not logged in'})
    tb_count = ThreadBasic.objects.filter(tid__exact=thread_id).count()
    if tb_count == 0:
        return simplejson.dumps({'success': False,
                                 'reason': 'Thread does not exist'})
    else:
        tb = ThreadBasic.objects.get(pk=thread_id)

    if quote_floor != None:
        # Add the quote label, and then send messages
        text = make_quote_post_text(text,thread_id,quote_floor)
        
    new_post = PostBasic()
    new_post.tid = tb
    new_post.uid = ub
    new_post.text = escape(text)  # We do not check the text
    new_post.upvote = 0
    new_post.downvote = 0
    new_post.privilege = privilege
    new_post.floor = PostBasic.objects.filter(tid__tid__exact=thread_id).count() + 1
    new_post.save()

    ub.userextend.money += 1
    ub.userextend.credit += 1
    ub.userextend.num_of_posts += 1
    ub.userextend.save()

    try:
        bb = BoardBasic.objects.get(pk=tb.bid.bid)
    except ObjectDoesNotExist:
        return simplejson.dumps({'success': False,
                                 'reason': 'Board does not exist'})
    bb.post_num += 1
    bb.last_thread = tb
    bb.save()

    tb.last_reply_time = new_post.post_date
    tb.last_reply_user = ub
    tb.save()

    floor_name_num = FloorType.objects.count()
    
    single_post = render(request,'forum_post_block.html',{'i': new_post,
                                          'meta': meta,
                                          'floor_name_num': floor_name_num,})
    return simplejson.dumps({'success': True,
                            'content': single_post.content})
    
@csrf_protect
@dajaxice_register
def vote_post(request,post_id,vote):
    #print request.COOKIES['csrftoken']
    try:
        post = PostBasic.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return simplejson.dumps({'vote_success': False,
                                 'fail_reason': 'Post not found'})
    
    ub = get_user_by_cookie(request)
    if ub == False:
        return simplejson.dumps({'vote_success': False,
                                 'fail_reason': 'You are not logged in'})

    voted_flag = UserVote.objects.filter(uid__uid__exact=ub.uid,pid__pid__exact=post_id).count()

    if voted_flag != 0:
        return simplejson.dumps({'vote_success': False,
                                 'fail_reason': 'You have already voted'})

    uv = UserVote()
    try:
        pv = PostBasic.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return False
    
    uv.uid = ub
    uv.pid = pv
    uv.save()
    
    if vote == 1:
        post.upvote += 1
    elif vote == -1:
        post.downvote += 1
    else:
        return False
    post.save()
    return simplejson.dumps({'votes': (post.upvote,post.downvote),
                             'post_id': post_id,
                             'vote_success': True,})
        

def get_up_down_votes(request,post_id):
    try:
        post = PostBasic.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return (0,0)
    else:
        return (post.upvote,post.downvote)

@dajaxice_register
def get_post_details(request,post_id,request_page):
    replies = ReplyBasic.objects.filter(pid__exact=post_id).order_by('-post_date')
    total = replies.count()
    # We fix the number of relies is at most 5
    page_index = get_page_range(request_page,total,5)
    
    if page_index == False and request_page != 1:
        raise Http404  # Hope this won't happen
    elif page_index == False:
        replies = []
        total_page = 0
    else:
        replies = replies.all()[page_index[0]:page_index[1]]
        total_page = page_index[2]
    
    reply_dict = []
    
    now = datetime.utcnow()
    for i in replies:
        d = {}
        d['text'] = i.text
        d['post_time'] = readable_delta(i.post_date,now)
        d['username'] = i.uid.username
        d['image'] = str(i.uid.userextend.image)
        # TODO: d['user_link'] = reverse('')
        reply_dict.append(d)
        
    available_pages = get_range(total_page,request_page)
    page_link = []
    
    for i in available_pages:
        onclick = """Dajaxice.forum.get_post_details(load_replies,
                    {"post_id": %d, "request_page": %d})""" % (post_id,i)
        page_link.append(onclick)

    votes = get_up_down_votes(request,post_id)
    
    return simplejson.dumps({'total_page': total_page,
                             'request_page': request_page,
                             'replies': reply_dict,
                             'post_id': post_id,
                             'page_link': page_link,
                             'available_pages': available_pages,
                             'votes': votes,
                             'vote_success': True})
