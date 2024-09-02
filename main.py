import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from system_prompts import gather_info_prompt, plugin_developer_prompt
load_dotenv()  # take environment variables from .env.


config_list = [
    {
        'model':  'gpt-4', #gpt-3.5-turbo'
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 120,
    "seed": 42, # for caching. once task is run it caches the response,
    "config_list": config_list,
    "temperature": 0 #lower temperature more standard lesss creative response, higher is more creative

}
assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}
)

# Start the chat
user_proxy = autogen.UserProxyAgent(
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

gather_info_assistant = autogen.AssistantAgent(
    name="gather_info_assistant",
    llm_config=llm_config,
    system_message=gather_info_prompt,
)


plugin_developer = autogen.AssistantAgent(
    name="TLSN_plugin_developer",
    llm_config=llm_config,
    system_message=plugin_developer_prompt,
)

def main():
    chat_results = user_proxy.initiate_chats([
        {
            "recipient": gather_info_assistant,
            "message": "I want to build a tlsn plugin for a website.",
            "silent": False,
            "summary_method": "reflection_with_llm"
        },
        {
            "recipient": plugin_developer,
            "message": "with the info gathered in previous step and read info.json. and the plugin dev code you have. Modify the code that you have with the info that user provided to you.",
            "silent": False,
            "summary_method": "reflection_with_llm"
        },
    ])

    for i, chat_res in enumerate(chat_results):
        print(f"*****{i}th chat*******:")
        print(chat_res.summary)
        print("Human input in the middle:", chat_res.human_input)
        print("Conversation cost: ", chat_res.cost)
        print("\n\n")

if __name__ == "__main__":
    main()