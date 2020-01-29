from django.shortcuts import render, get_object_or_404, redirect

def strategic(request, project, text):
	context = {}
	return render(request, "strategic.html", context)