## 🤖TathyaX Bot
Welcome to the TathyaX Fact-Check Bot repository! This project demonstrates the use of AI and APIs to create a bot that verifies the truthfulness of tweets and responds with concise, authoritative explanations.

## 🚀 Features
-> Automatically checks the truthfulness of tweets mentioning the bot.
-> Replies with "True", "False", or "Unverifiable", followed by a brief explanation.
-> Professional and neutral tone in all responses.
-> Uses a blend of AI language models and reliable data sources for fact-checking.

## 📋 How It Works
1. Monitoring Mentions: The bot scans for tweets mentioning its handle.
2. Fact-Checking:
   - If the claim is verifiable, it determines its truthfulness using predefined datasets or APIs.
   - For unverifiable claims, it responds appropriately.
3. Replying to Tweets: The bot crafts a concise reply with reasoning and posts it under the original tweet.

## 🛠️ Setup and Deployment
#### Prerequisites
- Python 3.8+
- A Twitter Developer Account with API keys (Free Tier suffices for light usage).
- OpenAI API key for language processing.
- Optional: Airtable account for logging (can be disabled).

#### Installation
1. Clone the repository:
`git clone https://github.com/Tathya-X/TathyaX-version-2.git
cd TathyaX-version-2
`
2. Install dependencies:
`pip install -r requirements.txt
`
3. Set environment variables:
 `TWITTER_API_KEY=your-twitter-api-key,
TWITTER_API_SECRET=your-twitter-api-secret,
TWITTER_ACCESS_TOKEN=your-access-token,
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret,
OPENAI_API_KEY=your-openai-api-key
`
4. Run Locally
`tathyax.py`

#### Deployment
- Use free hosting platforms like Railway or any other cloud service.
- Add your environment variables to the hosting platform.

## 📚 Response Template
The bot responds to tweets with:

- True: A claim is correct, backed by a reliable source.
Example: "True: Polar bears can swim for days. Studies show they travel hundreds of miles in open water."

- False: A claim is incorrect, with a brief explanation.
Example: "False: Goldfish do not have a 3-second memory. They remember tasks for months."

- Unverifiable: A claim cannot be confirmed or denied due to lack of evidence.
Example: "Unverifiable: No reliable data supports or refutes this claim."

## 📝 License
- This project is licensed under the MIT License. See the LICENSE file for more details.

## 🤝 Contributing
- Feel free to fork this repo, submit issues, or suggest features!



