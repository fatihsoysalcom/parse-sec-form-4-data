import requests
import json
from datetime import datetime, timedelta

# This script demonstrates parsing SEC Form 4 filings for a single day.
# It fetches data from the SEC EDGAR API and extracts key transaction details.

# Define the target date (yesterday)
today = datetime.now()
yesterday = today - timedelta(days=1)
filing_date_str = yesterday.strftime('%Y%m%d')

# SEC EDGAR API endpoint for Form 4 filings
# We'll use the 'form4' endpoint and filter by date.
# The API returns a JSON object with filing metadata and links to the actual filings.
api_url = f"https://api.sec.gov/filings/form4?date={filing_date_str}"

print(f"Fetching Form 4 filings for: {filing_date_str}")

try:
    response = requests.get(api_url)
    response.raise_for_status() # Raise an exception for bad status codes
    data = response.json()

    # The response contains a list of filings. Each filing has a 'filingUrl' pointing to the full filing data.
    filings = data.get('filings', [])

    if not filings:
        print("No Form 4 filings found for the specified date.")
    else:
        print(f"Found {len(filings)} Form 4 filings.")
        print("--- Transaction Details ---")

        for filing in filings:
            filing_url = filing.get('filingUrl')
            if not filing_url:
                continue

            # Fetch the actual filing data
            filing_response = requests.get(filing_url)
            filing_response.raise_for_status()
            filing_data = filing_response.json()

            # Extract relevant information from the filing data
            # The structure can be complex, we're looking for 'ownerSignature' and 'transactionInformation'
            owner_signature = filing_data.get('ownerSignature', {{}})
            owner_name = owner_signature.get('person', {{}}).get('lastName', 'N/A')

            transactions = filing_data.get('transactionInformation', {{}})
            if not transactions:
                continue

            # Iterate through each transaction within the filing
            # 'securitiesTransactions' is a list of individual trades
            securities_transactions = transactions.get('securitiesTransactions', [])
            for transaction in securities_transactions:
                # Extract details of each transaction
                security_title = transaction.get('securityTitle', 'N/A')
                transaction_type = transaction.get('transactionType', {{}}).get('type', 'N/A')
                shares_transacted = transaction.get('sharesTransacted', {{}}).get('value', 'N/A')
                price_per_share = transaction.get('pricePerShare', {{}}).get('value', 'N/A')

                print(f"Owner: {owner_name}")
                print(f"  Security: {security_title}")
                print(f"  Type: {transaction_type}")
                print(f"  Shares: {shares_transacted}")
                print(f"  Price/Share: {price_per_share}")
                print("-" * 20)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from SEC API: {e}")
except json.JSONDecodeError:
    print("Error decoding JSON response from SEC API.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
