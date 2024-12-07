# TLSN-plugin-gen
Generate TLSNotary plugins using agents

## description
This project implements a FastAPI-based web application that uses Autogen to create a group chat of AI agents for information gathering and processing, specifically designed to generate TLSNotary plugins.


## Prerequisites

- Python 3.7+
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone git@github.com:hackertron/TLSN-plugin-gen.git
   cd TLSN-plugin-gen
   ```

2. Install the required dependencies:
   ```
   pip install fastapi uvicorn python-dotenv openai autogen
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
   This will start the server on `http://0.0.0.0:8000`.

2. Connect to the WebSocket endpoint:
   - The WebSocket endpoint is available at `ws://localhost:8000/ws/{chat_id}`.
   - Replace `{chat_id}` with a unique identifier for each chat session.

3. Send messages to the WebSocket to interact with the AutogenChat system.

## Project Structure

- `main.py`: The main FastAPI application file containing the WebSocket endpoint and Autogen chat logic.
- `autogen_group_chat.py`: Contains the `AutogenChat` class that sets up the group chat with different AI agents.
- `user_proxy_webagent.py`: Implements the `UserProxyWebAgent` class for handling user interactions in the web context.
- `groupchatweb.py`: Contains the `GroupChatManagerWeb` class for managing the group chat.
- `system_prompts.py`: Contains system prompts for different agents, including:
  - `info_gather_prompt`: For gathering initial information about the website and notarization target.
  - `request_gather_prompt`: For filtering relevant requests.
  - `response_gather_prompt`: For gathering and processing responses.
  - `plugin_developer_prompt`: For generating the TLSNotary plugin based on gathered information.

## Customization

You can customize the behavior of the AI agents by modifying the system prompts and agent configurations in the `AutogenChat` class and `system_prompts.py` file.

## Notes

- This application uses the GPT-4 model. Make sure you have access to it in your OpenAI account.
- The application is set up to use a custom model called "gpt-4o-mini" and "gpt-4o". You may need to adjust these to use standard OpenAI models or your own fine-tuned models.

## Security Warning

This application doesn't implement any authentication or authorization. Be cautious when deploying it in a production environment. Implement proper security measures before exposing the application to the internet.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 jayssj11

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

