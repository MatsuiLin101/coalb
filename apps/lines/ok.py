995810 WebhookHandler get channel_secret =  cee5f9aa47f1c46beeb2c7b2016843fb
995829 Finish WebhookParser
995832 else message is None:
995836 event.__name__ =  MessageEvent
995840 message.__name__ =  TextMessage
996851 signature =  9HfFAukbCjkXadZi4/yRDWhOBwG5u0adpACO6YAuwAY=
996916 body =  {'events': [{'type': 'message', 'replyToken': 'a2532b7af384488db255fd7773829cf4', 'source': {'userId': 'U67b6f90a48a53c810fa42fecde71082c', 'type': 'user'}, 'timestamp': 1577069292203, 'mode': 'active', 'message': {'type': 'text', 'id': '11130128641673', 'text': 'ooo'}}], 'destination': 'Ua61523200cf13759b5c2c1a4ba9a7943'}
996920 body =  {"events":[{"type":"message","replyToken":"a2532b7af384488db255fd7773829cf4","source":{"userId":"U67b6f90a48a53c810fa42fecde71082c","type":"user"},"timestamp":1577069292203,"mode":"active","message":{"type":"text","id":"11130128641673","text":"ooo"}}],"destination":"Ua61523200cf13759b5c2c1a4ba9a7943"}
996937 signature =  9HfFAukbCjkXadZi4/yRDWhOBwG5u0adpACO6YAuwAY=
996938 BEFORE self.parser.parse
996948 BEFORE self.signature_validator.validate(body, signature):
997077 AFTER self.signature_validator.validate(body, signature):
997140 body_json =  {'events': [{'type': 'message', 'replyToken': 'a2532b7af384488db255fd7773829cf4', 'source': {'userId': 'U67b6f90a48a53c810fa42fecde71082c', 'type': 'user'}, 'timestamp': 1577069292203, 'mode': 'active', 'message': {'type': 'text', 'id': '11130128641673', 'text': 'ooo'}}], 'destination': 'Ua61523200cf13759b5c2c1a4ba9a7943'}
999084 events =  [{"message": {"id": "11130128641673", "text": "ooo", "type": "text"}, "replyToken": "a2532b7af384488db255fd7773829cf4", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577069292203, "type": "message"}]
999147 if as_payload:
999154 AFTER self.parser.parse
999197 payload =  <apps.lines.webhook.WebhookPayload object at 0x7fa7b0de8ef0>
999319 payload.events =  [{"message": {"id": "11130128641673", "text": "ooo", "type": "text"}, "replyToken": "a2532b7af384488db255fd7773829cf4", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577069292203, "type": "message"}]
999456 FOR event =  {"message": {"id": "11130128641673", "text": "ooo", "type": "text"}, "replyToken": "a2532b7af384488db255fd7773829cf4", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577069292203, "type": "message"}
999459 if 1
999461 event.__class__ =  <class 'linebot.models.events.MessageEvent'>
999467 event.message.__class__ =  <class 'linebot.models.messages.TextMessage'>
999471 else message is None:
999493 event.__name__ =  MessageEvent
999497 message.__name__ =  TextMessage
999531 key =  MessageEvent_TextMessage
999551 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0dee730>}
999570 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0dee730>}
999590 if 1 end, func =  <function handle_message at 0x7fa7b0dee730>
999598 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fa7b0dee730>}
999617 else
999728 else if 2
999839 event =  {"message": {"id": "11130128641673", "text": "ooo", "type": "text"}, "replyToken": "a2532b7af384488db255fd7773829cf4", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577069292203, "type": "message"}
2019-12-23T02:48:13.242101 if 2 end, func =  <function handle_message at 0x7fa7b0dee730>
2019-12-23T02:48:13.242159 handleer ok
2019-12-23T02:48:13.243752 10.111.154.51 - - [23/Dec/2019:02:48:13 +0000] "POST /lines/callback/ HTTP/1.1" 200 2 "-" "LineBotWebhook/1.0"
