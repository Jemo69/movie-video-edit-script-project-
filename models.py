from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.TextField()

    def __str__(self):
        return self.name

class Video(Model):
    id = fields.IntField(pk=True)
    video_name = fields.CharField(max_length=255)
    project_link = fields.TextField()

    def __str__(self):
        return self.video_name
