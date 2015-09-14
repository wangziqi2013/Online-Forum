from django.db import models

class ColorType(models.Model):
    rgb = models.CharField(max_length=6)
    name = models.CharField(max_length=16,blank=True) # Optional name
    def __unicode__(self):
        if self.name != '':
            return self.name
        else:
            return 'RGB ' + self.rgb

class UserBasic(models.Model):
    username = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=128)
    uid = models.AutoField(primary_key=True)
    def __unicode__(self):
        return self.username

class UserExtend(models.Model):
    uid = models.OneToOneField(UserBasic)
    money = models.IntegerField()
    credit = models.IntegerField()
    num_of_posts = models.IntegerField()
    num_of_threads = models.IntegerField()
    register_date = models.DateTimeField(auto_now_add=True)
    privilege = models.IntegerField()
    title = models.CharField(max_length = 20,blank=True)
    signature = models.CharField(max_length = 50,blank=True)
    image = models.ImageField(upload_to='image_upload/',
                              default='image_upload/default.jpg')
    def __unicode__(self):
        return self.uid.username + ' Account'

class UserInfo(models.Model):
    uid = models.OneToOneField(UserBasic)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=30,blank=True)
    birthday = models.DateField(null=True)
    country = models.CharField(max_length=30,blank=True)
    city = models.CharField(max_length=30,blank=True)
    gender = models.CharField(max_length=1,blank=True)
    def __unicode__(self):
        return self.uid.username + " Information"
