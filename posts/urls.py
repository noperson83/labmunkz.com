from django.urls import include, path
from .views import post_like, post_detail, post_share

app_name = "posts"  # ✅ This should match the namespace

urlpatterns = [
    path('like/<int:post_id>/', post_like, name='post_like'),
    path('<int:post_id>/', post_detail, name='post_detail'),  # 🟢 View a post
    path('<int:post_id>/share/', post_share, name='post_share'),  # 🔄 Share a post
    #path('posts/', include('posts.urls', namespace='posts')),  # ✅ Correct namespace
]
