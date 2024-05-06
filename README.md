## A Pay as You Go Meta-Llama-3 AI Chatbot Template ##
Use this template to rapidly build and monetize a [Meta Llama 3](https://huggingface.co/meta-llama) AI chatbot and start earning with your Custom AI Chatbot

## Requirements for running it locally on laptop ##
* Windows / Mac / Linux with Git installed
* Python 3.8
* Ngrok for Tunneling (For Local Laptop Development Environment)
* Desktop / Laptop with a minimum of 16GB RAM
* Replicate API token - Get one [here](https://replicate.com/meta/meta-llama-3-8b-instruct/api)
* MessengerX API Token - Follow the instructions below to get your token

## Get MessengerX.io API Key ##
* Available on the [MessengerX.io](https://portal.messengerx.io/index#!/dashboard) portal
* If you aren't registered, please create an account and login
* Set up your new bot by providing it a `Character Name` and `Description`. 
  * Select `Custom Bot` option
  * It should look something like this:
  * ![figure](https://github.com/machaao/machaao-py/raw/master/images/bot_setup.png?raw=true)
* Click on `Save`. It will redirect you to your dashboard.
* On your dashboard you can see your newly created bot
  * ![figure](https://github.com/machaao/machaao-py/raw/master/images/new_bot.png?raw=true)
* Click on `Settings` tab. It will open your bot configuration page.
  * ![figure](https://github.com/machaao/machaao-py/raw/master/images/bot_config.png?raw=true)
* On the configuration page you'd be able to see a string named `token`. That's your `Machaao API Token`

## Local Setup ##
### Download or clone this repository ###
```
git clone https://github.com/machaao/llama3-chatbot.git

cd llama3-chatbot
```

### Install requirements ###
```bash
pip install -r requirements.txt
```

### Create a new .env file in the gpt-j-chatbot directory ###
```bash
nano -w .env
```
Put these key-value pairs in your .env file
```
API_TOKEN=<Machaao API Token>
BASE_URL=https://ganglia.machaao.com
NAME=Jess
REPLICATE_API_TOKEN=<YOUR REPLICATE API TOKEN> 
MODEL_NAME=meta/meta-llama-3-8b-instruct
CREDIT=5
```

Get your replicate api token [here](https://replicate.com/meta/meta-llama-3-8b-instruct/api)

### Change ```CREDIT``` variable to change the cost of a text message ###
```
CREDIT=5 implies one message should consume 5 credits
Each virtual credit amounts to ~$0.0035 USD
```

### Modify logic/prompt.txt to change the system prompt ###
```
You are a helpful assistant named [name]
```

### Modify the core() function in logic/bot_logic.py to personalize responses ###
```
def core(self, req: str, user_id: str):
```
* Refer to [platform documentation](https://messengerx.rtfd.io) for personalization options

### Run the chatbot server from the root directory of the repo ###
```
python app.py
```

### Start ngrok.io tunnel ###
```
ngrok http 5000
```
* You'll get a `Forwarding` URL mentioned on the console as shown below
  * ![figure](https://github.com/machaao/machaao-py/raw/master/images/ngrok_console.png?raw=true)
* Copy the `Forwarding` URL. In this example it would be:
```
https://26ea-150-107-177-46.ngrok-free.app
```

### Update your webhook ###
Update your bot `Webhook URL` on the bot configuration page with the NGROK `Forwarding URL`<br/>
In this example your Webhook URL would be:
```
https://26ea-150-107-177-46.ngrok-free.app/machaao/hook
```
Refer to this screenshot below
![figure](https://github.com/machaao/machaao-py/raw/master/images/update_hook.png?raw=true)

### Test your bot:
Click on `Preview` to chat with your bot

  
### Get Dashbot.io API KEY (Recommended for Production) ###
* You can acquire the API Key via [Dashbot.io](https://dashbot.io) and replace it in the ```.env``` file under the entry
```DASHBOT_KEY```

## Remote Setup (Heroku) ##

We are assuming you have access to a [heroku account](https://heroku.com)
and have installed heroku command line client for your OS.

### Login to Heroku ###
```
heroku login
```

### Create a new app on Heroku and note down your heroku app name
```
heroku create
```

### Commit changes and push the repository to Heroku ###
```
git commit -m ".env updated"
git push heroku master
```

### Open the logs to confirm successful Deployment ###
```
heroku logs --tail
```

### Update your webhook ###
Update your bot Webhook URL at [MessengerX.io Portal](https://portal.messengerx.io) with the heroku app url
```
Webhook Url: <YOUR-HEROKU-APP-URL>/machaao/hook
```

### Test your bot:
Visit: ```https://messengerx.io/<your-character-name>```

## Notes / Additional Resources ##
* Please note that this document isn't meant to be used as a guide for production environment setup.