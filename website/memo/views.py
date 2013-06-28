# _*_ coding: utf8 _*_
from django import http
from django.views.generic.base import View, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from models import User, Entry
from forms import RegisterForm
import utils


def _as_view(name, login=False):
    ''' class decorator to get a short name from django generic views
    parameters:
        name -- short name for view function
        login -- whether the view need user login
    # old style: app.views.ViewClass.as_view()
    # new style: app.views.NAME
    '''

    from django.contrib.auth.decorators import login_required

    def decorator(cls):
        globals()[name] = login_required(cls.as_view()) if login else cls.as_view()
        return cls
    return decorator


@_as_view('home')
class HomeView(TemplateView):
    template_name = 'home.html'


@_as_view('register')
class RegisterView(TemplateView):
    template_name = 'user/register.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['form'] = RegisterForm
        return context

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                user.save()
                return self.render_to_response({'status': 'success'})
            else:
                return self.render_to_response({'status': 'fail', 'form': form})
        else:
            return self.render_to_response({'form': form})


def login(request):
    from django.contrib.auth.views import login as login_view
    return login_view(request,
                      template_name='user/login.html')


def logout(request):
    from django.contrib.auth import logout as dj_logout
    dj_logout(request)
    # redirect to the home page
    return redirect(reverse('memo.views.home'))


@_as_view('memo_io', login=True)
class ImportExportView(TemplateView):
    template_name = 'memo/import_export.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.POST.get('action')
        if action == 'import':
            f = request.FILES.get('file')
            for date, text, star in utils.str2entrys(f.read()):
                Entry(user=user, date=date, text=text, star=star).save()
        elif action == 'export':
            buf = ''.join(map(lambda e: utils.entry2str(e), user.entry_set.all()))
            resp = http.HttpResponse(buf, content_type='text/plain')
            resp['Content-Disposition'] = 'attachment; filename="entrys_export.txt"'
            return resp
        return self.render_to_response({})


@_as_view('memo_ajax', login=True)
class AjaxView(View):
    def get(self, request, *args, **kwargs):
        ''' get entry with ajax request and return json format
        URL parameters:
            mode=single:
                query=METHOD -- query method, can be 'date', 'random', 'next', 'prev':
                    'date' -> require 'date'
                    'random' -> not other parameters required
                    'next', 'prev' -> require 'date' as baseline
                date=YYYY-MM-DD -- targeted query date, all date must be in 'YYYY-MM-DD' format
            mode=batch:
                query=all/year/month/range/star
                value=VALUE, format determined by query type
                    year -> YYYY
                    month -> YYYY-MM
                    range -> YYYY-MM-DD_YYYY-MM-DD
            text -- specified whether to fetch original text, default is False

        response:
            {
                'status' = True/False, /* if request success, return True, else False */
                'msg' = 'OPTIONAL MESSAGE if REQUEST FAILED',
                'count' = NUM, /* number of entries return */
                'entries' = [
                    {'date': 'YYYY-MM-DD',
                     'star': True/False,
                     'html': 'CONTENT OF THE ENTRY IN HTML',
                     'text': 'CONTENT OF THE ENTRY IN TEXT', /* optional, return if text set */
                    },
                    { ... }, /* entry 2 */
                    ...
                ]
            }
        '''
        pass

    def post(self, request, *args, **kwargs):
        pass
