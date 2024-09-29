import autogen
from user_proxy_webagent import UserProxyWebAgent
from groupchatweb import GroupChatManagerWeb
import asyncio
from system_prompts import gather_info_prompt, plugin_developer_prompt

config_list = [
    {
        "model": "gpt-4o",
    }
]
llm_config_assistant = {
    "model":"gpt-4o",
    "temperature": 0,
    "config_list": config_list,
}
llm_config_proxy = {
    "model":"gpt-4o",
    "temperature": 0,
    "config_list": config_list,
}


#############################################################################################
# this is where you put your Autogen logic, here I have a 2 agents
class AutogenChat():
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.creator = autogen.AssistantAgent(
            name="creator",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=5,
            system_message=gather_info_prompt,
            description="This is a web agent that can help the user to share the website url and things they want to notarize."
        )
        self.plugin_developer = autogen.AssistantAgent(
            name="plugin_developer",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=5,
            system_message=plugin_developer_prompt,
            description="once the information is gathered, this agnet can develop tlsn extension plugin"
        )

        self.user_proxy = UserProxyWebAgent( 
            name="user_proxy",
            human_input_mode="ALWAYS", 
            system_message="""you are a helpful assistant, help the user to share the website url and things they want to notarize.""",
            max_consecutive_auto_reply=5,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )

        # add the queues to communicate 
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

        self.groupchat = autogen.GroupChat(agents=[self.user_proxy, self.creator, self.plugin_developer], messages=[], max_round=20)
        self.manager = GroupChatManagerWeb(groupchat=self.groupchat, 
            llm_config=llm_config_assistant,
            human_input_mode="ALWAYS" )     

    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.manager,
            clear_history=True,
            message=message
        )


