---
title: Realtime Streaming Chat UI with React and Django
category: Frontend
status: published
---
## Why streaming feels different
A normal request waits until the whole answer is ready, then shows it at once. A streaming chat sends tokens as they are generated. The user sees the reply grow in place. That small change makes the interface feel faster even when the total time is the same.

Django can stream with a StreamingHttpResponse. React can consume the stream with the Fetch API and a reader. The two sides stay simple because neither tries to be a full websocket server. The connection is still a single HTTP request that stays open until the model finishes or the user stops it.

## What the backend sends
The Django view accepts the user’s message, starts the language-model call, and yields each token as soon as it arrives. Each chunk is a small JSON line or a plain text fragment followed by a newline. The response uses the text/event-stream content type so browsers treat it as a stream.

The view must not buffer the entire answer. It yields and flushes. If an error occurs mid-stream, it yields a final error event and closes. The client can then show a retry button instead of a half-finished message that never ends.

```python
def stream_chat(request):
    def token_stream():
        for token in call_model_streaming(request.POST["message"]):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingHttpResponse(token_stream(), content_type="text/event-stream")
```

## What the frontend does
The React component keeps the current assistant message in state. When the user sends a new message, it clears the previous assistant text and opens a fetch request with the streaming body. A reader pulls chunks as they arrive. Each chunk is decoded and appended to the message state, so the UI re-renders with the new text.

A stop button aborts the fetch. The reader loop ends, the partial text stays on screen, and the input becomes active again. No extra websocket or second connection is required.

## Keeping the UI stable
Only one stream should be active at a time. Starting a new message cancels the previous reader. The message list itself is an ordinary array of objects; streaming only mutates the last assistant entry. This keeps scrolling and markdown rendering simple. Code blocks and links inside the streamed text are rendered only after the stream ends, or with a lightweight incremental parser if partial highlighting is needed.

## What good looks like
The user types a question and sees the first words appear in under a second. The text continues to grow smoothly. Clicking stop freezes the reply exactly where it is and lets the user type again immediately. If the stream ever delivers the entire answer in one jump, or if a second message can start while the first is still arriving, the streaming boundary has been lost and needs to be restored.