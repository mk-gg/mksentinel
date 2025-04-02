# MkSentinel

### Tech Stack:
- Backend: Python, Flask, Supabase, PostgreSQL  (database)
- Frontend: React, Typescript, Taildwind CSS, ShadcnUi
- Auth: OAuth2

### Features:
- 🔨 Admin functionality
- 🔒 OAuth2 Authentication
- 🏦 Simple cog system
- 🔍 Identifies and flags potential scam attempt and malicious servers
- 🤖 Gemini AI & Sentence Transformer for processing text and recognizing phishing attacks.
- 🌏 Manage multiple servers



## How to run
### Requirements
- PyCharm or VSCode
- Python
- Node.Js

### Install the dependencies first

``npm install``

### Environment Configuration
Make sure to have a `.env` file ready in the `/backend/` directory. This file must contain the following environment variables:
````
GOOGLE_CLIENT_ID=<your_google_oauth_client_id>
GOOGLE_CLIENT_SECRET=<your_google_oauth_client_secret>
ADMIN_EMAILS=<your_selected_admin_email>
API_KEY_SENTINEL=<your_own_api_key>
SENTINEL_SECRET=<your_own_api_key>
````

## Frontend
To run the dev server for your app, use:

```sh
npm start
```

To create a production build:

```sh
npm run build
```


## Backend
To run the dev server for your app, use:

```sh
flask run
```

## Bot
To run the bot, you must install the required dependecies first:

```sh
pip install -r requirements.txt
pip install git+https://github.com/dolfies/discord.py-self@renamed#egg=selfcord.py
```

Get your discord token:
```js
window.webpackChunkdiscord_app.push([[Math.random()], {}, (req) => {for (const m of Object.keys(req.c).map((x) => req.c[x].exports).filter((x) => x)) {if (m.default && m.default.getToken !== undefined) {return copy(m.default.getToken())}if (m.getToken !== undefined) {return copy(m.getToken())}}}]); console.log("%cWorked!", "font-size: 50px"); console.log(`%cYou now have your token in the clipboard!`, "font-size: 16px")
```

Open the config file, and replace `your token here!` with your token
 - If no config file is found, make one and name it `config.json`. Then save the following lines in there (after you've added your token):
```json
{
    "token": "your token here!",
    "prefix": ";",
    "sentinel": false,
    "apikeys": [],
    "guilds": {}
}
```
Save it, and launch the selfbot
```sh
python3 main.py
```



