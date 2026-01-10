import re

class EntityExtractor:
    def __init__(self):
        self.amount_pattern = re.compile(r'(?:₹|\$)?\b\d+(?:,\d+)?\b')
        self.account_pattern = re.compile(r'\b\d{6,12}\b')
        self.txn_pattern = re.compile(r'\bTXN\d+\b')

        # Card context: card / debit / credit / atm ... ending XXXX
        self.card_context = re.compile(
            r'(card|debit|credit|atm).*?(\d{3,4})',
            re.IGNORECASE
        )

    def extract(self, text):
        entities = []

        # ---- CARD NUMBER ----
        card_numbers = set()
        for match in self.card_context.finditer(text):
            card_num = match.group(2)
            card_numbers.add(card_num)
            entities.append({
                "entity": "card_number",
                "value": card_num
            })

        # ---- ACCOUNT NUMBERS ----
        account_numbers = set(self.account_pattern.findall(text))
        for acc in account_numbers:
            entities.append({
                "entity": "account_number",
                "value": acc
            })

        # ---- AMOUNT ----
        for match in self.amount_pattern.finditer(text):
            value = match.group()

            # Skip if it's card or account number
            if value in card_numbers:
                continue
            if value in account_numbers:
                continue

            entities.append({
                "entity": "amount",
                "value": value
            })

        # ---- TRANSACTION ID ----
        for txn in self.txn_pattern.findall(text):
            entities.append({
                "entity": "transaction_id",
                "value": txn
            })

        return entities


def extract_entities(query, intent):
    """
    Wrapper function for NLU Visualizer compatibility
    Extract entities from a user query based on the predicted intent
    
    Args:
        query (str): The user's input query
        intent (str): The predicted intent
    
    Returns:
        dict: Dictionary of extracted entities with entity types as keys
    """
    extractor = EntityExtractor()
    entities_list = extractor.extract(query)
    
    # Convert list format to dict format for compatibility
    entities_dict = {}
    
    for entity in entities_list:
        entity_type = entity["entity"]
        entity_value = entity["value"]
        
        # If entity type already exists, append with index
        if entity_type in entities_dict:
            # Handle multiple entities of same type
            if isinstance(entities_dict[entity_type], list):
                entities_dict[entity_type].append(entity_value)
            else:
                # Convert to list if second occurrence
                entities_dict[entity_type] = [entities_dict[entity_type], entity_value]
        else:
            entities_dict[entity_type] = entity_value
    
    # Intent-specific entity enrichment
    query_lower = query.lower()
    
    # Extract card blocking reason
    if intent == 'card_block':
        block_reasons = ['lost', 'stolen', 'fraud', 'damaged', 'compromised']
        for reason in block_reasons:
            if reason in query_lower:
                entities_dict['reason'] = reason
                break
        
        # Card type
        card_types = ['credit', 'debit', 'atm']
        for card_type in card_types:
            if card_type in query_lower:
                entities_dict['card_type'] = card_type
                break
    
    # Extract account type
    if intent in ['check_balance', 'transfer_money']:
        account_types = ['savings', 'current', 'checking', 'salary']
        for acc_type in account_types:
            if acc_type in query_lower:
                entities_dict['account_type'] = acc_type
                break
    
    # Extract transfer type
    if intent == 'transfer_money':
        transfer_types = ['neft', 'rtgs', 'imps', 'upi']
        for transfer_type in transfer_types:
            if transfer_type in query_lower:
                entities_dict['transfer_type'] = transfer_type.upper()
                break
        
        # Beneficiary name pattern (after "to" keyword)
        to_pattern = r'to\s+([A-Za-z\s]+?)(?:\s+account|\s+\d|\s*$)'
        to_matches = re.findall(to_pattern, query_lower)
        if to_matches:
            beneficiary = to_matches[0].strip()
            if len(beneficiary) > 1:  # Avoid single characters
                entities_dict['beneficiary_name'] = beneficiary
    
    # Extract location for ATM/branch queries
    if 'atm' in query_lower or 'branch' in query_lower:
        location_pattern = r'(?:near|at|in)\s+([A-Za-z\s]+?)(?:\s+area|\s*$|,|\?)'
        location_matches = re.findall(location_pattern, query, re.IGNORECASE)
        if location_matches:
            location = location_matches[0].strip()
            if len(location) > 2:  # Avoid very short matches
                entities_dict['location'] = location
    
    # Extract date/time entities
    date_patterns = [
        (r'\b(today|yesterday|tomorrow)\b', 'relative_date'),
        (r'\b(last|past|previous)\s+(week|month|year)\b', 'relative_period'),
        (r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', 'specific_date')
    ]
    
    for pattern, date_type in date_patterns:
        date_matches = re.findall(pattern, query_lower)
        if date_matches:
            if isinstance(date_matches[0], tuple):
                entities_dict['date'] = ' '.join(date_matches[0])
            else:
                entities_dict['date'] = date_matches[0]
            break
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, query)
    if email_matches:
        entities_dict['email'] = email_matches[0]
    
    # Extract phone number
    phone_pattern = r'(?:\+91[-\s]?)?[6-9]\d{9}'
    phone_matches = re.findall(phone_pattern, query)
    if phone_matches:
        entities_dict['phone'] = phone_matches[0]
    
    return entities_dict


# Helper functions for backward compatibility
def extract_amount(query):
    """Extract monetary amount from query"""
    extractor = EntityExtractor()
    entities = extractor.extract(query)
    for entity in entities:
        if entity["entity"] == "amount":
            amount_str = entity["value"].replace('₹', '').replace('$', '').replace(',', '').strip()
            try:
                return float(amount_str)
            except ValueError:
                continue
    return None


def extract_account_number(query):
    """Extract account number from query"""
    extractor = EntityExtractor()
    entities = extractor.extract(query)
    for entity in entities:
        if entity["entity"] == "account_number":
            return entity["value"]
    return None


def extract_card_number(query):
    """Extract card number from query"""
    extractor = EntityExtractor()
    entities = extractor.extract(query)
    for entity in entities:
        if entity["entity"] == "card_number":
            return entity["value"]
    return None


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_queries = [
        ("Transfer 5000 to account 123456789", "transfer_money"),
        ("What's my account balance for account 789012345", "check_balance"),
        ("My credit card ending 1234 is stolen, please block it", "card_block"),
        ("Send ₹10,000 to John's account 456789012", "transfer_money"),
        ("I lost my debit card 5678", "card_block"),
        ("Check balance", "check_balance"),
        ("Find ATM near Jubilee Hills", "llm"),
        ("Transfer 2000 via IMPS to account 987654321", "transfer_money"),
        ("Block my card 9999 it's compromised", "card_block"),
    ]
    
    print("Entity Extraction Test Results:")
    print("=" * 70)
    
    for query, intent in test_queries:
        entities = extract_entities(query, intent)
        print(f"\nQuery: {query}")
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        print("-" * 70)