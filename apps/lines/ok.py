488485 WebhookHandler get channel_secret =  cee5f9aa47f1c46beeb2c7b2016843fb
488648 Finish WebhookParser
488763 WebhookHandler ADD
488799 WebhookHandler ADD DECORATOR
488850 else message =  <class 'linebot.models.messages.TextMessage'>
488899 else message is None:
488931 event.__name__ =  MessageEvent
488969 message.__name__ =  TextMessage
490579 signature =  DqKEyRVNYkghtBz8Ob5rjOD3t4HGixVQFjAulKvjS18=
490710 body =  {'events': [{'type': 'message', 'replyToken': '0e73e9ee3b724179bc9632d8f8b02444', 'source': {'userId': 'U67b6f90a48a53c810fa42fecde71082c', 'type': 'user'}, 'timestamp': 1577070601431, 'mode': 'active', 'message': {'type': 'text', 'id': '11130221656410', 'text': 'fff'}}], 'destination': 'Ua61523200cf13759b5c2c1a4ba9a7943'}
490766 body =  {"events":[{"type":"message","replyToken":"0e73e9ee3b724179bc9632d8f8b02444","source":{"userId":"U67b6f90a48a53c810fa42fecde71082c","type":"user"},"timestamp":1577070601431,"mode":"active","message":{"type":"text","id":"11130221656410","text":"fff"}}],"destination":"Ua61523200cf13759b5c2c1a4ba9a7943"}
490814 signature =  DqKEyRVNYkghtBz8Ob5rjOD3t4HGixVQFjAulKvjS18=
490848 BEFORE self.parser.parse
490879 BEFORE self.signature_validator.validate(body, signature):
491151 AFTER self.signature_validator.validate(body, signature):
491244 body_json =  {'events': [{'type': 'message', 'replyToken': '0e73e9ee3b724179bc9632d8f8b02444', 'source': {'userId': 'U67b6f90a48a53c810fa42fecde71082c', 'type': 'user'}, 'timestamp': 1577070601431, 'mode': 'active', 'message': {'type': 'text', 'id': '11130221656410', 'text': 'fff'}}], 'destination': 'Ua61523200cf13759b5c2c1a4ba9a7943'}
492930 events =  [{"message": {"id": "11130221656410", "text": "fff", "type": "text"}, "replyToken": "0e73e9ee3b724179bc9632d8f8b02444", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577070601431, "type": "message"}]
492975 if as_payload:
493014 AFTER self.parser.parse
493129 payload =  <apps.lines.webhook.WebhookPayload object at 0x7fdc1c0a7e48>
493568 payload.events =  [{"message": {"id": "11130221656410", "text": "fff", "type": "text"}, "replyToken": "0e73e9ee3b724179bc9632d8f8b02444", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577070601431, "type": "message"}]
497342 FOR event =  {"message": {"id": "11130221656410", "text": "fff", "type": "text"}, "replyToken": "0e73e9ee3b724179bc9632d8f8b02444", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577070601431, "type": "message"}
497401 if 1
497444 event.__class__ =  <class 'linebot.models.events.MessageEvent'>
497483 event.message.__class__ =  <class 'linebot.models.messages.TextMessage'>
497562 else message is None:
497600 event.__name__ =  MessageEvent
497638 message.__name__ =  TextMessage
497677 key =  MessageEvent_TextMessage
497756 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0ac730>}
497805 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0ac730>}
497845 if 1 end, func =  <function handle_message at 0x7fdc1c0ac730>
497925 self._handlers =  {'MessageEvent_TextMessage': <function handle_message at 0x7fdc1c0ac730>}
497960 else
498161 else if 2
498411 event =  {"message": {"id": "11130221656410", "text": "fff", "type": "text"}, "replyToken": "0e73e9ee3b724179bc9632d8f8b02444", "source": {"type": "user", "userId": "U67b6f90a48a53c810fa42fecde71082c"}, "timestamp": 1577070601431, "type": "message"}
750166+00:00 heroku[router]: at=info method=POST path="/lines/callback/" host=coa-line-bot.herokuapp.com request_id=fffbc4e4-dc26-41ad-a101-1dd32fdf10f7 fwd="147.92.150.195" dyno=web.1 connect=1ms service=591ms status=200 bytes=217 protocol=https
747479 if 2 end, func =  <function handle_message at 0x7fdc1c0ac730>
747892 handleer ok
750717 10.150.193.19 - - [23/Dec/2019:03:10:02 +0000] "POST /lines/callback/ HTTP/1.1" 200 2 "-" "LineBotWebhook/1.0"
