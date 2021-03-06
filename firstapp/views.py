from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, FormView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from .forms import ContactUsForm, RegistrationFormBasic, RegistrationFormSeller
from .models import SellerAdditional, CustomUser


# def index(request):           // just a test function view
#     age = 10
#     arr = ['roy', 'swap', 'rhyes']
#     dic = {'a':'one', 'b':'two'}

#     return render(request, 'firstapp/index.html', {'age' : age, 'array':arr, 'dic':dic})

class Index(TemplateView):
    template_name = "firstapp/index.html"

    def get_context_data(self, **kwargs):
        age = 10
        arr = ['roy', 'swap', 'rhyes']
        dic = {'a':'one', 'b':'two'}
        context_old = super().get_context_data(**kwargs)
        context = {'age' : age, 'array':arr, 'dic':dic, 'context_old':context_old}
        return context

def contactUs(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST['phone']
        if len(phone) < 10 or len(phone) > 10:
            #return HttpResponse("Phone number should have a length of 10")
            raise ValidationError("Phone number should have a length of 10")
        email = request.POST.get('email')
        userQuery = request.POST.get('query')
        print(name + " " + phone + " " + email + " " + userQuery) 
    return render(request, 'firstapp/contactus.html')


def contactus2(request):                #contact us function based view
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():            # when this gets executed it executes cleaned_data
            if len(form.cleaned_data.get('query')) > 10:
                form.add_error('query', "Query length is not right")
                return render(request, 'firstapp/contactus2.html', {'form':form})
            form.save()
            return HttpResponse("Thank you. We will get back to you. ")
        else:
            if len(form.cleaned_data.get('query')) > 10:
                #form.add_error('query', "Query length is not right")
                form.errors['query'] = ['Query length is not right', 'It should be under 10']
            return render(request, 'firstapp/contactus2.html', {'form':form})

    return render(request, 'firstapp/contactus2.html', {'form':ContactUsForm})

class ContactUs(FormView):          # contact us class based view
    form_class = ContactUsForm
    template_name = 'firstapp/contactus2.html'
    success_url = reverse_lazy("firstapp:index")

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """

        if len(form.cleaned_data.get('query')) > 10:
            form.add_error('query', "Query length is not right")
            return render(self.request, 'firstapp/contactus2.html', {'form':form})
        form.save()
        response = super().form_valid(form)
        return response
    
    def form_invalid(self, form):
        """
        If the form is invalid, render the invalid form.
        """
        if len(form.cleaned_data.get('query')) > 10:
            form.add_error('query', "Query length is not right")
            #form.errors['query'] = ['Query length should be under 10']
        response = super().form_invalid(form)
        return response


# class RegisterViewSeller(CreateView):
#     template_name = 'firstapp/register.html'
#     form_class = RegistrationForm
#     success_url = reverse_lazy('firstapp:index')

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == 302:
#             gst = request.POST.get('gst')
#             warehouse_location = request.POST.get('warehouse_location')
#             user = CustomUser.objects.get(email=request.POST.get('email'))
#             sell_a = SellerAdditional.objects.create(user=user, gst=gst, warehouse_location=warehouse_location)
#             return response
#         else:
#             return response


class RegisterViewBasic(CreateView):
    template_name = 'firstapp/registerBasic.html'
    form_class = RegistrationFormBasic
    success_url = reverse_lazy('firstapp:index')

class LoginViewUser(LoginView):
    template_name = 'firstapp/login.html'


class RegisterViewSeller(LoginRequiredMixin, CreateView):
    template_name = 'firstapp/registerSeller.html'
    form_class = RegistrationFormSeller
    success_url = reverse_lazy('firstapp:index')

    def form_valid(self, form):
        user = self.request.user
        user.type.append(user.Types.SELLER)
        user.save()

        form.instance.user = self.request.user
        return super().form_valid(form)

class LogoutViewUser(LogoutView):
    template_name = reverse_lazy("firstapp:index")
