import csv
from random import choice, randint, sample
from itertools import permutations
import requests
from faker import Faker
from helpers import get_random_datetime

MAX_WARBLER_LENGTH = 140

USERS_CSV_HEADERS = ['email', 'username', 'image_url', 'password', 'bio', 'header_image_url', 'location']
MESSAGES_CSV_HEADERS = ['text', 'timestamp', 'user_id']
FOLLOWS_CSV_HEADERS = ['user_being_followed_id', 'user_following_id']

NUM_USERS = 300
NUM_MESSAGES = 1000
NUM_FOLLWERS = 5000

fake = Faker()

image_urls = [
    f"https://randomuser.me/api/portraits/{kind}/{i}.jpg"
    for kind, count in [("lego", 10), ("men", 100), ("women", 100)]
    for i in range(count)
]

header_image_urls = []
for i in range(1, 46):
    try:
        response = requests.get(f"http://www.splashbase.co/api/v1/images/{i}")
        response.raise_for_status()
        header_image_urls.append(response.json().get('url'))
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching header image {i}: {e}")
        header_image_urls.append("https://defaultimage.com/default.jpg")  # Fallback URL

with open('generator/users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.email(),
            username=fake.user_name(),
            image_url=choice(image_urls),
            password='$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe',
            bio=fake.sentence(),
            header_image_url=choice(header_image_urls),
            location=fake.city()
        ))

with open('generator/messages.csv', 'w') as messages_csv:
    messages_writer = csv.DictWriter(messages_csv, fieldnames=MESSAGES_CSV_HEADERS)
    messages_writer.writeheader()

    for i in range(NUM_MESSAGES):
        messages_writer.writerow(dict(
            text=fake.paragraph()[:MAX_WARBLER_LENGTH],
            timestamp=get_random_datetime(),
            user_id=randint(1, NUM_USERS)
        ))

with open('generator/follows.csv', 'w') as follows_csv:
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))

    users_writer = csv.DictWriter(follows_csv, fieldnames=FOLLOWS_CSV_HEADERS)
    users_writer.writeheader()

    for followed_user, follower in sample(all_pairs, NUM_FOLLWERS):
        users_writer.writerow(dict(user_being_followed_id=followed_user, user_following_id=follower))
