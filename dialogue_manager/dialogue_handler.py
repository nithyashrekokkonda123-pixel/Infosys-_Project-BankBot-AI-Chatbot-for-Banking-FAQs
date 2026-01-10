from database.bank_crud import (
    get_account,
    transfer_money,
    save_chat
)
from database.security import verify_password
from nlu_engine.nlu_router import NLURouter
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# ---------------- INIT ----------------
router = NLURouter()
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)


class DialogueHandler:
    def __init__(self):
        self.context = {}

    def handle_message(self, user_input):
        text = user_input.strip()
        lower_text = text.lower()

        response = None
        intent = None
        confidence = 0.0

        # ================= QUICK GREETINGS =================
        if lower_text in ["hi", "hello", "hey", "good morning", "good evening"]:
            intent = "greetings"  # Changed from "greet" to match your intents
            confidence = 1.0  # Fixed: Set high confidence for direct matches
            response = "Hello 👋 Welcome to BankBot. How can I assist you today?"

        elif lower_text in ["thanks", "thank you", "thx", "thankyou"]:
            intent = "greetings"
            confidence = 1.0  # Fixed: Set high confidence for direct matches
            response = "You're welcome 😊 Happy to help you!"

        # ================= CONTEXT FLOWS =================

        # ---- BALANCE FLOW ----
        elif self.context.get("flow") == "balance_acc":
            intent = "check_balance"
            confidence = 0.95  # Fixed: Set confidence for context flow
            self.context["acc_no"] = text
            self.context["flow"] = "balance_pwd"
            response = "Please enter your password."

        elif self.context.get("flow") == "balance_pwd":
            intent = "check_balance"
            confidence = 0.95  # Fixed: Set confidence for context flow
            acc_no = self.context.get("acc_no")
            self.context.clear()
            response = self.process_balance(acc_no, text)

        # ---- TRANSFER FLOW ----
        elif self.context.get("flow") == "transfer_from":
            intent = "transfer_money"
            confidence = 0.95  # Fixed: Set confidence for context flow
            self.context["from_acc"] = text
            self.context["flow"] = "transfer_to"
            response = "Please enter receiver account number."

        elif self.context.get("flow") == "transfer_to":
            intent = "transfer_money"
            confidence = 0.95  # Fixed: Set confidence for context flow
            self.context["to_acc"] = text
            self.context["flow"] = "transfer_amount"
            response = "Please enter transfer amount."

        elif self.context.get("flow") == "transfer_amount":
            intent = "transfer_money"
            confidence = 0.95  # Fixed: Set confidence for context flow
            if not text.isdigit():
                response = "Please enter a valid amount."
            else:
                self.context["amount"] = int(text)
                self.context["flow"] = "transfer_pwd"
                response = "Please enter your password."

        elif self.context.get("flow") == "transfer_pwd":
            intent = "transfer_money"
            confidence = 0.95  # Fixed: Set confidence for context flow
            data = self.context.copy()
            self.context.clear()
            response = self.process_transfer(
                data["from_acc"],
                data["to_acc"],
                data["amount"],
                text
            )

        # ---- CARD BLOCK FLOW ----
        elif self.context.get("flow") == "card_acc":
            intent = "card_block"
            confidence = 0.95  # Fixed: Set confidence for context flow
            self.context["acc_no"] = text
            self.context["flow"] = "card_reason"
            response = "Please mention the reason (lost / stolen / fraud)."

        elif self.context.get("flow") == "card_reason":
            intent = "card_block"
            confidence = 0.95  # Fixed: Set confidence for context flow
            acc_no = self.context.get("acc_no")
            self.context.clear()
            response = self.process_card_block(acc_no, text)

        # ================= NLU =================
        else:
            nlu_result = router.process(text)
            intent = nlu_result.get("top_intent", "llm")
            confidence = nlu_result.get("confidence", 0.0)

            if intent == "greetings":  # Changed from "greet"
                response = "Hello 👋 Welcome to BankBot. How can I assist you today?"

            elif intent == "check_balance":
                self.context["flow"] = "balance_acc"
                response = "Sure 😊 Please provide your account number."

            elif intent == "transfer_money":
                self.context["flow"] = "transfer_from"
                response = "💸 Please enter sender account number."

            elif "block" in lower_text and "card" in lower_text:
                intent = "card_block"
                confidence = 0.90  # Fixed: Set confidence for keyword match
                self.context["flow"] = "card_acc"
                response = "🔒 Please provide your account number to block the card."

            else:
                intent = "llm"
                confidence = 0.85  # Fixed: Set confidence for LLM fallback
                response = self.ask_llm(text)

        # ================= SAVE CHAT (IMPORTANT) =================
        # Get username from context, or use "guest" as default
        username = self.context.get("username", "guest")

        # Save to database with proper intent and confidence
        save_chat(
            username=username,
            query=text,
            intent=intent,
            confidence=confidence
        )

        return response

    # ================= PROCESS METHODS =================

    def process_balance(self, acc_no, password):
        account = get_account(acc_no)
        if not account:
            return "❌ Account does not exist."

        _, _, _, balance, pwd_hash = account
        if not verify_password(password, pwd_hash):
            return "❌ Incorrect password."

        return f"✅ Your available balance is ₹{balance}"

    def process_transfer(self, from_acc, to_acc, amount, password):
        return transfer_money(from_acc, to_acc, amount, password)

    def process_card_block(self, acc_no, reason):
        account = get_account(acc_no)
        if not account:
            return "❌ Account not found."

        return (
            f"✅ Card linked to account **{acc_no}** has been successfully blocked.\n\n"
            f"📝 Reason: {reason}\n"
            "📞 Please contact customer support to request a new card."
        )

    def ask_llm(self, text):
        response = llm.invoke([
            SystemMessage(
                content=(
                    "You are a helpful AI assistant for a banking application. "
                    "Answer clearly and confidently. "
                    "Do not mention knowledge cutoff dates or disclaimers."
                )
            ),
            HumanMessage(content=text)
        ])
        return response.content