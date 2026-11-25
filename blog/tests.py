"""Week 4 Day 3: drafts must never be visible to the public."""

from django.test import TestCase
from rest_framework.test import APIClient

from blog.models import Post


class PublishedOnlyTests(TestCase):
    def setUp(self):
        self.client = APIClient()  # no token: a member of the public
        Post.objects.create(
            title="Live post", slug="live-post", content="Hello.", status="published"
        )
        Post.objects.create(
            title="Secret draft", slug="secret-draft", content="Not yet.", status="draft"
        )

    def test_api_list_shows_only_published(self):
        response = self.client.get("/api/posts/")

        self.assertEqual(response.status_code, 200)
        slugs = [post["slug"] for post in response.data["results"]]
        self.assertEqual(slugs, ["live-post"])

    def test_api_detail_of_draft_is_404(self):
        response = self.client.get("/api/posts/secret-draft/")

        self.assertEqual(response.status_code, 404)  # not 403: don't confirm it exists

    def test_api_detail_of_published_is_200(self):
        response = self.client.get("/api/posts/live-post/")

        self.assertEqual(response.status_code, 200)

    def test_html_detail_of_draft_is_404(self):
        response = self.client.get("/blog/secret-draft/")

        self.assertEqual(response.status_code, 404)
