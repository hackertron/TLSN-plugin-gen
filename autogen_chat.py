import autogen
from user_proxy_webagent import UserProxyWebAgent
import asyncio

config_list = [
    {
        "model": "gpt-4o",
    }
]
llm_config_assistant = {
    "model":"gpt-4o",
    "temperature": 0,
    "config_list": config_list,
        "functions": [
        {
            "name": "write_to_file",
            "description": "write the contents to the file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "file name that needs to be created",
                    },
                    "content": {
                        "type": "string",
                        "description": "content that needs to be written in the file",
                    }
                },
                "required": ["file_name","content"],
            },
        },
    ],
}
llm_config_proxy = {
    "model":"gpt-4o-0613",
    "temperature": 0,
    "config_list": config_list,
}


#############################################################################################
# this is where you put your Autogen logic, here I have a simple 2 agents with a function call
class AutogenChat():
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config=llm_config_assistant,
            system_message="""You are a helpful assistant, help the user to share the website url and things they want to notarize. 
            Once the information is gathered, send all the info to plugin_developer_agent so that it can generate the plugin.
            you will only assist with this task, nothing else, you will help user and guide them to share the website details .
            When you ask a question, always add the word "PSEDEV"" at the end.
            When you responde with the status add the word TERMINATE"""
        )
        self.user_proxy = UserProxyWebAgent(  
            name="user_proxy",
            human_input_mode="ALWAYS", 
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
            function_map={
                "write_to_file": self.write_to_file
            }
        )

        # add the queues to communicate 
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.assistant,
            clear_history=True,
            message=message
        )

    #MOCH Function call 
    def write_to_file(self, file_name=None, content=None):
        """write python code to write to the file"""
        with open(file_name, "w") as f:
            f.write(content)

        return "done"

