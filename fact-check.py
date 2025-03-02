import requests
import json
import os

def search_fact_check_claims(query, api_key=None, max_results=10, language_code="en-US"):
    """
    Searches Google's Fact Check Claim API for claims matching the given query.

    Args:
        query: The search query.
        api_key: Your Google Fact Check API key. If None, it will be read from the GOOGLE_FACT_CHECK_API_KEY environment variable.
        max_results: The maximum number of results to return.
        language_code: The language code for the results (e.g., "en-US").

    Returns:
        A list of claim dictionaries, or None if an error occurs.
    """

    if api_key is None:
        api_key = os.environ.get("GOOGLE_FACT_CHECK_API_KEY")
        if api_key is None:
            print("Error: API key not provided and GOOGLE_FACT_CHECK_API_KEY environment variable not set.")
            return None

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": query,
        "key": api_key,
        "pageSize": max_results,
        "languageCode": language_code,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get("claims", [])  # Return the list of claims, or an empty list if not found.

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except KeyError as e:
        print(f"Error extracting claims from response: {e}")
        return None


# Example Usage (replace with your actual API key or set the environment variable):
if __name__ == "__main__":

    my_query = "global warming is a hoax"
    #Option 1: Using an environment variable
    #claims = search_fact_check_claims(my_query)

    #Option 2: Passing the api key directly.
    api_key_value = "AIzaSyAUOzd0eLCkDi4LgOmwTh-mAwNLKlnZevU" #Replace with your api key.
    claims = search_fact_check_claims(my_query, api_key=api_key_value)

    if claims:
        for claim in claims:
            print("Claim Review:")
            print(f"  Text: {claim.get('text')}")

            if 'claimReview' in claim:  
                for review in claim['claimReview']:
                    print(f"    Publisher: {review.get('publisher', {}).get('name')}")
                    print(f"    URL: {review.get('url')}")
                    print(f"    Rating: {review.get('textualRating')}") #If available
                    print("-" * 20)
            else:
              print("    No reviews found")
            print("=" * 40)
    else:
        print("No claims found or an error occurred.")