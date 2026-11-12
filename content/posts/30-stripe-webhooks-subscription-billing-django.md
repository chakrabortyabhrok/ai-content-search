---
title: Stripe Webhooks for Subscription Billing in Django
category: Billing
status: published
---
## Webhooks are the source of truth
A successful Checkout session or a customer portal change does not mean your database is up to date. The browser can close, the network can fail, or the user can abandon the flow. Stripe sends webhooks for the events that actually change a subscription. Your application should treat those events as the authoritative record and update its own tables only after verifying the webhook.

The endpoint must be fast and idempotent. Verify the signature, enqueue any heavy work, and return 200 quickly. Stripe retries on non-2xx responses, so a slow or failing handler creates duplicate deliveries that your code must tolerate.

## Verifying and routing events
Use Stripe’s library to verify the `Stripe-Signature` header against your webhook secret. Reject any request that fails verification. Once the event is trusted, switch on the event type. The events that matter most for subscriptions are `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, and `invoice.paid` or `invoice.payment_failed`.

Store the Stripe event id in a processed-events table. If the same id arrives again, return 200 immediately without re-applying the change. This makes retries safe.

```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if ProcessedEvent.objects.filter(event_id=event.id).exists():
        return HttpResponse(status=200)

    handle_event(event)  # enqueue or process
    ProcessedEvent.objects.create(event_id=event.id)
    return HttpResponse(status=200)
```

## Updating local subscription state
Inside the handler, load or create the local Subscription row using the Stripe customer id or subscription id as the key. Copy the status, current period end, price id, and cancel-at-period-end flag. Do this inside a transaction so a partial update cannot leave the row inconsistent.

When a subscription becomes active or past_due, update any feature flags or usage limits that depend on the plan. When it is canceled or unpaid, revoke access at the end of the paid period rather than immediately, unless your policy is stricter. Send the actual email or provisioning work to a background task so the webhook itself stays short.

## Testing and failure handling
Use the Stripe CLI to forward events to your local endpoint and to trigger specific event types. Write tests that post a fixture payload with a valid signature and assert that the local Subscription row changes as expected. Also test the duplicate-event path.

Log every handled event id and the resulting status. If a handler raises, the processed-event row should not be written so Stripe’s retry can succeed later. Alert on a growing number of failed events so you notice when a bug prevents updates.

## What good looks like
A customer can subscribe, upgrade, or cancel and the local database reflects the new status within seconds, even if the browser never returns to your site. Re-delivering the same webhook changes nothing. A failed payment moves the subscription to past_due and eventually restricts access according to your rules. If subscription status can diverge from Stripe, or if a retried webhook creates a second subscription row, the verification, idempotency check, or update logic needs another look.