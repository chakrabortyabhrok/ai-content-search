---
title: Clean Architecture and Service Layers in Django
category: Architecture
status: published
---
## Views should stay thin
A Django view that contains business rules becomes hard to test and hard to reuse. The view’s job is to validate input, call one service function, and turn the result into a response. All decisions about what may happen live in the service layer.

This split also makes background tasks simple. The same service function that a view calls can be called by a worker. No logic is copied, and no HTTP request object leaks into the domain code.

## What a service layer owns
A service module holds the use-case functions: create a post, re-index a post, change a subscription, record a payment. Each function receives plain Python objects or primary keys, performs the work inside a transaction when needed, and returns a simple result or raises a domain exception.

Models stay responsible for their own invariants. A Post model can enforce that a published post has a title. The service decides when to publish and which other objects must be updated at the same time. Queries that are used in more than one place move into custom managers or querysets so they are not repeated inside services.

```python
# services/posts.py
from django.db import transaction
from .models import Post

def publish_post(post_id, user):
    with transaction.atomic():
        post = Post.objects.select_for_update().get(id=post_id)
        if post.author_id != user.id:
            raise PermissionError("Not the author")
        post.status = "published"
        post.save(update_fields=["status"])
    return post
```

## Dependencies point inward
Service functions may import models and other services. Views and serializers may import services. Models and services do not import views, serializers, or request objects. This keeps the core testable with plain pytest and a database fixture; no HTTP client is required.

External systems (email, payment providers, embedding APIs) are called from the service layer or from a thin adapter module. The service receives the adapter as an argument or imports a single function. Tests can replace that function with a fake that records calls.

## Testing and growth
Service tests cover the business rules: what happens on success, what happens when the user lacks permission, what happens when a related object is missing. View tests only check status codes, response shapes, and that the correct service was called. When a rule changes, only the service test and the service implementation need to be updated.

As the project grows, a service module that exceeds a few hundred lines can be split by use case. The public functions stay the same, so views and workers do not change. The boundary remains the service layer, not a new set of microservices.

## What good looks like
A new feature can be fully tested by calling service functions directly. The same function is used by both the API view and the background worker. Changing a business rule requires edits in one module. If a view contains conditional logic about payments or permissions, or if a model method starts sending email, the responsibilities have blurred and need to be moved back into the service layer.