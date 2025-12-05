from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Blog,Comment,Category
from accounts.models import User
from .forms import BlogForm,CommentForm,CategoryForm,BlogFileAttachmentForm,BlogCoverImageForm

# Create your views here.

class BlogCreateView(LoginRequiredMixin,CreateView):
    template_name = 'blog/create.html'
    form_class = BlogForm

    success_message = "Blog was created successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def get_context_data(self, **kwargs):
        context = super(BlogCreateView, self).get_context_data(**kwargs)
        form_attachment = BlogFileAttachmentForm(prefix='form_attachment')
        form_coverimage = BlogCoverImageForm(prefix='form_coverimage')
        context['form_attachment'] = form_attachment
        context['form_coverimage'] = form_coverimage
        context['blog_menu'] = 'active'
        return context


@login_required()
def add_blog_post(request):
    form = BlogForm(request.POST)
    if form.is_valid():
        blog = form.save(commit=False)
        blog.author = request.user
        blog.article = request.POST['article']
        if request.POST['link'] != '':
            blog.link = request.POST['link']

        blog.save()

        messages.success(request,"Successfully added blog post")

        if 'form_coverimage-cover_image' in request.FILES:
            mycoverpagefile = request.FILES['form_coverimage-cover_image']
            ext_coverimage = mycoverpagefile.name.split('.')[-1]
            if ext_coverimage == 'img' or ext_coverimage == 'IMG' or ext_coverimage == 'PNG' or ext_coverimage == 'png' or ext_coverimage == 'JPG' or ext_coverimage == 'jpg' or ext_coverimage == 'JPEG' or ext_coverimage == 'jpeg':
                form_coverimage = BlogCoverImageForm(request.POST, request.FILES,instance=blog,prefix='form_coverimage')
                if form_coverimage.is_valid():
                    form_coverimage.save()
                    messages.success(request,'Successfully added Cover Image')
                else:
                    messages.warning(request,form_coverimage.errors)

        if 'form_attachment-file_attachment' in request.FILES:
            myfileattachment = request.FILES['form_attachment-file_attachment']
            if ext == 'pdf' or ext == 'PDF':
                form_attachment = BlogFileAttachmentForm(request.POST, request.FILES,instance=blog,prefix='form_attachment')
                if form_attachment.is_valid():
                    form_attachment.save()
                    messages.success(request,'Successfully added File Attachment')
                else:
                    messages.warning(request,form_attachment.errors)

    else:
        messages.warning(request,form.errors)

    return redirect('psycad:blog_list')

@login_required()
def blog_edit(request,pk):

    if request.method == 'GET':
        blog_instance = Blog.objects.get(id=pk)
        categories = Category.objects.all()
        form_attachment = BlogFileAttachmentForm(prefix='form_attachment')
        form_coverimage = BlogCoverImageForm(prefix='form_coverimage')
        return render(request,'blog/edit.html',{'blog':blog_instance,'form_attachment':form_attachment,'form_coverimage':form_coverimage,'categories':categories})

    elif request.method == 'POST':
        blog_instance = Blog.objects.get(id=pk)
        form = BlogForm(request.POST,instance=blog_instance)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.article = request.POST['article']
            if request.POST['link'] != '':
                blog.link = request.POST['link']
            blog.save()

            if 'form_coverimage-cover_image' in request.FILES:
                mycoverpagefile = request.FILES['form_coverimage-cover_image']
                ext_coverimage = mycoverpagefile.name.split('.')[-1]
                if ext_coverimage == 'img' or ext_coverimage == 'IMG' or ext_coverimage == 'PNG' or ext_coverimage == 'png' or ext_coverimage == 'JPG' or ext_coverimage == 'jpg' or ext_coverimage == 'JPEG' or ext_coverimage == 'jpeg':
                    form_coverimage = BlogCoverImageForm(request.POST, request.FILES,instance=blog_instance,prefix='form_coverimage')
                    if form_coverimage.is_valid():
                        form_coverimage.save()
                        messages.success(request,'Successfully added Cover Image')
                    else:
                        messages.warning(request,form_coverimage.errors)

            if 'form_attachment-file_attachment' in request.FILES:
                myfileattachment = request.FILES['form_attachment-file_attachment']
                if ext == 'pdf' or ext == 'PDF':
                    form_attachment = BlogFileAttachmentForm(request.POST, request.FILES,instance=blog_instance,prefix='form_attachment')
                    if form_attachment.is_valid():
                        form_attachment.save()
                        messages.success(request,'Successfully added File Attachment')
                    else:
                        messages.warning(request,form_attachment.errors)

            return redirect('psycad:blog_list')

        else:
            messages.warning(request,form.errors)
            categories = Category.objects.all()
            form_attachment = BlogFileAttachmentForm(prefix='form_attachment')
            form_coverimage = BlogCoverImageForm(prefix='form_coverimage')
            return render(request,'blog/edit.html',{'blog':blog_instance,'form_attachment':form_attachment,'form_coverimage':form_coverimage,'categories':categories})


