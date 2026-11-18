# Transcript message shape (v0.0.5)

One **message** = one send as it appeared in iMessage (after scroll-merge of the same bubble).  
**authors** in a thread: `operator` (blue, right) and the contact slug (e.g. `justin`, gray, left).

Report labels:

- `operator` / `justin` — primary voice: exposition and **answers** inside a self-Q&A send
- `operator (interlocutor)` — **question / probe** lines (`interlocutions[]` anchors); the interlocutor interrupts with framed questions
- `justin (interlocutor)` — same pattern if a contact self-interlocutes in one gray bubble (unusual)

See Cursor rule `self-interlocution.mdc` for interlocutor vs dialog vs pedagogical self-interlocution.

## Example (one `transcript.jsonl` line)

```json
{
  "record_type": "message",
  "message_id": 12,
  "author": "operator",
  "text": "The war also proved (again) that price is independent of supply and demand. That model only works in the context of scarcity. No one drove less.\n\nWhat does that mean?\n\nIt means that we were above the level of utter collapse of petroleum resource management system as a global community.\n\nWhere did the oils come from?\n\nMuch of it was exported from the Gulf of America. China and Russia were the ones more dependent on Iranian petroleum.\n\nWhy did prices go up?\n\nPrice is a separate phenomenon than supply. US petroleum becoming a larger global supplier would suggest lower import cost thus lower prices in US. If the price of US-extracted petroleum is more expensive than Iranian-extracted then we establish than price is not a framed measure regarding the war; there is no 'unit price'. The US and Israel righteously attacked Iran. Then. The price of petroleum increased.\n\nThat's not an answer and 'then' cannot be a standalone sentence. Why are you abandoning grammar and reason?\n\nThe safest thing to do is *observe*. Proximity and order are not causation. Supply and demand is the base model. It is correct. Then. It is not correct. The dot com boom led to a rush of investment in infrastructure for the World Wide Web. The companies who built the infrastructure across the Atlantic were vested with the ability to build. Then. That vestment was considered over leveraged. Then. The companies defaulted on debt. Then. The market 'crashed'. Then. The infrastructure was effectively auctioned at cost. Now. Sending data packets across the Atlantic is simply a network hop. It is essentially free.\n\nOk so you read Friedman. What does that mean about data centers and Amazon?\n\nIt means wait to see if the Democrats win Congress as I said. A change in policy will likely lead to a similar phenomenon where infrastructure growth horizon is retarded then valuation of infrastructure companies drops then mega corporations like Amazon sell their data centers to mitigate loss while data center companies default and liquidate then transformers will be cheap then it will just be matrix multiplication.\n\nIs that ok?\n\nIt is fine. It's how humanity overcomes infrastructure hurdles historically. World wars work too.",
  "interlocutions": [
    {"question": "What does that mean?", "line": 5},
    {"question": "Where did the oils come from?", "line": 9},
    {"question": "Why did prices go up?", "line": 13},
    {"question": "That's not an answer and 'then' cannot be a standalone sentence. Why are you abandoning grammar and reason?", "line": 17},
    {"question": "Ok so you read Friedman. What does that mean about data centers and Amazon?", "line": 21},
    {"question": "Is that ok?", "line": 25}
  ],
  "source_image_index": 4,
  "bubble_side": "right"
}
```

`text` is **complete, verbatim, as sent**, including internal Q&A and the closing “It is fine…” paragraph (still **operator**, not Justin).

`interlocutions` are **pointers into `text`** for report styling only; they do not split the message on disk. Each anchor is a line of **interlocution** (the interlocutor’s question).
