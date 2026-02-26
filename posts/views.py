from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from .models import Post, Category, Like, Comment
from .forms import PostForm, CommentForm, ReplyForm


class PostListView(ListView):
    """Barcha chop etilgan postlar"""
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True
        ).select_related('author', 'category', 'author__profile').annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        )

        # Qidiruv
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(author__username__icontains=q)
            )

        # Kategoriya filtri
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Saralash
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'most_liked':
            queryset = queryset.order_by('-like_count')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__is_published=True))
        )
        context['featured_post'] = Post.objects.filter(
            is_published=True
        ).order_by('-views_count').first()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['current_category'] = self.request.GET.get('category', '')
        return context


class PostDetailView(DetailView):
    """Post tafsilotlari"""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(
            Post,
            slug=self.kwargs['slug'],
            is_published=True
        )
        # Ko'rishlar sonini oshirish (session orqali — har safar emas)
        session_key = f'viewed_post_{post.pk}'
        if not self.request.session.get(session_key):
            post.increment_views()
            self.request.session[session_key] = True
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        # Faqat root kommentlar (parent=None), replylar ichida ko'rsatiladi
        context['comments'] = post.comments.filter(
            is_active=True, parent=None
        ).select_related('author', 'author__profile').prefetch_related(
            'replies__author', 'replies__author__profile'
        )
        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm()
        context['is_liked'] = post.is_liked_by(user)
        context['like_count'] = post.get_like_count()
        context['comment_count'] = post.get_comment_count()

        # O'xshash postlar
        context['related_posts'] = Post.objects.filter(
            is_published=True,
            category=post.category
        ).exclude(pk=post.pk).select_related('author')[:3]

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post yaratish"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "✅ Post muvaffaqiyatli yaratildi!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Yangi post"
        context['submit_text'] = "Yaratish"
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Post tahrirlash — faqat muallif"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, "✅ Post yangilandi!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Postni tahrirlash"
        context['submit_text'] = "Saqlash"
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Post o'chirish — faqat muallif"""
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, "🗑️ Post o'chirildi.")
        return super().form_valid(form)


class CategoryPostsView(ListView):
    """Kategoriya bo'yicha postlar"""
    model = Post
    template_name = 'posts/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category, is_published=True
        ).select_related('author', 'author__profile').annotate(
            like_count=Count('likes')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def like_post(request, slug):
    """AJAX orqali like/unlike"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Faqat POST'}, status=405)

    post = get_object_or_404(Post, slug=slug, is_published=True)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'count': post.get_like_count()
    })


@login_required
def add_comment(request, slug):
    """Komment qo'shish"""
    if request.method != 'POST':
        return redirect('post_detail', slug=slug)

    post = get_object_or_404(Post, slug=slug, is_published=True)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post

        # Reply bo'lsa parent set
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=post)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                pass

        comment.save()
        messages.success(request, "💬 Izoh qo'shildi!")
    else:
        messages.error(request, "Izoh bo'sh bo'lmasligi kerak.")

    return redirect(reverse('post_detail', kwargs={'slug': slug}) + '#comments')


@login_required
def delete_comment(request, comment_id):
    """Komment o'chirish — faqat muallif yoki post muallifi"""
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.author or request.user == comment.post.author:
        post_slug = comment.post.slug
        comment.is_active = False
        comment.save()
        messages.success(request, "Izoh o'chirildi.")
        return redirect(reverse('post_detail', kwargs={'slug': post_slug}) + '#comments')

    messages.error(request, "Ruxsat yo'q.")
    return redirect('post_list')