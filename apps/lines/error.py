827281 WebhookHandler get channel_secret =  cee5f9aa47f1c46beeb2c7b2016843fb
827310 Finish WebhookParser
827312 WebhookHandler ADD
827314 WebhookHandler ADD DECORATOR
827317 else message =  <class 'linebot.models.messages.TextMessage'>
827319 else message is None:
827321 event.__name__ =  MessageEvent
827327 message.__name__ =  TextMessage
828298 signature =  nxIj2ICDqHU1KAcqusGSL5nd0rGcxEibyxCSWySYuNk=
828414 body =  {'events': [{'replyToken': '00000000000000000000000000000000', 'type': 'message', 'timestamp': 1577070546017, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100001', 'type': 'text', 'text': 'Hello, world'}}, {'replyToken': 'ffffffffffffffffffffffffffffffff', 'type': 'message', 'timestamp': 1577070546017, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100002', 'type': 'sticker', 'packageId': '1', 'stickerId': '1'}}]}
828465 body =  {
828468   "events": [
828470     {
828472       "replyToken": "00000000000000000000000000000000",
828475       "type": "message",
828478       "timestamp": 1577070546017,
828480       "source": {
828482         "type": "user",
828484         "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"
828487       },
828489       "message": {
828492         "id": "100001",
828494         "type": "text",
828496         "text": "Hello, world"
828498       }
828500     },
828503     {
828505       "replyToken": "ffffffffffffffffffffffffffffffff",
828507       "type": "message",
828509       "timestamp": 1577070546017,
828511       "source": {
828513         "type": "user",
828515         "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"
828518       },
828520       "message": {
828522         "id": "100002",
828524         "type": "sticker",
828526         "packageId": "1",
828528         "stickerId": "1"
828530       }
828532     }
828534   ]
828536 }
828606
828661 signature =  nxIj2ICDqHU1KAcqusGSL5nd0rGcxEibyxCSWySYuNk=
828743 BEFORE self.parser.parse
828785 BEFORE self.signature_validator.validate(body, signature):
828933 AFTER self.signature_validator.validate(body, signature):
829008 body_json =  {'events': [{'replyToken': '00000000000000000000000000000000', 'type': 'message', 'timestamp': 1577070546017, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100001', 'type': 'text', 'text': 'Hello, world'}}, {'replyToken': 'ffffffffffffffffffffffffffffffff', 'type': 'message', 'timestamp': 1577070546017, 'source': {'type': 'user', 'userId': 'Udeadbeefdeadbeefdeadbeefdeadbeef'}, 'message': {'id': '100002', 'type': 'sticker', 'packageId': '1', 'stickerId': '1'}}]}
831459 events =  [{"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}, {"message": {"id": "100002", "packageId": "1", "stickerId": "1", "type": "sticker"}, "replyToken": "ffffffffffffffffffffffffffffffff", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}]
831508 if as_payload:
831555 AFTER self.parser.parse
831597 payload =  <apps.lines.webhook.WebhookPayload object at 0x7fdc1c0a6f98>
832133 payload.events =  [{"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}, {"message": {"id": "100002", "packageId": "1", "stickerId": "1", "type": "sticker"}, "replyToken": "ffffffffffffffffffffffffffffffff", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}]
832326 FOR event =  {"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}
832368 if 1
832414 event.__class__ =  <class 'linebot.models.events.MessageEvent'>
832458 event.message.__class__ =  <class 'linebot.models.messages.TextMessage'>
832498 else message is None:
832537 event.__name__ =  MessageEvent
832576 message.__name__ =  TextMessage
832612 key =  MessageEvent_TextMessage
832675 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0a8730>}
832738 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0a8730>}
832744 if 1 end, func =  <function handle_message at 0x7fdc1c0a8730>
832780 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0a8730>}
832785 else
832900 else if 2
833012 event =  {"message": {"id": "100001", "text": "Hello, world", "type": "text"}, "replyToken": "00000000000000000000000000000000", "source": {"type": "user", "userId": "Udeadbeefdeadbeefdeadbeefdeadbeef"}, "timestamp": 1577070546017, "type": "message"}
091382 heroku[router]: at=info method=POST path="/lines/callback/" host=coa-line-bot.herokuapp.com request_id=2bb19319-b2b0-4045-82c4-d3f9a8f9c3e2 fwd="203.104.156.74" dyno=web.1 connect=1ms service=413ms status=500 bytes=380 protocol=https
092100 10.47.238.174 - - [23/Dec/2019:03:09:07 +0000] "POST /lines/callback/ HTTP/1.1" 500 145 "-" "LINE-Developers/0.1"
