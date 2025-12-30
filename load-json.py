import sys
import json
from pymongo import MongoClient
import argparse

def load_json_to_mongodb(json_file, port):
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:{}/'.format(port))
        db = client['291db']
        
        # Create collection if it doesn't exist
        collection = db.reviews
        
        # Process JSON file in batches
        batch_size = 5000
        batch = []
        
        with open(json_file, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    review = json.loads(line.strip())
                    batch.append(review)
                    
                    if len(batch) >= batch_size:
                        collection.insert_many(batch)
                        batch = []
                except json.JSONDecodeError:
                    print("Error decoding JSON line: {}".format(line.strip()))
                    continue
            
            # Insert remaining documents
            if batch:
                collection.insert_many(batch)
        
        print("Successfully loaded data from {} into MongoDB".format(json_file))
        print("Database: 291db")
        print("Collection: reviews")
        
    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Load JSON file into MongoDB')
    parser.add_argument('json_file', help='Path to the JSON file')
    parser.add_argument('port', type=int, help='MongoDB port number')
    
    args = parser.parse_args()
    load_json_to_mongodb(args.json_file, args.port)

if __name__ == "__main__":
    main() 
