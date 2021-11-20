from django import forms
from django.core import paginator
from django.db.models.query import QuerySet
from django.forms.fields import EmailField
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.views.generic.base import TemplateView
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import message, send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) #3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        #If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_list_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    #Recuperar articulo por id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        #Formulario enviado
        form = EmailField(request.POST)
        if form.is_valid():
            #Validacion correcta de campos del formulario
            cd = form.cleaned_data
            #... enviar email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])

            sent = True
        else:
            form = EmailField()
        return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent':sent})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish_year=year, publish_month=month, publish__day=day)

    #Lista de articulos activos para este articulo
    Comments = post.comments.filter(active=True)

    new_comments = None
    
    if request.method == 'POST':
        #Un comentario ha sido enviado
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #Crear un objeto Comment pero no se persiste en base de datos todavía
            new_comment = comment_form.save(commit=False)
            #Asociar el comentario al artículo
            new_comment.post = post
            #Guardar los datos en base de datos
            new_comment.save()
        else:
            comment_form = CommentForm()

        return render(request, 'blog/post/detail.html', {'comments': new_comment, 'comment_form': comment_form})