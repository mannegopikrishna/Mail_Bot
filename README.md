# Mail Generation Bot

Mail Generator Assistant is a conversational bot designed to assist users in generating professional emails based on their input. The bot utilizes advanced natural language processing (NLP) capabilities provided by the Google Gemini model and is built with LangChain, Chainlit, and Python.

### Features

- Email Generation :  Automatically generates email content based on user input.
- Conversation Memory :  Maintains context across interactions to ensure coherent and relevant responses.
- Async Handling :  Supports asynchronous processing for fast and efficient response times.

### Prerequisites
- Python
- Chainlit
- Langchain

### Steps to set up the project

- Install the Depedencies and Setup the Project using Below Command.

     ` poetry install `

- make sure all dependencies are installed.
- Change to Poetry Shell

    ` Poetry shell`

- Make Sure the Virtual environment is Activated

- Configure Environment Variables:

  Create a .env file in the root directory of the project.

  Add your Google API key to the .env file

  `GOOGLE_API_KEY=your_google_api_key_here`

- Run the chainlit script

  `chainlit run app.py -w --port=5100 --host=127.0.0.1`

  `chainlit run filename.py -w`
  or
  `poetry run chainlit run app.py`