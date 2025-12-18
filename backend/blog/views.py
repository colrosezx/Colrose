from django.shortcuts import render, get_object_or_404
from .models import Post

def main_page(request):
    latest_posts = Post.objects.order_by('-pub_date')[:3]
    return render(request, 'index.html', {'latest_posts': latest_posts})

def post_list(request):
    posts = Post.objects.order_by('-pub_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})