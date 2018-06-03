# coding=utf-8
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.template import loader
import urllib.request
import sys

sys.path.append('G:\Database-APP\DatabaseAPP')
from assets.models import Staff, InviteCode


# Create your views here.

class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=50)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='重复密码', widget=forms.PasswordInput())
    last_name = forms.CharField(label='姓')
    first_name = forms.CharField(label='名')
    email = forms.EmailField(label='邮箱')
    invite_code = forms.CharField(label='邀请码（选填）', max_length=100, required=False)
    # first_name = forms.CharField(label='名')
    # last_name = forms.CharField(label='姓')


@csrf_protect
def regist(request):
    ticket = request.GET.get('ticket')
    randstr = request.GET.get('randstr')
    ip = request.GET.get('ip')
    if randstr:
        textmod = {'aid': '2036447301', 'AppSecretKey': '0CQuV8SIDluGCVpMcfAPwgA**', 'Ticket': ticket, 'UserIP': ip,
                   'Randstr': randstr}
        textmod = urllib.parse.urlencode(textmod)
        req = urllib.request.Request(url='%s%s%s' % ("https://ssl.captcha.qq.com/ticket/verify", '?', textmod))
        res = urllib.request.urlopen(req)
        print(res.read())
        res.close()

    if request.method == 'POST':
        userform = UserForm(request.POST)
        print(userform)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            if User.objects.filter(username=username):
                messages.error(request, '用户已存在！')
                return render(request, "regist.html", {'userform': userform})

            password = userform.cleaned_data['password']
            password_repeat = userform.cleaned_data['password_repeat']
            if password != password_repeat:
                messages.error(request, '两次输入的密码不同！')
                return render(request, "regist.html", {'userform': userform})
            email = userform.cleaned_data['email']
            password = make_password(password, None, 'pbkdf2_sha256')

            invite_code = userform.cleaned_data['invite_code']
            first_name = userform.cleaned_data['first_name']
            last_name = userform.cleaned_data['last_name']

            user = User.objects.create(username=username, password=password, email=email, is_staff=True,
                                       first_name=first_name,
                                       last_name=last_name)
            # User.save()
            if invite_code:
                import base64
                invite_code=str.encode(invite_code)
                try:
                    invite_code_id = int(base64.b64decode(invite_code).decode().split()[0])
                except:
                    messages.error(request, '邀请码错误！')
                    return render(request, "regist.html", {'userform': userform})
                code_obj=InviteCode.objects.get(id=invite_code_id)
                if code_obj.key == invite_code.decode():
                    if code_obj.times:
                        Staff.objects.create(staff_name=last_name + first_name, staff_user=user, staff_dep= code_obj.dept)
                        user.groups.add(code_obj.dept.dep_permmison)
                        code_obj.times -= 1
                        code_obj.save()
                else:
                    messages.error(request, '邀请码错误或失效！')
                    return render(request, "regist.html", {'userform': userform})

            else:
                Staff.objects.create(staff_name=last_name + first_name, staff_user=user)
            messages.success(request, "注册成功")
    else:
        userform = UserForm()

    # return render_to_response('regist.html', {'userform': userform})
    return render(request, "regist.html", {'userform': userform})


def index(request):
    # template = loader.get_template('register/index.html')
    # return HttpResponse(template.render(request))
    return render(request, "index_home.html", {})
