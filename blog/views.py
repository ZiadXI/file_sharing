import uuid
from datetime import datetime

from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views import View
from .models import FileTable
from blog.models import FileTable
from django.views.generic import TemplateView
import boto3
from django.conf import settings



def home_view(request):
    return render(request,'home.html',context={})


def blog_view(request):
    files = FileTable.objects.all().order_by('-uploaded_at')

    return render(request, 'uplodedFile.html', {'files': files})

def upload_file(request):
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        uploaded_files = []

        ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip']

        for file in files:
            ext = file.name.split('.')[-1]
            if ext not in ALLOWED_EXTENSIONS:
                return JsonResponse({
                    'status': 'error',
                    'message': f'File type {ext} is not allowed'
                }, status=400)

            fileid = str(uuid.uuid4())

            # Save file to media folder and record to DB
            uploaded_file = FileTable.objects.create(
                id=fileid,
                fileName=file.name,
                file=file,
                ext=ext,
                uploaded_at=timezone.now()
            )
            uploaded_files.append(file.name)
            uploaded_file.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{len(files)} file(s) uploaded successfully',
            'files': uploaded_files
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


def download_file(request, file_id):
    file_obj = FileTable.objects.get(id=file_id)

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    file_data = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_obj.file.name)

    response = HttpResponse(file_data['Body'].read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.fileName}"'

    return response