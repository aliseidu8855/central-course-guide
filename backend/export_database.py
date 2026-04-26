import json
import os
from pymongo import MongoClient
from bson import json_util

# Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"
DUMP_DIR = "../database_dump"

def export_collection(db, collection_name):
    print(f"Exporting {collection_name}...")
    collection = db[collection_name]
    cursor = collection.find({})
    
    # Convert BSON to JSON-compatible format
    data = [json.loads(json_util.dumps(doc)) for doc in cursor]
    
    file_path = os.path.join(DUMP_DIR, f"{collection_name}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅  Exported {len(data)} documents to {file_path}")

def main():
    if not os.path.exists(DUMP_DIR):
        os.makedirs(DUMP_DIR)
        print(f"Created directory: {DUMP_DIR}")

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        
        export_collection(db, "schools")
        export_collection(db, "programmes")
        
        print("\n🏁  Database export complete!")
        print("You can now commit the 'database_dump' directory to the repository.")
        
    except Exception as e:
        print(f"❌  Error: {e}")
        print("Make sure MongoDB is running on localhost:27017")

if __name__ == "__main__":
    main()
