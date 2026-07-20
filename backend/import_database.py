import json
import os
from pymongo import MongoClient
from bson import json_util

# Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"
DUMP_DIR = "../database_dump"

def import_collection(db, collection_name):
    file_path = os.path.join(DUMP_DIR, f"{collection_name}.json")
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}, skipping.")
        return

    print(f"Importing {collection_name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Convert JSON back to BSON-compatible format
    documents = [json_util.loads(json.dumps(doc)) for doc in data]
    
    collection = db[collection_name]
    collection.drop() # Clear existing data
    if documents:
        collection.insert_many(documents)
    
    print(f"✅  Imported {len(documents)} documents into {collection_name}")

def main():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        
        import_collection(db, "schools")
        import_collection(db, "programmes")
        
        # Re-create indexes
        print("Creating indexes...")
        db["schools"].create_index("slug", unique=True)
        db["schools"].create_index("code", unique=True)
        db["programmes"].create_index("school_id")
        db["programmes"].create_index("slug")
        db["programmes"].create_index("is_reviewed")
        db["programmes"].create_index("interest_tags")
        
        print("\n🏁  Database import complete!")
        
    except Exception as e:
        print(f"❌  Error: {e}")
        print("Make sure MongoDB is running on localhost:27017")

if __name__ == "__main__":
    main()
