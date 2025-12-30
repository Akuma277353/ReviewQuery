import sys
import argparse
from pymongo import MongoClient

def connect_to_mongodb(port):
    """
    Connects to MongoDB (localhost) on the specified port and returns the 'reviews' collection 
    from a database named '291db'.
    """
    try:
        client = MongoClient(f'mongodb://localhost:{port}/')
        db = client['291db']
        return db.reviews
    except Exception as e:
        print("Error connecting to MongoDB:", str(e))
        sys.exit(1)

def get_product_rating(collection, asin):
    """
    1) Get the average rating and total reviews for a product by its ASIN.
    """
    pipeline = [
        {"$match": {"asin": asin}},
        {"$group": {
            "_id": "$asin",
            "average_rating": {"$avg": "$overall"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        print(f"\nProduct ASIN: {asin}")
        print(f"Average Rating: {result[0]['average_rating']:.2f}")
        print(f"Total Reviews: {result[0]['total_reviews']}")
    else:
        print(f"No reviews found for product with ASIN: {asin}")

def get_top_products(collection, n):
    """
    2) Find the top N highest-rated products by average rating (descending), 
       showing their ASIN, average rating, and total reviews.
    """
    pipeline = [
        {"$group": {
            "_id": "$asin",
            "average_rating": {"$avg": "$overall"},
            "total_reviews": {"$sum": 1}
        }},
        {"$sort": {"average_rating": -1}},
        {"$limit": n}
    ]
    results = list(collection.aggregate(pipeline))
    print(f"\nTop {n} Products:")
    if not results:
        print("No products found in the database.")
        return
    
    for i, product in enumerate(results, start=1):
        print(f"{i}. ASIN: {product['_id']}")
        print(f"   Average Rating: {product['average_rating']:.2f}")
        print(f"   Total Reviews: {product['total_reviews']}")

def get_most_active_reviewers(collection):
    """
    3) List the 10 most active reviewers (descending by number of reviews).
    """
    pipeline = [
        {"$group": {
            "_id": "$reviewerID",
            "reviewer_name": {"$first": "$reviewerName"},
            "total_reviews": {"$sum": 1}
        }},
        {"$sort": {"total_reviews": -1}},
        {"$limit": 10}
    ]
    results = list(collection.aggregate(pipeline))
    print("\nMost Active Reviewers:")
    if not results:
        print("No reviewers found.")
        return
    
    for i, reviewer in enumerate(results, start=1):
        print(f"{i}. Reviewer ID: {reviewer['_id']}")
        print(f"   Name: {reviewer['reviewer_name']}")
        print(f"   Total Reviews: {reviewer['total_reviews']}")

def get_reviews_over_time(collection, asin):
    """
    4) Show how the number of reviews for a specific product has changed over
       user-input years (up to 5). We do NOT advance to the next "year #"
       if the user enters a duplicate or invalid year.
    """

    years = []
    max_years = 5
    count_valid = 0  # how many valid (unique) years we have so far

    while count_valid < max_years:
        prompt_num = count_valid + 1
        year_str = input(f"Enter year {prompt_num} (or press Enter to stop): ").strip()

        # If user presses Enter with no input, stop entirely
        if not year_str:
            break

        # Try converting input to an integer year
        try:
            year = int(year_str)
            # If it's a duplicate, print a message but DO NOT increment count_valid
            if year in years:
                print(f"You already entered {year}. Skipping duplicate.")
            else:
                years.append(year)
                count_valid += 1
        except ValueError:
            print("Invalid input. Please enter a numeric year or press Enter to stop.")
            # We do NOT increment count_valid here, so the user is asked for the same slot again

    # If user ended up entering no valid years, just return
    if not years:
        print("No valid years provided.")
        return

    # Build a pipeline to compute total reviews grouped by 'year' for the given ASIN.
    pipeline = [
        {"$match": {"asin": asin}},
        {"$project": {
            # Convert from seconds to milliseconds, then to a Date, extract the year
            "year": {
                "$year": {
                    "$toDate": {"$multiply": ["$unixReviewTime", 1000]}
                }
            }
        }},
        {"$group": {
            "_id": "$year",
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(collection.aggregate(pipeline))
    
    print(f"\nReviews over time for product {asin}:")
    for y in years:
        # Find the result for this specific year, or default to 0
        cnt = next((r['count'] for r in results if r['_id'] == y), 0)
        print(f"{y}: {cnt} reviews")


def get_suspicious_reviews(collection):
    """
    5) Identify reviews that might be spam:
       - rating >= 4.5
       - "helpful" array present with at least 2 elements: [#unhelpful, #helpful]
       - fewer than 10% found it helpful => helpful_votes / total_votes < 0.1
    """
    pipeline = [
        # Make sure "helpful" field exists and has 2 elements
        {"$match": {
            "overall": {"$gte": 4.5},
            "helpful": {"$exists": True, "$size": 2}
        }},
        # Exclude any that have zero total votes to avoid dividing by zero
        {"$match": {
            "$expr": {
                "$gt": [
                    {"$add": [
                        {"$arrayElemAt": ["$helpful", 0]},
                        {"$arrayElemAt": ["$helpful", 1]}
                    ]},
                    0
                ]
            }
        }},
        # Project a helpfulness_ratio = helpful_votes / (helpful_votes + unhelpful_votes)
        {"$project": {
            "asin": 1,
            "overall": 1,
            "helpful": 1,
            "reviewText": 1,
            "helpfulness_ratio": {
                "$divide": [
                    {"$arrayElemAt": ["$helpful", 1]},  # helpful_votes
                    {"$add": [
                        {"$arrayElemAt": ["$helpful", 0]},  # unhelpful_votes
                        {"$arrayElemAt": ["$helpful", 1]}   # helpful_votes
                    ]}
                ]
            }
        }},
        # Keep only those with ratio < 0.1
        {"$match": {"helpfulness_ratio": {"$lt": 0.1}}},
        # Sort by ratio ascending
        {"$sort": {"helpfulness_ratio": 1}},
        # Limit to top 10
        {"$limit": 10}
    ]
    results = list(collection.aggregate(pipeline))
    
    print("\nTop 10 Suspicious Reviews (rating >= 4.5, <10% found it helpful):")
    if not results:
        print("No suspicious reviews found.")
        return
    
    for i, review in enumerate(results, start=1):
        helpful = review.get('helpful', [])
        ratio = review.get('helpfulness_ratio', 0.0)
        print(f"\n{i}. ASIN: {review.get('asin')}")
        print(f"   Rating: {review.get('overall')}")
        print(f"   Helpfulness (unhelpful, helpful): {helpful}")
        print(f"   Helpfulness Ratio: {ratio:.2%}")
        # Print only first 200 chars of reviewText for brevity
        text_sample = (review.get('reviewText') or "")[:200]
        print(f"   Review Text: {text_sample}...")

def main():
    parser = argparse.ArgumentParser(description='MongoDB Query Interface')
    parser.add_argument('port', type=int, help='MongoDB port number')
    args = parser.parse_args()
    
    collection = connect_to_mongodb(args.port)
    
    while True:
        print("\nMongoDB Query Interface")
        print("1. Get product rating by ASIN")
        print("2. Find top N products")
        print("3. List most active reviewers")
        print("4. Show reviews over time")
        print("5. Flag suspicious reviews")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            asin = input("Enter product ASIN: ").strip()
            get_product_rating(collection, asin)
        
        elif choice == '2':
            try:
                n = int(input("Enter number of top products to show: ").strip())
                if n < 1:
                    print("Please enter a positive integer.")
                else:
                    get_top_products(collection, n)
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '3':
            get_most_active_reviewers(collection)
        
        elif choice == '4':
            asin = input("Enter product ASIN: ").strip()
            get_reviews_over_time(collection, asin)
        
        elif choice == '5':
            get_suspicious_reviews(collection)
        
        elif choice == '6':
            print("Goodbye!")
            sys.exit(0)
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
