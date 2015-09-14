# Models for forum

from django.db import models
from public.models import *
from django import forms

################################
# Image Form ###################
################################

class ImageForm(forms.Form):
    img = forms.ImageField()

################################
# Type Definition ##############
################################

class ProfileType(models.Model):
    name = models.CharField(max_length=50)
    page = models.CharField(max_length=128)
    def __unicode__(self):
        return self.name + ' @ ' + self.page

class OperationType(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

# Configured using the admin page, static when the forum is operating
class BoardType(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(unique=True)
    def __unicode__(self):
        return self.name + '@' + str(self.order)

class ThreadType(models.Model): # Automatic primary key added
    name = models.CharField(max_length=50)
    # Only this board will allow this type. You can also let it to be NULL
    bid = models.ForeignKey('BoardBasic',null=True) 
    def __unicode__(self):
        return self.name

class MessageType(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class FloorType(models.Model):
    name = models.CharField(max_length=10)
    def __unicode__(self):
        return self.name

class ForumSystemAdmin(models.Model):
    uid = models.ForeignKey(UserBasic)
    def __unicode__(self):
        return str(self.uid.uid) + ': ' + self.uid.username
    
class BoardBasic(models.Model):
    bid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=80)
    thread_num = models.IntegerField()
    post_num = models.IntegerField()
    # There is a constraint, i.e. the bid of this type must be the same in
    # ThreadType
    btype = models.ForeignKey(BoardType)
    # We must use the real ID instead of the ForeignKey abstract to do this
    # since there is a circular reference
    last_thread = models.ForeignKey('ThreadBasic',null=True,blank=True)
    # last_thread_time can be just retrieved using the foreign key

    def __unicode__(self):
        return "Board " + self.name

##########################
# About thread ###########
##########################
class ThreadBasic(models.Model):
    tid = models.AutoField(primary_key=True)
    bid = models.ForeignKey(BoardBasic)
    uid = models.ForeignKey(UserBasic,related_name='created_thread')
    title = models.CharField(max_length=120)
    #text = models.TextField()
    ttype = models.ForeignKey(ThreadType)
    last_reply_time = models.DateTimeField() # Create is also reply
    last_reply_user = models.ForeignKey(UserBasic, related_name='last_reply')
    create_time = models.DateTimeField(auto_now_add=True)
    num_of_read = models.IntegerField()
    num_of_reply = models.IntegerField()
    #upvote = models.IntegerField()
    #downvote = models.IntegerField()
    privilege = models.IntegerField() # 0 means normal, -1 means always on top

    locked = models.BooleanField()  # can't reply
    hided = models.BooleanField()   # won't display, can't read
    highlighted = models.BooleanField()
    # Stores a HEX color RGB representation, without the leading '#'
    highlight_color = models.ForeignKey(ColorType,null=True,blank=True)
    # This is used to post some blog on the personal space
    # private = models.BooleanField()
    def __unicode__(self):
        return self.title

"""
class SuperThread(models.Model):
    stid = models.AutoField(primary_key=True)
    bid = models.OneToManyField(BoardBasic)
    uid = models.ForeignKey(ForumSystemAdmin)
    title = models.CharField(max_length=120)
    text = models.TextField()
    sttype = models.ForeignKey(ThreadType)
    create_time = models.DateTimeField(auto_now_add=True)
    """
"""

class ThreadExtend(models.Model):
    tid = models.OneToOneField(ThreadBasic)
    upvote = models.IntegerField()
    downvote = models.IntegerField()
"""
    
##########################
# About Post #############
##########################
class PostBasic(models.Model):
    pid = models.AutoField(primary_key=True)
    tid = models.ForeignKey(ThreadBasic)
    uid = models.ForeignKey(UserBasic)
    text = models.TextField()
    upvote = models.IntegerField()
    downvote = models.IntegerField()
    post_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now_add=True)
    floor = models.IntegerField()
    privilege = models.IntegerField()
    def __unicode__(self):
        if len(self.text) > 30:
            return self.text[:30] + ' @ ' + str(self.tid.tid)
        else:
            return self.text + ' @ ' + str(self.tid.tid)
##########################
# About Reply ############
##########################
class ReplyBasic(models.Model):
    rid = models.AutoField(primary_key=True)
    pid = models.ForeignKey(PostBasic)
    uid = models.ForeignKey(UserBasic)
    text = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        if len(self.text) > 30:
            return self.text[:30] + ' @ ' + str(self.pid.pid)
        else:
            return self.text + ' @ ' + str(self.pid.pid)
    
##########################
# About User Relation ####
##########################

class UserFriend(models.Model):
    uid_1 = models.ForeignKey(UserBasic,related_name='friend_1')
    uid_2 = models.ForeignKey(UserBasic,related_name='friend_2')
    friend_date = models.DateTimeField(auto_now_add=True)
    
class UserMessage(models.Model):
    from_uid = models.ForeignKey(UserBasic,related_name='msg_from')
    to_uid = models.ForeignKey(UserBasic,related_name='msg_to')
    mtype = models.IntegerField() # No configurable types because this is static
    highlight = models.BooleanField()
    msg_date = models.DateTimeField(auto_now_add=True)

class UserVote(models.Model):
    uid = models.ForeignKey(UserBasic)
    pid = models.ForeignKey(PostBasic)
    vote_time = models.DateTimeField(auto_now_add=True)
