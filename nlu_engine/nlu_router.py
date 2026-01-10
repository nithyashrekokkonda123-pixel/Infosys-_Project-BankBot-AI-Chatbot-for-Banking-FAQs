"""
NLU Router
----------
Central router that combines:
1. Intent classification
2. Entity extraction

Usage:
    router = NLURouter()
    result = router.process("Transfer ₹5000 to account 123456 TXN9876")
"""

from .entity_extractor import EntityExtractor
from .infer_intent import predict_intents


class NLURouter:
    def __init__(self):
        """
        Initialize all NLU components
        """
        self.entity_extractor = EntityExtractor()

    def process(self, user_text):
        """
        Complete NLU pipeline

        Steps:
        1. Predict intents
        2. Extract entities
        3. Return structured output
        """

        # Step 1: Intent prediction
        intents = predict_intents(user_text)

        # Step 2: Entity extraction
        entities = self.entity_extractor.extract(user_text)

        # Step 3: Pick top intent
        top_intent = intents[0]["intent"] if intents else None
        confidence = intents[0]["confidence"] if intents else 0.0

        # Step 4: Final response
        nlu_output = {
            "text": user_text,
            "top_intent": top_intent,
            "confidence": confidence,
            "intents": intents,
            "entities": entities
        }

        return nlu_output


# -------------------------------
# TESTING THE NLU ROUTER
# -------------------------------
if __name__ == "__main__":
    router = NLURouter()

    test_text = "Transfer ₹5000 to account 123456 TXN9876"
    result = router.process(test_text)

    from pprint import pprint
    pprint(result)
    
    def detect_intent_and_entities(text):
        text = text.lower()
        if any(greet in text for greet in ["hi", "hello", "hey"]):
            return "greet", []
        elif "balance" in text:
            return "check_balance", []
        elif "transfer" in text:
            return "transfer_money", []
        else:
            return None, []