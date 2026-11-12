---
title: Hardening the Django Admin with Custom Permissions
category: Security
status: published
---
## The admin is a high-value target
The Django admin gives staff users powerful access. Default permissions are coarse: a user who can change posts can often change any post, and a user who can view the admin can sometimes reach models they should not see. Hardening means narrowing those rights and adding checks that the built-in flags do not cover.

Start by creating groups that match real roles: author, editor, admin. Assign only the permissions each role needs. Remove the default “add”, “change”, and “delete” permissions from models that should be managed through custom actions instead of the generic admin forms.

## Object-level checks
Model-level permissions are not enough when authors should edit only their own posts. Override `has_change_permission` and `has_delete_permission` on the ModelAdmin. Inside those methods, allow the action only when the object’s author matches the current user, or when the user is in an editors group.

The same pattern applies to list views. Override `get_queryset` so non-editors see only their own rows. This prevents an author from discovering other drafts through the admin changelist.

```python
class PostAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.groups.filter(name="editors").exists():
            return True
        return obj.author_id == request.user.id

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="editors").exists():
            return qs
        return qs.filter(author=request.user)
```

## Custom admin actions and read-only fields
Replace broad “delete selected” actions with narrower ones. An editor might be allowed to publish a batch of posts but not to delete them. Define the action, check the user’s group inside it, and register it only for the appropriate ModelAdmin.

Mark sensitive fields read-only for lower roles. An author can edit the body but not the publication date or the featured flag. Use `get_readonly_fields` to return different lists based on the user’s groups. This keeps the form simple while still enforcing the rule on the server.

## Audit and session hygiene
Log important admin actions. A simple signal or an overridden `save_model` can record who changed a post’s status and when. Store the log in an ordinary model so it can be reviewed later without external services.

Shorten the admin session cookie age and require re-authentication for sensitive actions if your threat model needs it. Ensure the admin is served only over HTTPS and that its URL is not the default `/admin/`. These steps do not replace permission checks, but they reduce the chance that a stolen session cookie remains useful for long.

## What good looks like
An author logging into the admin sees only their own drafts and published posts. Attempting to open another author’s change page returns a permission error. An editor can publish or unpublish any post but cannot delete users or change site settings. Every status change leaves a row in the audit log. If a staff user can still reach a model or an object outside their role, the ModelAdmin permission methods or the group assignments need to be tightened.