from django.contrib import admin
from public.models import *
from forum.models import *

admin.site.register(UserBasic)
admin.site.register(UserExtend)
admin.site.register(UserInfo)
admin.site.register(ThreadBasic)
admin.site.register(PostBasic)
admin.site.register(ReplyBasic)
admin.site.register(BoardBasic)
admin.site.register(ThreadType)
admin.site.register(MessageType)
admin.site.register(UserFriend)
admin.site.register(UserMessage)
admin.site.register(ForumSystemAdmin)
admin.site.register(BoardType)
admin.site.register(ColorType)
admin.site.register(FloorType)
admin.site.register(UserVote)
admin.site.register(ProfileType)
