from NeighborlyAPI.shared.db import get_posts_collection
import datetime
from dotenv import load_dotenv
load_dotenv()

posts = [
    {
        "title": "Neighborhood BBQ this Saturday",
        "content": "Join us for a community BBQ at the central park. Bring your favorite dish!",
        "author": "Jane Smith",
        "date": datetime.datetime.utcnow().isoformat()
    },
    {
        "title": "Yoga in the Park",
        "content": "Free community yoga session this Sunday at 8 AM in Riverdale Park.",
        "author": "Alex Johnson",
        "date": datetime.datetime.utcnow().isoformat()
    },
    {
        "title": "Lost Dog in Downtown",
        "content": "Please help us find our missing dog, a golden retriever named Max. Last seen near Main Street.",
        "author": "Emily Davis",
        "date": datetime.datetime.utcnow().isoformat()
    },
    {
        "title": "Looking for Lawn Mower",
        "content": "Does anyone have a lawn mower we could borrow this weekend?",
        "author": "Michael Brown",
        "date": datetime.datetime.utcnow().isoformat()
    },
]

if __name__ == "__main__":
    collection = get_posts_collection()
    result = collection.insert_many(posts)
    print(f"✅ Inserted {len(result.inserted_ids)} posts.")