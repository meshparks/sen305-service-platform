from django.shortcuts import render

from django.shortcuts import render


def home(request):
    context = {
        "page_title": "Home",
        "headline": "Enterprise Service Request and Maintenance Platform",
        "summary": "Report faults, track maintenance work and follow every request to resolution.",
    }
    
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html", {"page_title": "About"})


def contact(request):
    return render(request, "core/contact.html", {"page_title": "Contact"})


def workflow(request):
    steps = ["Open", "Assigned", "In progress", "Resolved", "Closed"]
    return render(request, "core/workflow.html", {"page_title": "Workflow", "steps": steps})