## writes the code that it got from plugin_developer_agent to the files
## work in progress
import os
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def write_code(code, file_name):
    file_path = Path(os.path.join(os.getcwd(), file_name))
    with open(file_path, "w") as f:
        f.write(code)
    print(f"File {file_name} written successfully.")
    return file_path

def write_config(config):
    write_code(config, "config.json")
    print("config.json written successfully.")

def write_index_d_ts(index_d_ts):
    write_code(index_d_ts, "index.d.ts")
    print("index.d.ts written successfully.")

def write_index_ts(index_ts):
    write_code(index_ts, "index.ts")
    print("index.ts written successfully.")

def write_utils_hf_js(utils_hf_js):
    write_code(utils_hf_js, "utils/hf.js")
    print("utils/hf.js written successfully.")

def write_plugin_code(plugin_code):
    write_code(plugin_code, "plugin.js")
    print("plugin.js written successfully.")


if __name__ == "__main__":
    plugin_code = json.load(open("plugin_code.json"))
    config = plugin_code["config"]
    index_d_ts = plugin_code["index.d.ts"]
    index_ts = plugin_code["index.ts"]
    utils_hf_js = plugin_code["utils/hf.js"]
    write_config(config)
    write_index_d_ts(index_d_ts)
    write_index_ts(index_ts)
    write_utils_hf_js(utils_hf_js)    
    write_plugin_code(plugin_code["plugin.js"])
    print("All files written successfully.")
