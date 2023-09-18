import random
from django.shortcuts import render
from markdown2 import Markdown
from . import util


def md_to_html(title):
    '''Returns converted HTML from the files' markdown contents'''
    md = util.get_entry(title)
    markdowner = Markdown()
    if md:
        return markdowner.convert(md)
    else:
        return None    
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
def entry(request, title):
    '''Displays page contents in html'''
    html = md_to_html(title)
    if html:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html
        })
    else:
        return render(request, "encyclopedia/error.html" , {
            "message": f"{title} Entry Does Not Exist"
        })

def search(request):
    if request.method == 'POST':
        entry_search = request.POST['q']
        html = md_to_html(entry_search)
        if html:
            return render(request, "encyclopedia/entry.html", {
                "title": entry_search,
                "content": html 
            })
        else:
            all_entries = util.list_entries()
            recommendation = []

            for entry in all_entries:
                if entry_search.lower() in entry.lower():
                    recommendation.append(entry)
            return render(request, "encyclopedia/search.html", {
                "recommendation": recommendation
            })

def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html")
    else:
        title = request.POST['title']
        content = request.POST['content']
        entry_exists = util.get_entry(title)
        if entry_exists:
            return render(request, "encyclopedia/error.html", {
                "message": f"{title} Page Already Exists"
            })
        else:
            util.save_entry(title, content)
            html = md_to_html(title)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": html,
            })

def edit(request):
    if request.method == "POST":
        title = request.POST['entry_title']
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
    
def save_edit(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        html = md_to_html(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html
        })
    
def random_page(request):
    all_entries = util.list_entries()
    random_entry = random.choice(all_entries)
    html = md_to_html(random_entry)
    return render(request, "encyclopedia/entry.html", {
       "title": random_entry,
       "content": html
    })