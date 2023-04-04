import os
import re
import sys
import time
from threading import Thread

from revChatGPT.V3 import Chatbot
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
}

if os.getenv("OPENAI_ENGINE"):
    ChatGPTConfig["engine"] = os.getenv("OPENAI_ENGINE")

app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    token=os.getenv("SLACK_BOT_TOKEN"),
)
chatbot = Chatbot(**ChatGPTConfig)


@app.event("app_mention")
def event_test(event, say):
    prompt = re.sub("\\s<@[^, ]*|^<@[^, ]*", "", event["text"])
    try:
        response = chatbot.ask(prompt)
        user = event["user"]
        send = f"<@{user}> {response}"
    except Exception as e:
        print(e)
        print("{} (a {})".format(e, type(e)), file=sys.stderr)
        send = "(Mention) Exception was logged on service process, usually due to high demand (please retry)."

    # Get the `ts` value of the original message
    original_message_ts = event["ts"]

    # Use the `app.event` method to send a reply to the message thread
    say(send, thread_ts=original_message_ts)


@app.event("message")
def event_test(event, say):
    prompt = re.sub("\\s<@[^, ]*|^<@[^, ]*", "", event["text"])
    try:
        response = chatbot.ask(prompt)
        user = event["user"]
        send = response
    except Exception as e:
        print(e)
        print("{} (a {})".format(e, type(e)), file=sys.stderr)
        send = "(Message) Exception was logged on service process, usually due to high demand (please retry)."

    # reply message to new message
    say(send)


def chatgpt_refresh():
    while True:
        time.sleep(60)


if __name__ == "__main__":
    # Give a Slack App Token to trigger SocketMode
    if os.getenv("SLACK_APP_TOKEN"):
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        handler.start()
    else:
        thread = Thread(target=chatgpt_refresh)
        thread.start()
        app.start(os.getenv("PORT"))  # POST http://localhost:4000/slack/events
