from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from wall.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import Profile, Friend_Request
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import random

User = get_user_model()


def users_list(request):
	allUsers = Profile.objects.exclude(user=request.user)
	sent_friend_requests = Friend_Request.objects.filter(from_user=request.user)
	sent_to = []
	friendsList = []
	for user in allUsers:
		friend = user.friends.all()
		for oneFriend in friend:
			if oneFriend in friendsList:
				friend = friend.exclude(user=oneFriend.user)
		friendsList+=friend
	myFriends = request.user.profile.friends.all()
	for i in myFriends:
		if i in friendsList:
			friendsList.remove(i)
	if request.user.profile in friendsList:
		friendsList.remove(request.user.profile)
	randomList = random.sample(list(allUsers), min(len(list(allUsers)), 10))
	for r in randomList:
		if r in friendsList:
			randomList.remove(r)
	friendsList+=randomList
	for i in myFriends:
		if i in friendsList:
			friendsList.remove(i)
	for se in sent_friend_requests:
		sent_to.append(se.to_user)
	context = {
		'users': friendsList,
		'sent': sent_to
	}
	return render(request, "users_list.html", context)

def friend_list(request):
	friends = request.user.profile.friends.all()
	context={
	'friends': friends
	}
	return render(request, "friend_list.html", context)

@login_required
def send_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	friendRequest, created = Friend_Request.objects.get_or_create(
			from_user=request.user,
			to_user=user)
	return HttpResponseRedirect('/users/{}'.format(user.profile.nick))

@login_required
def cancel_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	friendRequest = Friend_Request.objects.filter(
			from_user=request.user,
			to_user=user).first()
	friendRequest.delete()
	return HttpResponseRedirect('/users/{}'.format(user.profile.nick))

@login_required
def accept_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	friendRequest = Friend_Request.objects.filter(from_user=from_user, to_user=request.user).first()
	user1 = friendRequest.to_user
	user2 = from_user
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	if(Friend_Request.objects.filter(from_user=request.user, to_user=from_user).first()):
		request_rev = Friend_Request.objects.filter(from_user=request.user, to_user=from_user).first()
		request_rev.delete()
	friendRequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.nick))

@login_required
def delete_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	friendRequest = Friend_Request.objects.filter(from_user=from_user, to_user=request.user).first()
	friendRequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.nick))

def delete_friend(request, id):
	userProfile = request.user.profile
	friendProfile = get_object_or_404(Profile, id=id)
	userProfile.friends.remove(friendProfile)
	friendProfile.friends.remove(userProfile)
	return HttpResponseRedirect('/users/{}'.format(friendProfile.nick))

@login_required
def profile_view(request, nick):
	thisProfile = Profile.objects.filter(nick=nick).first()
	thisUser = thisProfile.user
	sent_friend_requests = Friend_Request.objects.filter(from_user=thisProfile.user)
	recieved_friend_requests = Friend_Request.objects.filter(to_user=thisProfile.user)
	user_posts = Post.objects.filter(user_name=thisUser)
	friends = thisProfile.friends.all()
	button = 'none'

	# if user is not in friendlist
	if thisProfile not in request.user.profile.friends.all():
		button = 'not_friend'
		# if friend request has been sent
		if len(Friend_Request.objects.filter(
			from_user=request.user).filter(to_user=thisProfile.user)) == 1:
				button = 'friend_request_sent'
		# if friend request has been received
		if len(Friend_Request.objects.filter(
			from_user=thisProfile.user).filter(to_user=request.user)) == 1:
				button = 'friend_request_received'

	context = {
		'u': thisUser,
		'button_status': button,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': recieved_friend_requests,
		'post_count': user_posts.count
	}
	return render(request, "profile.html", context)

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account has been created!')
			return redirect('register_success')
	else:
		form = UserRegisterForm()
	return render(request, 'register.html', {'form':form})

@login_required
def edit_profile(request):
	if request.method == 'POST':
		userForm = UserUpdateForm(request.POST, instance=request.user)
		profileForm = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if userForm.is_valid() and profileForm.is_valid():
			userForm.save()
			profileForm.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('my_profile')
	else:
		userForm = UserUpdateForm(instance=request.user)
		profileForm = ProfileUpdateForm(instance=request.user.profile)
	context ={
		'u_form': userForm,
		'p_form': profileForm,
	}
	return render(request, 'edit_profile.html', context)

@login_required
def my_profile(request):
	profile = request.user.profile
	currentUser = profile.user
	sent_friend_requests = Friend_Request.objects.filter(from_user=currentUser)
	received_friend_requests = Friend_Request.objects.filter(to_user=currentUser)
	userPosts = Post.objects.filter(user_name=currentUser)
	friends = profile.friends.all()

	# if the user is in friendlist
	buttonStatus = 'none'
	if profile not in request.user.profile.friends.all():
		buttonStatus = 'not_friend'
		# if user is invited to friendlist
		if len(Friend_Request.objects.filter(
			from_user=request.user).filter(to_user=currentUser)) == 1:
				buttonStatus = 'friend_request_sent'
		# if user has sent request to friends
		if len(Friend_Request.objects.filter(
			from_user=profile.user).filter(to_user=request.user)) == 1:
				buttonStatus = 'friend_request_received'
	context = {
		'u': currentUser,
		'buttonStatus': buttonStatus,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': received_friend_requests,
		'post_count': userPosts.count
	}
	return render(request, "profile.html", context)

@login_required
def search_users(request):
	query = request.GET.get('q')
	objectList = User.objects.filter(username__icontains=query)
	context ={
		'users': objectList
	}
	return render(request, "search_users.html", context)
