# Chatbot-for-GMU-university-
The GMU Chatbot aims to bridge the gap by providing a centralized AI-powered assistant that can respond to natural language queries. The chatbot will provide direct links to relevant GMU websites and offer conversational responses to clarify user doubts.
 
## Introduction
 
### Problem Definition
George Mason University (GMU) provides a variety of resources through multiple websites. However, navigating these fragmented websites often leads to inefficiency and frustration for users. Many students and professionals are unaware of the specific resources available to them.
 
The GMU Chatbot addresses this issue by offering a centralized, AI-powered assistant. This chatbot responds to natural language queries and provides direct links to relevant GMU resources along with conversational responses to clarify user doubts.
 
---
 
## Project Objectives
 
1. **Intent Recognition**: Use Natural Language Processing (NLP) to identify user intent and extract key phrases from queries.
2. **Efficient Information Retrieval**: Deliver accurate and concise answers with relevant GMU resource links.
3. **Enhanced Accessibility**: Improve discoverability of GMU resources for students and professionals.
 
---
 
## Functionalities
 
### Accept User Queries in Natural Language
Users can type questions in English, such as:
- *"Where can I find information about financial aid?"*
- *"How do I apply for on-campus housing?"*
 
### Identify Keywords or Intent in the Query
The chatbot uses NLP techniques to:
- Extract keywords (e.g., "financial aid").
- Identify the intent behind the query.
 
### Provide Relevant Website Links
Based on extracted keywords, the chatbot searches a predefined dataset of GMU resource links and suggests the most relevant website for further information.
 
### Conversational Responses
To enhance user experience, the chatbot also provides additional conversational replies. For example:
- **User**: *"Where can I find information about financial aid?"*
- **Chatbot**: *"You can visit the GMU Financial Aid page for detailed information. Would you like help with the application process?"*
 
---
 
## Implementation Details
 
### NLP Model for Intent Recognition
- **Model Architecture**: A Sequence-to-Sequence (Seq2Seq) model implemented with PyTorch.
- **Dataset**: A custom dataset of user queries paired with corresponding intents, manually created.
- **Preprocessing**: Queries were tokenized and padded for uniform input size.
- **Training Configuration**:
  - Training Duration: 30 epochs
  - Loss Function: Categorical cross-entropy
  - Training Loss: Achieved a low training loss of 0.062
- **Tools**: Model training conducted in Google Colab with GPU acceleration.
 
### Keyword Extraction and Database Mapping
- **Keyword Matching**: Standard NLP libraries (e.g., NLTK) were used to extract keywords from queries.
- **Database Design**:
  - Website URLs for various GMU services.
  - Descriptions and tags for efficient mapping.
  - Metadata for conversational context and summaries.
 
### Conversational Response System
- **Response Generation**: Based on intent and keywords, the chatbot generated conversational responses using predefined templates. For example:
  - **Query**: *"I want to know about student health."
  - **Response**:
    - *Summary*: Know everything about student healthcare services - appointments, patient portal, SHS forms, events/news, office hours, emergency contact information, and more.
    - *Link*: [https://shs.gmu.edu/](https://shs.gmu.edu/)
 
---
 
## Results
- **Training Loss**: The Seq2Seq model achieved a low training loss of 0.066 over 30 epochs, ensuring robust performance.
- **Training Duration**: Approximately 22 seconds per epoch.
 
---
 
## Getting Started
 
### Prerequisites
- Python 3.7+
- Libraries: PyTorch, NLTK, NumPy, Pandas
- Access to Google Colab (optional for training)
 
### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/gmu-chatbot.git
   ```
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
 
### Running the Chatbot
1. Train the model (if needed):
   ```bash
   python train_model.py
   ```
2. Start the chatbot:
   ```bash
   python chatbot.py
   ```
3. Interact with the chatbot by typing queries in the console.
 
---
 
## Future Enhancements
- **Voice Query Support**: Enable users to interact via voice commands.
- **Multi-Language Support**: Extend chatbot functionality to other languages.
- **Advanced Search**: Incorporate advanced algorithms for improved search relevance.
 
---
 
## License
This project is licensed under the MIT License.
 
---
 
## Acknowledgments
We thank George Mason University for providing resources and support for this project.
