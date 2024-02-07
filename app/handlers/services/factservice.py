import redis
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import mysql.connector
from redis.exceptions import RedisError
import random


class DatabaseError(Exception):
	"""Error in any DB connection or operations"""
	pass


class FactService:
	facts = None
	redis_conn = None

	DAILY_MAX = 5
	RECENT_IDS_SIZE = 50

	def populate_facts(self):
		"""Connect to db and populate facts dict class variable"""
		config = {
			'user': os.environ['DB_USER'],
			'password': os.environ['DB_PASSWORD'],
			'host': os.environ['DB_HOST'],
			'database': os.environ['DB_NAME']
		}

		try:
			conn = mysql.connector.connect(**config)
			cursor = conn.cursor()

			query = "select id, message from pojofacts"
			cursor.execute(query)
			FactService.facts = {id_: message for id_, message in cursor}

			cursor.close()
			conn.close()
		except (mysql.connector.Error, IOError) as e:
			raise DatabaseError()

	def get_redis_conn(self):
		"""Set Redis connection to class variable and return it"""
		if FactService.redis_conn is None:
			environment = os.environ['ENVIRONMENT']
			if environment == 'testing':
				config = {
					'host': os.environ['REDIS_HOST'],
					'port': os.environ['REDIS_PORT'],
					'db': os.environ['REDIS_DB'],
					'decode_responses': True
				}

				FactService.redis_conn = redis.Redis(**config)

			if environment == 'production':
				url = os.environ['REDIS_URL']
				FactService.redis_conn = redis.from_url(url, db=0, decode_responses=True)
		return FactService.redis_conn

	def increment_user_tries(self, user_id):
		"""Increment user's daily request count, set expiration if first, and return count"""
		r = self.get_redis_conn()
		key = f"user:{user_id}"
		r.incr(key)
		r.expireat(key, self.get_next_midnight(), nx=True)
		return int(r.get(key))

	def get_next_midnight(self):
		"""Calculate next midnight from now, for Redis expiration"""
		now = datetime.now(timezone.utc).astimezone(ZoneInfo('MST'))
		tomorrow = now + timedelta(1)
		midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
		return midnight

	def get_random_key(self):
		"""Get random key not in recently used"""
		r = self.get_redis_conn()
		recent_keys = [int(k) for k in r.lrange('recentfacts', 0, -1)]
		all_keys = FactService.facts.keys()
		fresh_keys = list(set(all_keys) - set(recent_keys))
		return random.choice(fresh_keys)

	def get_fact(self):
		"""Return random fact, add it to recently used and truncate length"""
		key = self.get_random_key()

		# Add to recently used IDs
		r = self.get_redis_conn()
		r.lpush('recentfacts', key)
		r.ltrim('recentfacts', 0, FactService.RECENT_IDS_SIZE-1)

		return FactService.facts[key]

	def response(self, user_id):
		try:
			# Populate facts dict if empty
			if FactService.facts is None:
				self.populate_facts()

			# Increment and check count (if above max, return message)
			if self.increment_user_tries(user_id) > FactService.DAILY_MAX:
				return "*Pojo has given you, specifically, too many facts today and must rest. Inquire again tomorrow.*"

			# Get value, add key to recents
			return self.get_fact()
		except (DatabaseError, RedisError):
			return "`Database error. Alert the admin and/or the president.`"

