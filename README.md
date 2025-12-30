[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/K8rTjKb8)
# Members(Names and CCIDs)
1. Abubakar Shaikh (amshaik1)
2. Ujjawal Pratap Singh (upsingh)
3. Fatin Ahmed (fatin2)
4. Stevin Santhosh (stevin1)

# Prerequisites
1. Python 3.x
2. MongoDB (running locally)
3. pymongo
```
pip install pymongo
```
# Instructions:
1. Clone the repository to your local machine
2. Open your terminal and navigate to the project folder
3. Make your MongoDB server
```
mongod --port 27017
```
4. Load the Dataset into MongoDB
```
python3 load-json.py 100.json 27017
```
5. Run the interactive Query tool
```
python3 phase2_query.py 27017
```
6. You'll see a menu, Follow the prompts for each query.
   
To Get product rating by ASIN (Type 1, press Enter, and then type an ASIN (e.g., B000FA64PK) to see the average rating and total number of reviews for that product.)

   Find top N products (Type 2, press Enter, then enter a number (e.g., 5), and it will show you the top 5 products by average rating.

   List most active reviewers (Type 3 and press Enter, and you’ll see the 10 reviewers who wrote the most reviews.)
   
   Show reviews over time (Type 4, press Enter, then type an ASIN.
       Next, enter up to 5 different years (press Enter on a year prompt to stop early).
       It will display how many reviews were posted in each of those years.
   
   Flag suspicious reviews (Type 5, press Enter, and the system will display the top 10 suspicious reviews (where rating >= 4.5 but fewer than 10% found it helpful).

   Exit (Type 6 to exit the program.)

# Sources of Information:
-

# AI Agent Use
-
