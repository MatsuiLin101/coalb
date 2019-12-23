302818 WebhookHandler get channel_secret =  cee5f9aa47f1c46beeb2c7b2016843fb
302868 Finish WebhookParser
302871 else message is None:
302873 event.__name__ =  MessageEvent
302875 message.__name__ =  TextMessage
303778 signature =  9NT8jOZuH5RuLghB6YXIjIHxSUoyvHyiLpaN9xJY7bs=
303869 body =  {'events': [{'replyToken': '00000000000000000000000000000000', 'type': 'message', 'timestamp': 1577069271452, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100001', 'type': 'text', 'text': 'Hello, world'}}, {'replyToken': 'ffffffffffffffffffffffffffffffff', 'type': 'message', 'timestamp': 1577069271452, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100002', 'type': 'sticker', 'packageId': '1', 'stickerId': '1'}}]}
303876 body =  {
303878   "events": [
303879     {
303881       "replyToken": "00000000000000000000000000000000",
303882       "type": "message",
303884       "timestamp": 1577069271452,
303886       "source": {
303887         "type": "user",
303889         "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"
303890       },
303892       "message": {
303893         "id": "100001",
303894         "type": "text",
303896         "text": "Hello, world"
303897       }
303899     },
303900     {
303902       "replyToken": "ffffffffffffffffffffffffffffffff",
303903       "type": "message",
303905       "timestamp": 1577069271452,
303906       "source": {
303908         "type": "user",
303909         "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"
303910       },
303912       "message": {
303913         "id": "100002",
303914         "type": "sticker",
303916         "packageId": "1",
303917         "stickerId": "1"
303918       }
303920     }
303921   ]
303922 }
303924
303925 signature =  9NT8jOZuH5RuLghB6YXIjIHxSUoyvHyiLpaN9xJY7bs=
303927 BEFORE self.parser.parse
303930 BEFORE self.signature_validator.validate(body, signature):
303979 AFTER self.signature_validator.validate(body, signature):
304035 body_json =  {'events': [{'replyToken': '00000000000000000000000000000000', 'type': 'message', 'timestamp': 1577069271452, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100001', 'type': 'text', 'text': 'Hello, world'}}, {'replyToken': 'ffffffffffffffffffffffffffffffff', 'type': 'message', 'timestamp': 1577069271452, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100002', 'type': 'sticker', 'packageId': '1', 'stickerId': '1'}}]}
305383 events =  [{"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}, {"message": {"id": "100002", "packageId": "1", "stickerId": "1", "type": "sticker"}, "replyToken": "ffffffffffffffffffffffffffffffff", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}]
305390 if as_payload:
305392 AFTER self.parser.parse
305402 payload =  <apps.lines.webhook.WebhookPayload object at 0x7fa7b0de9f98>
305671 payload.events =  [{"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}, {"message": {"id": "100002", "packageId": "1", "stickerId": "1", "type": "sticker"}, "replyToken": "ffffffffffffffffffffffffffffffff", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}]
305756 FOR event =  {"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}
305758 if 1
305762 event.__class__ =  <class 'linebot.models.events.MessageEvent'>
305765 event.message.__class__ =  <class 'linebot.models.messages.TextMessage'>
305776 else message is None:
305779 event.__name__ =  MessageEvent
305790 message.__name__ =  TextMessage
305793 key =  MessageEvent_TextMessage
305819 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0df0730>}
305822 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0df0730>}
305833 if 1 end, func =  <function handle_message at 0x7fa7b0df0730>
305836 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0df0730>}
305846 else
305936 else if 2
306017 event =  {"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577069271452, "type": "message"}
646666+00:00 heroku[router]: at=info method=POST path="/lines/callback/" host=coa-line-bot.herokuapp.com request_id=9c4089db-3954-4d70-bd49-67d9e51b419a fwd="203.104.156.76" dyno=web.1 connect=1ms service=537ms status=500 bytes=380 protocol=https
647362 10.11.241.172 - - [23/Dec/2019:02:47:52 +0000] "POST /lines/callback/ HTTP/1.1" 500 145 "-" "LINE-Developers/0.1"