@login_required()
def blog_add_coverimage(request,pk):
    blog_instance = Blog.objects.get(id=pk)
    mycoverimagefile = request.FILES['cover_image']
    ext_coverimage = mycoverimagefile.name.split('.')[-1]
    if ext_coverimage == 'img' or ext_coverimage == 'IMG' or ext_coverimage == 'PNG' or ext_coverimage == 'png' or ext_coverimage == 'JPG' or ext_coverimage == 'jpg' or ext_coverimage == 'JPEG' or ext_coverimage == 'jpeg':
        form_coverimage = BlogCoverImageForm(request.POST, request.FILES,instance=blog_instance)
        if form_coverimage.is_valid():
            form_coverimage.save()
            messages.success(request,'Successfully added Cover Image')
        else:
            messages.warning(request,form_coverimage.errors)

    return redirect('psycad:blog_list')

@login_required()
def delete_blog_post(request,pk):
    try:
        blog_instance = Blog.objects.get(id=pk)
        blog_instance.delete()
        messages.success(request,'Successfully deleted blog post')
    except:
        messages.warning(request,'An error occurred, please try again')

    return redirect('psycad:blog_list')

@login_required()
def blog_publish(request,pk):
    try:
        blog_instance = Blog.objects.get(id=pk)
        if blog_instance.publish == 'Yes':
            blog_instance.publish = 'No'
            blog_instance.save()
            messages.success(request,'Successfully unpublsihed article')
        else:
            blog_instance.publish = 'Yes'
            blog_instance.save()
            messages.success(request,'Successfully publsihed article')
    except:
        messages.warning(request,'An error has occurred, please try again')

    return redirect('psycad:blog_list')


class BlogListView(LoginRequiredMixin,ListView):
    template_name = 'blog/list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Blog.objects.all().select_related('author')

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        context['blog_menu'] = 'active'
        return context

class BlogStudentListView(LoginRequiredMixin,ListView):
    template_name = 'blog/list_student.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Blog.objects.filter(publish__exact='Yes').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super(BlogStudentListView, self).get_context_data(**kwargs)
        context['blog_menu'] = 'active'
        return context


@login_required()
def blog_categories(request):
    categories = Category.objects.all()
    form = CategoryForm()
    return render(request,'blog/categories.html',{'categories':categories,'form':form})

@login_required()
def add_blogcategory(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully added a category')
    else:
        messages.warning(request, form.errors)

    return redirect('psycad:config_blog_categories')

@login_required()
def edit_blogcategory(request,pk):
    category_instance = Category.objects.get(id=pk)
    form = CategoryForm(request.POST,instance=category_instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully edited category')
    else:
        messages.warning(request, form.errors)

    return redirect('psycad:config_blog_categories')

@login_required()
def delete_blogcategory(request,pk):
    try:
        category_instance = Category.objects.get(id=pk)
        category_instance.delete()
        messages.success(request, 'Successfully deleted category')
    except :
        messages.warning(request, 'An error occurred, please try again later')

    return redirect('psycad:config_blog_categories')

@login_required()
def blog_general_view(request,pk):
    blog = Blog.objects.get(id=pk)
    return render(request,'blog/blog_view.html',{'article':blog,'blog_menu':'active'})

@login_required()
def blog_view_addcomment(request,pk):
    blog_instance = Blog.objects.get(id=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.blog = blog_instance
        comment.save()
        messages.success(request,'Comment sent for review, once approved, it will be added to the comment list')
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 6:
        return redirect('student:blog_view',pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:blog_view',pk=pk)


@login_required()
def update_comment_status(request,pk):
    try:
        comment_instance = Comment.objects.get(id=pk)
        if comment_instance.published == 'Yes':
            comment_instance.published = 'No'
            comment_instance.save()
        else:
            comment_instance.published = 'Yes'
            comment_instance.save()
        messages.success(request,'Successfully updated comment status')
    except:
        messages.warning(request,'An error occurred, please try again later')

    return redirect('psycad:blog_list')

@login_required()
def blog_view(request,pk):
    blog = Blog.objects.get(id=pk)
    return render(request,'blog/blog_view_gre.html',{'article':blog,'blog_menu':'active'})
