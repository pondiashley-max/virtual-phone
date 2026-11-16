import os
import sys
import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='virtual-phone-secret-key-system',
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=['*'],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.staticfiles',
            'phone_system',
        ],
        MIGRATION_MODULES={
            'phone_system': 'migrations',
        },
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'phone_alpha', 'templates'),
                os.path.join(BASE_DIR, 'phone_beta', 'templates'),
            ],
            'APP_DIRS': True,
        }],
        STATIC_URL='/static/',
        STATICFILES_DIRS=[
            os.path.join(BASE_DIR, 'phone_alpha', 'static'),
            os.path.join(BASE_DIR, 'phone_beta', 'static'),
        ],
        MEDIA_URL='/media/',
        MEDIA_ROOT=os.path.join(BASE_DIR, 'media'),
    )

from django.apps import AppConfig

class PhoneSystemConfig(AppConfig):
    name = 'phone_system'
    label = 'phone_system'
    path = BASE_DIR

sys.modules['phone_system'] = sys.modules[__name__]

django.setup()

from django.core.management import execute_from_command_line, call_command
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path
from django.http import JsonResponse
from django.db import models
from django.conf.urls.static import static

class ChatMessage(models.Model):
    sender = models.CharField(max_length=50)
    recipient = models.CharField(max_length=50)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'phone_system'

class SharedItem(models.Model):
    sender = models.CharField(max_length=50)
    recipient = models.CharField(max_length=50)
    item_type = models.CharField(max_length=20)
    file = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'phone_system'

def home_view(request):
    return redirect('alpha_inbox')

def alpha_inbox_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send_message':
            text = request.POST.get('text', '').strip().lower()
            if text:
                ChatMessage.objects.create(
                    sender='alpha',
                    recipient='beta',
                    text=text
                )
        elif action == 'share_file':
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                SharedItem.objects.create(
                    sender='alpha',
                    recipient='beta',
                    item_type=request.POST.get('item_type', 'file'),
                    file=uploaded_file,
                    file_name=uploaded_file.name.lower()
                )
        return redirect('alpha_inbox')

    messages = ChatMessage.objects.all().order_by('timestamp')
    items = SharedItem.objects.all().order_by('timestamp')

    context = {
        'phone_name': 'alpha',
        'peer_name': 'beta',
        'messages': messages,
        'items': items,
    }
    return render(request, 'alpha_inbox.html', context)

def beta_inbox_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send_message':
            text = request.POST.get('text', '').strip().lower()
            if text:
                ChatMessage.objects.create(
                    sender='beta',
                    recipient='alpha',
                    text=text
                )
        elif action == 'share_file':
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                SharedItem.objects.create(
                    sender='beta',
                    recipient='alpha',
                    item_type=request.POST.get('item_type', 'file'),
                    file=uploaded_file,
                    file_name=uploaded_file.name.lower()
                )
        return redirect('beta_inbox')

    messages = ChatMessage.objects.all().order_by('timestamp')
    items = SharedItem.objects.all().order_by('timestamp')

    context = {
        'phone_name': 'beta',
        'peer_name': 'alpha',
        'messages': messages,
        'items': items,
    }
    return render(request, 'beta_inbox.html', context)

def api_status_view(request):
    messages = list(ChatMessage.objects.all().order_by('timestamp').values('sender', 'recipient', 'text', 'timestamp'))
    items = list(SharedItem.objects.all().order_by('timestamp').values('sender', 'recipient', 'item_type', 'file_name', 'file', 'timestamp'))
    for item in items:
        item['file_url'] = settings.MEDIA_URL + str(item['file'])
    return JsonResponse({
        'messages': messages,
        'items': items
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('alpha/', alpha_inbox_view, name='alpha_inbox'),
    path('beta/', beta_inbox_view, name='beta_inbox'),
    path('api/status/', api_status_view, name='api_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if __name__ == '__main__':
    try:
        call_command('makemigrations', 'phone_system', interactive=False)
        call_command('migrate', interactive=False)
    except Exception as e:
        print("migration note:", e)
    execute_from_command_line(sys.argv)
