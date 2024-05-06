import json
import os
import random
import traceback
from pathlib import Path

import replicate
from dotenv import load_dotenv
from snips_nlu import SnipsNLUEngine

from machaao_utils import check_balance, get_details, get_recent

ban_words = ["nigger", "negro", "nazi", "faggot", "murder", "suicide"]

# list of banned input words
c = 'UTF-8'


def intent_classifier(text):
    parent = Path(__file__).parent.parent.absolute()
    path_to_engine = os.path.join(parent, "nlu", "engine", "base")
    # text = self.session.user_message
    loaded_engine = SnipsNLUEngine.from_path(path_to_engine)
    nlu_obj = loaded_engine.parse(text)
    intent = nlu_obj.get("intent")
    intent_name = intent.get("intentName")
    return intent_name


COST_PER_CREDIT_IN_MILLI_CENTS = os.environ.get('COST_PER_CREDIT_IN_MILLI_CENTS', 334)  # 1/299 -> 299 credits for $1
MIN_CREDITS_AWARD = os.environ.get("MIN_REWARD", 9)
MAX_CREDITS_AWARD = os.environ.get("MAX_REWARD", 15)


class BotLogic:
    def __init__(self, server_session_create_time):
        # Initializing Config Variables
        load_dotenv()

        self.api_token = os.environ.get("API_TOKEN")
        self.base_url = os.environ.get("BASE_URL", "https://ganglia.machaao.com")
        self.name = os.environ.get("NAME")
        self.limit = os.environ.get("LIMIT", 'True')
        self.server_session_create_time = server_session_create_time
        self.model = os.environ.get("MODEL_NAME")

    # noinspection DuplicatedCode
    @staticmethod
    def read_prompt(name):
        file_name = "./logic/prompt.txt"
        with open(file_name) as f:
            prompt = f.read()

        return prompt.replace("[name]", f"{name}")

    @staticmethod
    def parse(data):
        msg_type = data.get('type')
        if msg_type == "outgoing":
            msg_data = json.loads(data['message'])
            msg_data_2 = json.loads(msg_data['message']['data']['message'])

            if msg_data_2 and msg_data_2.get('text', ''):
                text_data = msg_data_2['text']
            elif msg_data_2 and msg_data_2['attachment'] and msg_data_2['attachment'].get('payload', '') and \
                    msg_data_2['attachment']['payload'].get('text', ''):
                text_data = msg_data_2['attachment']['payload']['text']
            else:
                text_data = ""
        else:
            msg_data = json.loads(data['incoming'])
            if msg_data['message_data']['text']:
                text_data = msg_data['message_data']['text']
            else:
                text_data = ""

        return msg_type, text_data

    def core(self, req: str, label: str, user_id: str, client: str, sdk: str, action_type: str, api_token: str):
        intent_name = intent_classifier(text=req)
        balance = check_balance(self.base_url, api_token, user_id)

        if intent_name == "balance":
            resp = f"Your current balance is {balance} Credits"
            resp_type = "balance"
            if client != "web":
                credit_reward = random.randint(MIN_CREDITS_AWARD, MAX_CREDITS_AWARD)
                resp_type = resp_type + "_" + credit_reward
            return False, resp, resp_type

        if balance <= 0:
            reply = "Oops, your credits are exhausted. Please top up your balance and try again."
            return False, reply, "text"

        print(
            "input text: " + req + ", label: " + label + ", user_id: " + user_id + ", client: " + client + ", sdk: " + sdk
            + ", action_type: " + action_type + ", api_token: " + api_token)

        bot = get_details(api_token, self.base_url)
        name = self.name

        if not bot:
            return False, "Oops, the chat bot doesn't exist or is not active at the moment", "text"
        else:
            name = bot.get("displayName", name)

        valid = True

        recent_text_data = get_recent(
            self.base_url, self.api_token,
            self.server_session_create_time,
            user_id)
        recent_convo_length = len(recent_text_data)

        print(f"len of history: {recent_convo_length}")

        banned = any(ele in req for ele in ban_words)

        messages = []

        if banned:
            print(f"banned input:" + str(req) + ", id: " + user_id)
            return False, "Oops, please refrain from such words", "text"

        for text in recent_text_data[::-1]:
            msg_type, text_data = self.parse(text)

            if text_data:
                e_message = "Oops," in text_data and "connect@machaao.com" in text_data

                if msg_type is not None and not e_message:
                    # outgoing msg - bot msg
                    messages.append(
                        assistant(text_data)
                    )
                else:
                    # incoming msg - user msg
                    messages.append(
                        user(text_data)
                    )

        try:
            reply = self.process_via_replicate(self.name, messages)
            return valid, reply, "text"
        except Exception as e:
            print(f"error - {e}, for {user_id}")
            print(traceback.format_exc())
            return False, "Oops, I am feeling a little overwhelmed with messages\nPlease message me later", "text"

    def process_via_replicate(self, name, user_messages):
        _prompt = self.read_prompt(name)

        messages = [system(_prompt), *user_messages]
        # print(messages)

        _prompt = chat_prompt_template(messages=messages)

        llm_input = {
            "prompt": _prompt
        }

        output = replicate.run(
            self.model, llm_input
        )

        resp = "".join(output)

        print(resp)

        return resp


def chat_prompt_template(
        messages
) -> str:
    history = []
    for message in messages:
        if message["role"] == "assistant":
            history.append(
                "<|start_header_id|>assistant<|end_header_id|>\n" +
                message["content"] +
                "<|eot_id|>"
            )
        elif message["role"] == "user":
            history.append(
                "<|start_header_id|>user<|end_header_id|>\n" +
                message["content"] +
                "<|eot_id|>"
            )
        elif message["role"] == "system":
            history.append(
                "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n" +
                message["content"] +
                "<|eot_id|>"
            )
        else:
            raise Exception("Unknown role")

    return "".join(history)


def assistant(content: str):
    return {"role": "assistant", "content": content}


def user(content: str):
    return {"role": "user", "content": content}


def system(content: str):
    return {"role": "system", "content": content}
