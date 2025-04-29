from django.db import models

# Create your models here.

#filetable
class FileTable(models.Model):
    file = models.FileField(upload_to='uploads/',null=True, blank=True)
    id = models.CharField(max_length=255,primary_key=True)
    fileName = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ext = models.CharField(max_length=255)

