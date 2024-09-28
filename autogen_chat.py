import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
import asyncio
from system_prompts import gather_info_prompt, plugin_developer_prompt

config_list = [
    {
        'model': 'gpt-4',
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 120,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0
}

class AutogenChat:
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "last_n_messages": 3,
                "work_dir": "code",
                "use_docker": False,
            },
            llm_config=llm_config,
            system_message="""Reply TERMINATE if the task has been solved at full satisfaction
            otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
        )

        self.gather_info_assistant = autogen.AssistantAgent(
            name="gather_info_assistant",
            llm_config=llm_config,
            system_message=gather_info_prompt,
        )

        self.plugin_developer = autogen.AssistantAgent(
            name="TLSN_plugin_developer",
            llm_config=llm_config,
            system_message=plugin_developer_prompt,
        )

    async def start(self, message):
        chat_results = await self.user_proxy.a_initiate_chats([
            {
                "recipient": self.gather_info_assistant,
                "message": message,
                "silent": False,
                "summary_method": "reflection_with_llm"
            },
            {
                "recipient": self.plugin_developer,
                "message": """With the info gathered in the previous step and read info.json, and the plugin dev code you have.
                Modify the code that you have with the info that user provided to you. Finally write the plugin code into the respective files using python.
                Make sure to ask user for confirmation""",
                "silent": False,
                "summary_method": "reflection_with_llm"
            },
        ])

        for i, chat_res in enumerate(chat_results):
            await self.client_receive_queue.put(f"*****{i}th chat*******:")
            await self.client_receive_queue.put(chat_res.summary)
            await self.client_receive_queue.put(f"Human input in the middle: {chat_res.human_input}")
            await self.client_receive_queue.put(f"Conversation cost: {chat_res.cost}")
            await self.client_receive_queue.put("\n\n")

    async def get_human_input(self, prompt: str) -> str:
        await self.client_receive_queue.put(prompt)
        reply = await self.client_sent_queue.get()
        return "exit" if reply and reply == "DO_FINISH" else reply

# Modify UserProxyAgent to use our custom get_human_input method
autogen.UserProxyAgent.get_human_input = AutogenChat.get_human_input