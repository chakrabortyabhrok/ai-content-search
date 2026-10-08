from django.db import models
from blog.models import Post


class Sentence(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # delete post: its chunks also deleted
        related_name="sentences",  # lets write post.sentences.all()
    )
    para_index = models.IntegerField()  
    sent_index = models.IntegerField()  
    text = models.TextField()  # the citation sentence itself
    section = models.CharField(max_length=200, blank=True)  # last heading above it
    is_code = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "para_index", "sent_index"],
                name="uniq_sentence_address",
            )
        ]
        ordering = ["para_index", "sent_index"]

    def __str__(self):
        return f"{self.post.title}: para:{self.para_index}se{self.sent_index}"
