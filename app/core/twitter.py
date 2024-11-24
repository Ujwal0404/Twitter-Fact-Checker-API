# app/core/twitter.py
from typing import Dict, List, Optional, Union
import tweepy
import time
from ..config import get_settings
from ..utils.logging import get_logger

settings = get_settings()
logger = get_logger("fact_checker.core.twitter")

class TwitterFetcher:
    def __init__(self, bearer_token: str):
        try:
            self.client = tweepy.Client(bearer_token=bearer_token)
            self.last_request_time = 0
            self.request_count = 0
            self.rate_limit = {
                'requests': 0,
                'window_start': time.time(),
                'window_size': 900,
                'max_requests': 450
            }
            logger.info("TwitterFetcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TwitterFetcher: {str(e)}")
            raise

    def _wait_for_rate_limit(self):
        current_time = time.time()
        window_elapsed = current_time - self.rate_limit['window_start']
        
        if window_elapsed >= self.rate_limit['window_size']:
            logger.debug("Resetting rate limit window")
            self.rate_limit['requests'] = 0
            self.rate_limit['window_start'] = current_time

        if self.rate_limit['requests'] >= self.rate_limit['max_requests'] * 0.9:
            wait_time = self.rate_limit['window_size'] - window_elapsed
            logger.warning(f"Rate limit approaching, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
            self.rate_limit['requests'] = 0
            self.rate_limit['window_start'] = time.time()
            current_time = time.time()

        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < 1.0:
            time.sleep(1.0 - time_since_last_request)

        self.last_request_time = time.time()
        self.rate_limit['requests'] += 1
        logger.debug(f"Rate limit requests: {self.rate_limit['requests']}")

    def get_tweets(self, tweet_ids: Union[str, int, List[Union[str, int]]], max_retries: int = 10) -> Optional[Union[Dict, List[Dict]]]:
        if isinstance(tweet_ids, (str, int)):
            tweet_ids = [str(tweet_ids)]
        else:
            tweet_ids = [str(tid) for tid in tweet_ids]

        logger.info(f"Fetching {len(tweet_ids)} tweets")
        chunk_size = 100
        all_processed_tweets = []
        retry_chunks = []

        for i in range(0, len(tweet_ids), chunk_size):
            chunk = tweet_ids[i:i + chunk_size]
            success = False

            for attempt in range(max_retries):
                try:
                    self._wait_for_rate_limit()
                    logger.debug(f"Fetching chunk starting with ID {chunk[0]}, attempt {attempt + 1}")

                    response = self.client.get_tweets(
                        chunk,
                        tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                        user_fields=['username', 'description', 'public_metrics'],
                        expansions=['author_id', 'referenced_tweets.id']
                    )

                    if not response or not response.data:
                        logger.warning(f"No tweets found for chunk starting with ID {chunk[0]}")
                        break

                    users = {}
                    if response.includes and 'users' in response.includes:
                        users = {user.id: user for user in response.includes['users']}

                    for tweet in response.data:
                        try:
                            user = users.get(tweet.author_id)
                            tweet_data = {
                                'id': tweet.id,
                                'text': tweet.text,
                                'created_at': tweet.created_at,
                                'author_username': user.username if user else None,
                                'author_metrics': user.public_metrics if user else None,
                                'metrics': {
                                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                                    'replies': tweet.public_metrics.get('reply_count', 0),
                                    'likes': tweet.public_metrics.get('like_count', 0),
                                    'quotes': tweet.public_metrics.get('quote_count', 0)
                                },
                                'context_annotations': tweet.context_annotations if hasattr(tweet, 'context_annotations') else None
                            }
                            all_processed_tweets.append(tweet_data)
                            logger.debug(f"Processed tweet {tweet.id}")
                        except Exception as e:
                            logger.warning(f"Error processing tweet {tweet.id}: {str(e)}")
                            continue

                    success = True
                    break

                except tweepy.TooManyRequests as e:
                    reset_time = None
                    try:
                        if hasattr(e, 'response') and e.response is not None:
                            reset_time = int(e.response.headers.get('x-rate-limit-reset', 0))
                    except:
                        reset_time = None

                    wait_time = 30 #max(reset_time - time.time(), 0) if reset_time else min(900, 2 ** attempt * 60)
                    logger.warning(f"Rate limit hit. Waiting {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    self.rate_limit['requests'] = 0
                    self.rate_limit['window_start'] = time.time()

                except Exception as e:
                    wait_time = min(30, 2 ** attempt)
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    time.sleep(wait_time)

            if not success:
                retry_chunks.append(chunk)
                logger.warning(f"Failed to fetch chunk starting with ID {chunk[0]}")

        if retry_chunks:
            logger.info(f"Retrying {len(retry_chunks)} failed chunks...")
            time.sleep(5)

            for chunk in retry_chunks:
                try:
                    self._wait_for_rate_limit()
                    response = self.client.get_tweets(
                        chunk,
                        tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                        user_fields=['username', 'description', 'public_metrics'],
                        expansions=['author_id', 'referenced_tweets.id']
                    )

                    if response and response.data:
                        users = {}
                        if response.includes and 'users' in response.includes:
                            users = {user.id: user for user in response.includes['users']}

                        for tweet in response.data:
                            user = users.get(tweet.author_id)
                            tweet_data = {
                                'id': tweet.id,
                                'text': tweet.text,
                                'created_at': tweet.created_at,
                                'author_username': user.username if user else None,
                                'author_metrics': user.public_metrics if user else None,
                                'metrics': {
                                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                                    'replies': tweet.public_metrics.get('reply_count', 0),
                                    'likes': tweet.public_metrics.get('like_count', 0),
                                    'quotes': tweet.public_metrics.get('quote_count', 0)
                                },
                                'context_annotations': tweet.context_annotations if hasattr(tweet, 'context_annotations') else None
                            }
                            all_processed_tweets.append(tweet_data)
                            logger.debug(f"Processed tweet {tweet.id} in retry")
                except Exception as e:
                    logger.error(f"Final retry failed for chunk: {str(e)}")

        if not all_processed_tweets:
            logger.warning("No tweets were successfully fetched")
            return None

        logger.info(f"Successfully fetched {len(all_processed_tweets)} tweet(s)")
        return all_processed_tweets[0] if len(tweet_ids) == 1 else all_processed_tweets