from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from . import forms, models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/index.html')

# for showing signup/login button for student


def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/studentclick.html')

# for showing signup/login button for teacher


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/adminclick.html')


def adminsignup_view(request):
    form = forms.AdminSigupForm()
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()

            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request, 'library/adminsignup.html', {'form': form})


def studentsignup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    mydict = {'form1': form1, 'form2': form2}
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            user.set_password(user.password)
            user.save()
            f2 = form2.save(commit=False)
            f2.user = user
            user2 = f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request, 'library/studentsignup.html', context=mydict)


def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


def afterlogin_view(request):
    if is_admin(request.user):
        return render(request, 'library/adminafterlogin.html')
    else:
        return render(request, 'library/studentafterlogin.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    # now it is empty book form for sending to html
    form = forms.BookForm()
    if request.method == 'POST':
        # now this form have data from html
        form = forms.BookForm(request.POST)
        if form.is_valid():
            user = form.save()
            return render(request, 'library/bookadded.html')
    return render(request, 'library/addbook.html', {'form': form})

#view books
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/viewbook.html', {'books': books})

# delete view 
from .models import Book
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def DeleteBookView(request, book_id):
    if request.method == "POST":
        book = get_object_or_404(Book, pk=book_id)
        book.delete()
        return redirect("viewbook")
    else:
        return redirect("viewbook")
        #end delete book view
#update book
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def UpdateBookView(request, book_id):
    # get the book and form
    book = Book.objects.get(pk=book_id)
    updateForm = forms.BookForm(instance=book)
    if request.method == "POST":
        updateForm = forms.BookForm(request.POST or None,instance=book)
        updateForm.save()
        return redirect('viewbook')
    return render(request, 'library/editbook.html',{'form':updateForm})
    #end update book