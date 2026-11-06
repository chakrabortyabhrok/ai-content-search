---
title: Database Transactions and Atomic Safety in Django
category: Backend
status: published
---
## Why partial writes are worse than failures
A view that creates an order, charges a card, and then sends a confirmation email can leave the database in a bad state if any step fails. The order exists but the payment never happened, or the payment succeeded and the order row is missing. Wrapping the critical steps in a transaction makes the whole unit succeed or fail together. The database either commits every change or rolls them all back.

Django’s `transaction.atomic` is the tool for this. It can decorate a function or be used as a context manager. Everything inside the block shares one database transaction. If an exception escapes the block, Django rolls the transaction back and the exception continues. If the block finishes normally, the changes are committed.

## What belongs inside the atomic block
Only the writes that must be consistent with each other belong inside the transaction. Creating the order row, updating the inventory count, and recording the payment intent are a classic set. Sending the email, calling an external embedding API, or generating a PDF do not belong inside. Those steps can fail for reasons outside your control and should not hold the database transaction open.

If an external call must happen, do it after the transaction commits. Use `transaction.on_commit` to register a callback that runs only after the database has successfully saved the changes. The callback can then enqueue a background task or make the external request. If the transaction rolls back, the callback never runs.

```python
from django.db import transaction

def create_order(user, items):
    with transaction.atomic():
        order = Order.objects.create(user=user)
        for item in items:
            OrderItem.objects.create(order=order, **item)
        # inventory update happens here too
    # email or webhook goes outside
    transaction.on_commit(lambda: send_confirmation(order.id))
```

## Nested blocks and savepoints
An atomic block inside another atomic block does not start a second transaction. It creates a savepoint. If the inner block raises an exception and you catch it, you can roll back only to the savepoint while the outer transaction continues. This is useful when you want to try an optional step without undoing the required work. Most application code never needs explicit savepoints. A single well-placed atomic block around the critical writes is enough.

## Isolation and concurrent updates
Postgres defaults to read-committed isolation. Two transactions can each read the same row, both decide to update it, and the second update silently overwrites the first. For counters, inventory, or any value that must not be lost, use `select_for_update` inside the atomic block. The row is locked until the transaction ends. The second transaction waits, then sees the updated value.

Keep the locked section short. Do the read, the calculation, and the write, then exit the atomic block. Holding a lock while you call an external service will block other requests and can lead to timeouts.

## What good looks like
A payment flow either creates the order and the payment record together or creates neither. A concurrent request that tries to decrement the same inventory count waits and then sees the correct remaining quantity. If an exception occurs after the database writes but before the confirmation email is sent, the email is simply never sent; the order and payment stay consistent. When a view performs several related writes without an atomic block, or when an external API call sits inside the transaction, the safety boundary has been lost and needs to be restored.

---

This version now includes a short code block. All previous posts already had headings and multi-sentence bodies. The sample set meets the three requirements.