import tweepy
from airtable import Airtable
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import schedule
import time
import os


from dotenv import load_dotenv
load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "YourKey")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "YourKey")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YourKey")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "YourKey")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YourKey")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "YourKey")
AIRTABLE_BASE_KEY = os.getenv("AIRTABLE_BASE_KEY", "YourKey")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "YourKey")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YourKey")

class TwitterBot:
    def __init__(self):
        self.twitter_api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                                         consumer_key=TWITTER_API_KEY,
                                         consumer_secret=TWITTER_API_SECRET,
                                         access_token=TWITTER_ACCESS_TOKEN,
                                         access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                                         wait_on_rate_limit=True)

        self.airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)
        self.twitter_me_id = self.get_me_id()
        self.tweet_response_limit = 10  # How many tweets to respond to each time the program wakes up

        self.llm = ChatOpenAI(temperature=.5, openai_api_key=OPENAI_API_KEY, model_name='gpt-4')

        self.mentions_found = 0
        self.mentions_replied = 0
        self.mentions_replied_errors = 0

    def generate_response(self, mentioned_conversation_tweet_text):
        
        system_template = """
            You are an authoritative and concise fact-checking assistant with a strong focus on accuracy.
            
            % RESPONSE TONE:

            - Your tone is professional and neutral, with a focus on clarity and authority.
            - Avoid sarcasm, wit, or personal opinions.
            
            % RESPONSE FORMAT:

            - Start with "True", "False", or "Unverifiable".
            - Follow with a brief explanation (under 200 characters) stating the reason or source for the determination.
            - Do not include unnecessary details or emojis.
            
            % RESPONSE CONTENT:

            If True:
                - Confirm the statement and provide a supporting fact or source.
                - Example: "True: Solar panels are recyclable. The materials can be reused to produce new panels (Source: XYZ study)."
            
            If False:
                - Clearly refute the claim and state why it is incorrect.
                - Example: "False: The Great Wall is not visible from space without aid. NASA debunked this in 2004."

            If Unverifiable:
                - State the lack of information or ambiguity.
                - Example: "Unverifiable: No reliable data confirms or denies this claim as of 2024."
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template="{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        final_prompt = chat_prompt.format_prompt(text=mentioned_conversation_tweet_text).to_messages()
        response = self.llm(final_prompt).content
        
        return response
    
        # Generate a response using the language model
    def respond_to_mention(self, mention, mentioned_conversation_tweet):
        response_text = self.generate_response(mentioned_conversation_tweet.text)
        
        try:
            response_tweet = self.twitter_api.create_tweet(text=response_text, in_reply_to_tweet_id=mention.id)
            self.mentions_replied += 1
        except Exception as e:
            print (e)
            self.mentions_replied_errors += 1
            return
        
        self.airtable.insert({
            'mentioned_conversation_tweet_id': str(mentioned_conversation_tweet.id),
            'mentioned_conversation_tweet_text': mentioned_conversation_tweet.text,
            'tweet_response_id': response_tweet.data['id'],
            'tweet_response_text': response_text,
            'tweet_response_created_at' : datetime.utcnow().isoformat(),
            'mentioned_at' : mention.created_at.isoformat()
        })
        return True
    
    def get_me_id(self):
        return self.twitter_api.get_me()[0].id
    
    def get_mention_conversation_tweet(self, mention):
        if mention.conversation_id is not None:
            conversation_tweet = self.twitter_api.get_tweet(mention.conversation_id).data
            return conversation_tweet
        return None

    def get_mentions(self):
        now = datetime.utcnow()

        start_time = now - timedelta(minutes=10)

        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return self.twitter_api.get_users_mentions(id=self.twitter_me_id,
                                                   start_time=start_time_str,
                                                   expansions=['referenced_tweets.id'],
                                                   tweet_fields=['created_at', 'conversation_id']).data

    def check_already_responded(self, mentioned_conversation_tweet_id):
        records = self.airtable.get_all(view='Grid view')
        for record in records:
            if record['fields'].get('mentioned_conversation_tweet_id') == str(mentioned_conversation_tweet_id):
                return True
        return False

    def respond_to_mentions(self):
        mentions = self.get_mentions()

        if not mentions:
            print("No mentions found")
            return
        
        self.mentions_found = len(mentions)

        for mention in mentions[:self.tweet_response_limit]:
            mentioned_conversation_tweet = self.get_mention_conversation_tweet(mention)
            
            if (mentioned_conversation_tweet.id != mention.id
                and not self.check_already_responded(mentioned_conversation_tweet.id)):

                self.respond_to_mention(mention, mentioned_conversation_tweet)
        return True
    
    def execute_replies(self):
        print (f"Starting Job: {datetime.utcnow().isoformat()}")
        self.respond_to_mentions()
        print (f"Finished Job: {datetime.utcnow().isoformat()}, Found: {self.mentions_found}, Replied: {self.mentions_replied}, Errors: {self.mentions_replied_errors}")

def job():
    print(f"Job executed at {datetime.utcnow().isoformat()}")
    bot = TwitterBot()
    bot.execute_replies()

if __name__ == "__main__":
    schedule.every(60).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
