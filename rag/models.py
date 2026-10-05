from django.db import models
from blog.models import Post


class Sentence(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # delete post: its chunks auto-delete
        related_name="sentences",  # lets write post.sentences.all()
    )
    para_index = models.IntegerField()  # which paragraph (0, 1, 2, ...)
    sent_index = models.IntegerField()  # which sentence in it (0, 1, 2, ...)
    text = models.TextField()  # the sentence itself : what we cite later
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
        return f"{self.post.title}: p{self.para_index}s{self.sent_index}"
