import graphene
from .models import *
from framework.api.user import UserBasicObj
from django.db.models import F
from framework.api.APIException import APIException
from graphql_jwt.decorators import login_required


class CategoryObj(graphene.ObjectType):
    name = graphene.String()
    author = graphene.Field(UserBasicObj)

    def resolve_name(self, info):
        return self['name']

    def resolve_author(self, info):
        return User.objects.values().get(id=self['author_id'])


class TagObj(graphene.ObjectType):
    name = graphene.String()

    def resolve_name(self, info):
        return self['name']


class NewsObj(graphene.ObjectType):
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    author = graphene.Field(UserBasicObj)
    date = graphene.Date(required=True)
    category = graphene.Field(CategoryObj)
    tags = graphene.List(TagObj)
    pinned = graphene.Boolean()
    description = graphene.String(required=True)
    cover = graphene.String(required=True)

    def resolve_title(self, info):
        return self['title']

    def resolve_slug(self, info):
        return self['slug']

    def resolve_author(self, info):
        return User.objects.values().get(id=self['author_id'])

    def resolve_date(self, info):
        return self['date']

    def resolve_pinned(self, info):
        return self['pinned']

    def resolve_category(self, info):
        return Category.objects.values().get(id=self['category_id'])

    @graphene.resolve_only_args
    def resolve_tags(self):
        return News.objects.values().annotate(
            name=F('tags__name'),
        ).filter(id=self['id'])

    def resolve_cover(self, info):
        return self['cover']


class BlogObj(graphene.ObjectType):
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    author = graphene.Field(UserBasicObj)
    date = graphene.Date(required=True)
    tags = graphene.List(TagObj)
    draft = graphene.String(required=True)
    featured = graphene.Boolean()
    description = graphene.String(required=True)
    cover = graphene.String(required=True)
    category = graphene.Field(CategoryObj)

    def resolve_title(self, info):
        return self['title']

    def resolve_slug(self, info):
        return self['slug']

    def resolve_author(self, info):
        return User.objects.values().get(id=self['author_id'])

    def resolve_date(self, info):
        return self['date']

    @graphene.resolve_only_args
    def resolve_tags(self):
        return Blog.objects.values().annotate(
            name=F('tags__name'),
        ).filter(id=self['id'])

    def resolve_draft(self, info):
        return self['draft']

    def resolve_featured(self, info):
        return self['featured']

    def resolve_description(self, info):
        return self['description']

    def resolve_cover(self, info):
        return self['cover']

    def resolve_category(self, info):
        return Category.objects.values().get(id=self['category_id'])


class blogStatusObj(graphene.ObjectType):
    id = graphene.String()


class CreateBlog(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        slug = graphene.String(required=True)
        description = graphene.String(required=True)
        date = graphene.Date(required=True)
        draft = graphene.String(required=True)

    Output = blogStatusObj

    @login_required
    def mutate(self, info, title, slug, description, date, draft):
        blogs = Blog.objects.filter(title=title)
        if blogs.count() == 0:
            blog = Blog.objects.create(
                title=title,
                slug=slug,
                description=description,
                date=date,
                author=info.context.user,
                draft=draft,
                cover=info.context.FILES['cover']
            )
            blog.save()
            return blogStatusObj(id=blog.id)
        else:
            raise APIException('Blog already exists with same name',
                               code='BLOG_EXISTS')


class Query(graphene.ObjectType):
    news = graphene.List(NewsObj)
    getNews = graphene.Field(NewsObj, slug=graphene.String(required=True))
    tags = graphene.List(TagObj)
    categories = graphene.List(CategoryObj)
    blogs = graphene.List(BlogObj)
    blog = graphene.Field(BlogObj, slug=graphene.String(required=True))

    def resolve_news(self, info):
        return reversed(News.objects.values().all().order_by('date'))

    def resolve_getNews(self, info, **kwargs):
        slug = kwargs.get('slug')
        if slug is not None:
            return News.objects.values().get(slug=slug)
        else:
            raise APIException('Slug is required',
                               code='SLUG_IS_REQUIRED')

    def resolve_tags(self, info):
        return Tag.objects.values().all()

    def resolve_categories(self, info):
        return Category.objects.values().all()

    def resolve_blogs(self, info):
        return reversed(Blog.objects.values().all().order_by('date'))

    def resolve_blog(self, info, **kwargs):
        slug = kwargs.get('slug')
        if slug is not None:
            return Blog.objects.values().get(slug=slug)
        else:
            raise APIException('Slug is required',
                               code='SLUG_IS_REQUIRED')


class Mutation(graphene.ObjectType):
    createBlog = CreateBlog.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
