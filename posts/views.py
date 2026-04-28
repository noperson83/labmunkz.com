from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Like

def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user.is_authenticated:
        like_filter = {'post': post, 'user': request.user}
    else:
        # ensure session exists
        if not request.session.session_key: 
            request.session.create()
        anon_id = request.session.session_key
        like_filter = {'post': post, 'anon_id': anon_id}

    like, created = Like.objects.get_or_create(**like_filter)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes': post.likes.count()
    })

def post_detail(request, post_id):
    """View a single post"""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {'post': post})

def post_share(request, post_id):
    """Share a post"""
    post = get_object_or_404(Post, id=post_id)
    # Example logic: Duplicate the post for the sharing user
    new_post = Post.objects.create(
        author=request.user,
        text=post.text,
        youtube_url=post.youtube_url,
        is_public=True
    )
    new_post.save()
    return redirect('posts:post_detail', post_id=new_post.id)
