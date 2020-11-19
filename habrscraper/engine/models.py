from django.db import models

class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Hub(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    description = models.TextField()
    link = models.URLField()
    poll = models.BooleanField(default=False)
    poll_interval = models.SmallIntegerField(null=True, default=0)
    last_poll_date_time = models.DateTimeField(auto_created=True)

    class Meta:
        ordering = ["name", "last_poll_date_time"]


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    date_time = models.DateTimeField(auto_created=True)
    #date_time = models.CharField(max_length=50)
    author_link = models.URLField()
    author_name = models.CharField(max_length=100)
    link = models.URLField()
    body = models.TextField()
    hash = models.CharField(max_length=300)

    class Meta:
        ordering = ["date_time", "title"]


# class NewPosts(models.Model):
#     hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
#     Post = models.ForeignKey(Hub, on_delete=models.CASCADE)


class EngineSettings(SingletonModel):
    first_run = models.BooleanField(default=True)
    max_tasks = models.SmallIntegerField()
    hubs_main_url = models.URLField()
