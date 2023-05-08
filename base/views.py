from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message
from .forms import roomForm
from django.db.models import Q

# Create your views here.
# rooms = [
#     {'id':1, 'name': "let's learn python"},
#     {'id':2, 'name': "let's learn data science"},
#     {'id':3, 'name': "let's learn algorithms"},
#     {'id':4, 'name': "let's learn judo"}
# ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('Username').lower()
        password = request.POST.get('Password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ""
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q) |
                                Q(host__username__icontains=q)
                                )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.all()
    context = {"rooms": rooms, "topics": topics,
               "room_count": room_count, "room_messages": room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {"room": room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = roomForm()
    if request.method == 'POST':
        form = roomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        form = roomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    if request.user != room.host:
        return HttpResponse('you are not allowed to do this!!')

    form = roomForm(instance=room)
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    if request.user != room.host:
        return HttpResponse('you are not allowed to do this!!')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deletemessage(request, pk):
    roommessage = Message.objects.get(id=pk)
    if request.method == 'POST':
        roommessage.delete()
        return redirect('room', roommessage.room_id)

    # if request.user != roommessage.user:
    #     return HttpResponse('you are not allowed to do this!!')
    return render(request, 'base/delete.html', {'obj': roommessage})
