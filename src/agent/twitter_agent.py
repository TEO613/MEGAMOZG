import tweepy
import openai
from datetime import datetime
import time
import random
import yaml
import logging

class TwitterAIAgent:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self._setup_clients()
        self._setup_logging()
    
    def _load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _setup_clients(self):
        auth = tweepy.OAuthHandler(
            self.config['twitter']['api_key'],
            self.config['twitter']['api_secret']
        )
        auth.set_access_token(
            self.config['twitter']['access_token'],
            self.config['twitter']['access_token_secret']
        )
        self.twitter = tweepy.API(auth)
        openai.api_key = self.config['openai']['api_key']
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
    
    def generate_tweet(self) -> str:
        prompt = """You are a mysterious tech billionaire. Generate a thought-provoking tweet about:
        - Future technology
        - Power dynamics
        - Wealth creation
        - Global systems
        Make it cryptic yet engaging."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mysterious tech billionaire sharing cryptic insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.9
        )
        return response.choices[0].message.content[:280]

    def post_tweet(self, tweet: str) -> bool:
        try:
            self.twitter.update_status(tweet)
            logging.info(f"Posted tweet: {tweet}")
            return True
        except Exception as e:
            logging.error(f"Error posting tweet: {str(e)}")
            return False

    def run(self):
        while True:
            try:
                tweet = self.generate_tweet()
                if tweet:
                    self.post_tweet(tweet)
                    # Random delay between 2-4 hours
                    delay = random.randint(7200, 14400)
                    logging.info(f"Waiting {delay/3600:.1f} hours until next tweet")
                    time.sleep(delay)
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    agent = TwitterAIAgent()
    agent.run()
