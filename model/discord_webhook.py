import requests
import json

class DiscordWebhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message_content, image_path=None):
        if image_path:
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': image_file
                }
                response = requests.post(self.webhook_url, files=files, data={'payload_json': json.dumps({"content": message_content})})
        else:
            message = {
                "content": message_content
            }
            response = requests.post(self.webhook_url, data=json.dumps(message), headers={"Content-Type": "application/json"})
        
        if response.status_code in [200, 204]:
            print("メッセージが正常に送信されました。")
        else:
            print(f"メッセージの送信に失敗しました。ステータスコード: {response.status_code}")
