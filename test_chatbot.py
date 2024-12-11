import json
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
import logging

# Configure logging for analytics
logging.basicConfig(filename="chatbot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Step 1: Load the database
def load_database(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Step 2: Log user queries and responses
def log_query(user_query, response):
    logging.info(f"Query: {user_query} | Response: {response}")

# Step 3: Process a user query with enhanced matching
def find_link(user_query, database):
    user_query = user_query.lower()
    stop_words = set(stopwords.words('english'))
    query_tokens = word_tokenize(user_query)
    filtered_tokens = [word for word in query_tokens if word not in stop_words]

    possible_matches = []
    for entry in database:
        for keyword in entry['keywords']:
            # Substring and fuzzy matching
            if keyword in user_query or fuzz.partial_ratio(keyword, user_query) > 80:
                # Ensure 'popularity' exists and increment
                if "popularity" not in entry:
                    entry["popularity"] = 0
                entry["popularity"] += 1  # Increase popularity for analytics
                
                # Provide a default description if not available
                description = entry.get('description', 'No description available.')
                
                return f"Intent: {entry['intent']}\nDescription: {description}\nLink: {entry['link']}"
            if any(fuzz.partial_ratio(word, keyword) > 60 for word in filtered_tokens):
                possible_matches.append(entry['intent'])

    if possible_matches:
        return f"Sorry, no exact match found. Did you mean: {', '.join(set(possible_matches))}?"
    return "Sorry, no relevant link found."


# Step 4: Main function for the chatbot
def main():
    # Load the database
    database = load_database('gmu_resources.json')

    print("GMU Chatbot Local Test")
    print("Type 'help' to see available intents or 'exit' to quit.")

    while True:
        # Get user input
        user_query = input("\nEnter your query: ")
        if user_query.lower() == 'exit':
            print("Exiting the test. Goodbye!")
            break
        elif user_query.lower() == 'help':
            print("\nAvailable intents:")
            for entry in database:
                print(f"- {entry['intent']}: {entry.get('description', 'No description available')}")
        else:
            response = find_link(user_query, database)
            log_query(user_query, response)
            print("\nResponse:")
            print(response)

# Run the script
if __name__ == "__main__":
    main()
