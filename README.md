# BankBot AI – Intelligent Banking FAQ Chatbot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![AI](https://img.shields.io/badge/AI-NLP-green)
![LLM](https://img.shields.io/badge/LLM-Transformer--Based-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Project Description

**BankBot AI** is an intelligent, AI-powered chatbot designed to handle **banking-related frequently asked questions (FAQs)** efficiently.
The system leverages **Natural Language Processing (NLP)** and **Large Language Models (LLMs)** to provide accurate, human-like responses to user queries while supporting non-banking conversational queries through LLM integration.

This project is developed as part of an **Infosys Certification / Academic Project**, demonstrating real-world application of AI, NLP, and LLM technologies in the banking domain. It also supports **local execution**, making it suitable for evaluation, learning, and further enhancement.

---

## Features

* Conversational chatbot for banking FAQs
* Intelligent intent detection and response handling
* LLM-powered responses for non-banking and general queries
* Admin-ready architecture for future analytics and monitoring
* Configurable and extensible LLM integration
* User-friendly web interface
* Secure and modular project structure

---

## Techniques Used

### Natural Language Processing (NLP)

* Text preprocessing and normalization
* Intent recognition
* Query classification (banking vs non-banking)
* Semantic understanding of user input

### Prompt Engineering

* Structured prompts for controlled LLM responses
* Context-aware question handling
* Optimized prompts to reduce hallucinations

### LLM-based Text Generation

* Dynamic response generation using transformer-based LLMs
* Contextual and conversational reply generation
* Fallback handling using LLMs for unmatched queries

---

## Tech Stack

### Programming Language

* Python

### Libraries / Frameworks

* Streamlit – Web application framework
* Pandas – Data handling
* NLP libraries (NLTK / spaCy – as applicable)
* SQL / File-based storage for FAQs and logs

### AI / ML Technologies

* Natural Language Processing (NLP)
* Machine Learning–based intent handling
* Large Language Models (LLMs)

---

## LLM Details

* Uses **transformer-based Large Language Models** (LLMs)
* Supports models such as:

  * OpenAI-compatible LLMs
  * Other transformer-based text generation models

**LLM Configuration**
The LLM layer is **fully configurable**, allowing:

* Easy replacement or upgrade of the LLM
* Switching between different providers or models
* Custom prompt and response tuning

This ensures flexibility, scalability, and future-proofing of the system.

---

## Project Structure

```
BankBot-AI/
│
├── app.py                     # Main Streamlit application
├── database/
│   ├── db.py                  # Database initialization
│   ├── bank_crud.py           # FAQ and data operations
│   └── security.py            # Authentication utilities
│
├── dialogue_manager/
│   └── dialogue_handler.py    # Chatbot logic and flow
│
├── models/
│   └── llm_handler.py         # LLM integration and configuration
│
├── data/
│   └── banking_faqs.csv       # Banking knowledge base
│
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

---

## Installation Steps

1. Clone the repository

   ```
   git clone https://github.com/nithyashrekokkonda123-pixel/Infosys-_Project-BankBot-AI-Chatbot-for-Banking-FAQs.git
   ```

2. Navigate to the project directory

   ```
   cd Infosys-_Project-BankBot-AI-Chatbot-for-Banking-FAQs
   ```

3. Create a virtual environment (optional but recommended)

   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

4. Install dependencies

   ```
   pip install -r requirements.txt
   ```

---

## How to Run the Project Locally

1. Ensure all dependencies are installed
2. Run the Streamlit application

   ```
   streamlit run app.py
   ```
3. Open the provided local URL in your browser
4. Start interacting with **BankBot AI** through the chat interface

---

## Certification Use Case

This project is ideal for:

* **Infosys Certification Submission**
* Academic project evaluation
* Demonstrating practical implementation of:

  * AI & NLP concepts
  * LLM integration
  * Prompt engineering
  * Real-world chatbot systems

It showcases end-to-end development, from problem statement to deployment-ready solution.

---

## License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute this project for educational and non-commercial purposes.

---

**Developed as an AI-powered banking assistant with a focus on real-world applicability, scalability, and certification standards.**

