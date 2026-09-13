from django.db import models
from django.utils.text import slugify
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
class Author(models.Model):
    name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Author"
        ordering = ["name"]


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class Post(models.Model):
    title = models.CharField(max_length=200, help_text="Blog post title")
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField()
    content = models.TextField()

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts", null=True, blank=True
    )

    published_date = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(
        Tag,
        null=True,
        blank=True
    )

    def __str__(self):

        return self.title

    class Meta:
        ordering = ["-published_date"]
