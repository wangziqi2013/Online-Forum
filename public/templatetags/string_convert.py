from django import template
from datetime import datetime
from forum.models import FloorType, ColorType
from django.core.exceptions import *
from django.core.urlresolvers import reverse 

# This is a new filter
# Use {% load string_convert %} to load it into a template

register = template.Library()

def readable_time_delta(delta,dt,now):
    """
    Convert the time difference of some given time and the current time into
    a human readable form, including:

    seconds, minutes, hours, days, weeks, months

    We also assume that td1  and td2 can be subtracted directly. If you cannot
    guarantee this then just use utcnow() before passing them.
    """
    number = None
    plural = ''
    days = delta.days
    seconds = delta.seconds
    ms = delta.microseconds
    # Special handling for yesterday
    if dt.day - now.day == 1:
        return 'yesterday ' + num_time(dt)
    if days != 0:
        if days == 1:
            number = days
            plural = ' Day'
        elif days < 7:
            number = days
            plural = ' Days'
        elif days < 14:
            number = days / 7
            plural = ' Week'
        elif days < 30:
            number = days / 7
            plural = ' Weeks'
        else:
            return str(td)
    elif seconds != 0:
        if seconds == 1:
            number = seconds
            plural = ' Second'
        elif seconds < 60:
            number = seconds
            plural = ' Seconds'
        elif seconds < 120:
            number = seconds / 60
            plural = ' Minute'
        elif seconds < 3600:
            number = seconds / 60
            plural = ' Minutes'
        elif seconds < 7200:
            number = seconds / 3600
            plural = ' Hour'
        else:
            number = seconds / 3600
            plural = ' Hours'
    else:
        return num_datetime(dt)
    
    return str(number) + plural + ' Ago'

def render_bold(s):
    while True:
        start_index = s.find('[b]')
        if start_index == -1:
            return s
        end_index = s.find('[/b]',start_index + 3)
        if end_index == -1:
            return s
        s = (s[:start_index] + '<strong>' +
             s[start_index + 3:end_index] + '</strong>' +
             s[end_index + 4:])
    # We should not see this line
    return s

def render_color(s):
    while True:
        start_index = s.find('[color')
        if start_index == -1:
            return s
        end_index = s.find(']',start_index)
        if end_index == -1:
            return s
        color_number = s[start_index + 6:end_index]
        equal_sign = color_number.find('=')
        if equal_sign == -1:
            return s
        try:
            color_number = color_number[equal_sign + 1:].strip()
            color_index = int(color_number)
        except ValueError:
            if color_number[0] == '#':
                color_hex = color_number[1:]
            else:
                return s
        else:
            try:
                color_hex = ColorType.objects.get(pk=color_index).rgb
            except ObjectDoesNotExist:
                return s

        color_end_index = s.find('[/color]',end_index + 1)
        if color_end_index == -1:
            return s
        s = (s[:start_index] + '<span style="color: #' + color_hex + '">' +
             s[end_index + 1:color_end_index] +
             '</span>' + s[color_end_index + 8:])
    # You should not see this line    
    return s

def render_size(s):
    """
    [size = num][/size]
    """
    while True:
        start_index = s.find('[size')
        if start_index == -1:
            return s
        end_index = s.find(']',start_index)
        if end_index == -1:
            return s
        size = s[start_index + 5:end_index]
        equal_sign = size.find('=')
        if equal_sign == -1:
            return s
        try:
            size = int(size[equal_sign + 1:].strip())
        except ValueError:
            return s

        size_end_index = s.find('[/size]',end_index + 1)
        if size_end_index == -1:
            return s
        s = (s[:start_index] + '<span style="font-size: ' + str(size) + 'px">' +
             s[end_index + 1:size_end_index] +
             '</span>' + s[size_end_index + 7:])
    # You should not see this line    
    return s

def render_image(s):
    while True:
        tag = '<img '
        start_index = s.find('[img')
        if start_index == -1:
            return s
        end_index = s.find(']',start_index + 4)
        if end_index == -1:
            return s
        param = s[start_index + 4:end_index]
        param = param.split('=')
        param_pair = []
        for i in param:
            param_pair += i.split()
        param_length = len(param_pair)
        for i in range(0,param_length):
            if param_pair[i] == 'width':
                tag += 'width="' + param_pair[i + 1] + '" '
            elif param_pair[i] == 'height':
                tag += 'height="' + param_pair[i + 1] + '" '
        tag_closing = s.find('[/img]',end_index + 1)
        if tag_closing == -1:
            return s
        src = s[end_index + 1:tag_closing]
        tag += ' style="max-width: 100%" '
        tag += ' src="' + src + '" />'
        s = s[:start_index] + tag + s[tag_closing + 6:]
    # You should not have seen this
    return s

def render_quote(s,tid):
    while True:
        start_index = s.find('[quote')
        if start_index == -1:
            return s
        end_index = s.find(']',start_index + 6)
        if end_index == -1:
            return s
        param = s[start_index + 6:end_index]
        equal_sign = param.find('=')
        if equal_sign == -1:
            return s
        try:
            floor_num = int(param[equal_sign + 1:].strip())
        except ValueError:
            return s
        tag_end_index = s.find('[/quote]',end_index + 1)
        if tag_end_index == -1:
            return s
        quote_text = s[end_index + 1:tag_end_index]
        if len(quote_text) > 200:
            quote_text = quote_text[:200] + '...'
        tag = ''
        tag += '<div style="background-color: #DDDDDD">'
        tag += ('<div style="color: gray">You quoted from floor ' + str(floor_num)
                + '&nbsp;<a href="' +
                reverse('forum.views.forum_post_page',args=[tid,(floor_num + 29) / 30])
                + '#floor_' + str(floor_num) + '">[goto]</a>' +'</div>')
        tag += ('<div> "' + quote_text + '"</div></div>')
        s = s[:start_index] + tag + s[tag_end_index + 8:]
    # You should not have seen this
    return s

@register.filter            
def reply_text_render(s):
    """
    User for rendering styles for replies. Only bold and color are available
    """
    return render_color(render_bold(s))

@register.filter
def post_text_render(s,tid):
    """
    Convert all [tag] [/tag] into proper HTML
    """
    return render_quote(render_image(render_size(render_color(render_bold(s)))),tid)
    

@register.filter
def floor_to_text(floor_index,available_floor):
    if floor_index > available_floor:
        return "Floor %d" % (floor_index)
    else:
        return FloorType.objects.get(pk=floor_index).name

@register.filter
def num_time(dt):
    return "%s:%s:%s" % (dt.hour,dt.minute,dt.second)

@register.filter
def num_date(dt):
    return "%d-%d-%d" % (dt.year,dt.month,dt.day)

@register.filter
def num_datetime(dt):
    return "%d-%d-%d %d:%d:%d" % (dt.year,dt.month,dt.day,
                                  dt.hour,dt.minute,dt.second)

@register.filter
def readable_delta(dt,now):
    now = now.replace(tzinfo=None)
    dt = dt.replace(tzinfo=None)
    delta = now - dt   # We know which one is larger
    return readable_time_delta(delta,dt,now)

@register.filter
def get_range(total,current):
    """
    If we have a range, a current position, this function will return at most 4
    positions before the current, and at most 4 after the current. If we already
    touched the bound then just display as much as possible.

    The numbers start at 1, instead of 0
    """
    start_index = current - 4
    end_next_index = current + 5
    if start_index < 1:
        start_index = 1
    if end_next_index > total + 1:
        end_next_index = total + 1
    return range(start_index, end_next_index) 
