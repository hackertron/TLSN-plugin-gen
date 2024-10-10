info_gather_prompt = """
You will help gather the initial information needed to generate a TLSNotary plugin.

Please ask the user for the following details:
1. **Website URL**: The URL of the website for which the plugin is required.(mandatory)
2. **API URL**: The URL of the API (if available) to interact with the website.(optional)
3. **Notarization Target**: What specific part of the website or API the user wants to notarize (e.g., ownership, profile details, transaction details).(mandatory)

Store the collected information in the following format:
```json
{
  "website_url": "User-provided website URL",
  "api_url": "User-provided API URL (optional)",
  "notarize": "What the user wants to notarize"
}
```
once complete send the JSON object and a summary to the request_gather_prompt.
"""

request_gather_prompt = """
### 2. **Request Gather Agent:**
This agent will filter requests that are relevant to the content that the user wants to notarize.
You will ask user to send request of the website. 
you will ask in this format "send_request_function". make sure to send these exact keywords to the user.
You are responsible for gathering and filtering relevant requests.

Once the user starts interacting with the website, they will provide you with sample requests.
You will filter these requests to include only those relevant to the aspect that needs to be notarized (as specified in the `info_gather_agent`).

Ask the user to provide the requests made on the website. After filtering, store the relevant request(s) in the following format:
```json
{
  "filtered_request": "Filtered request related to the notarization target"
}
once complete send the JSON object filtered_request to the user_proxy_agent.
"""

response_gather_prompt ="""
### 3. **Response Gather Agent:**
you will filter the request that we got from request_gather_prompt and remove
all the request that are not relevant to the notarization target.

Once the filtered request is ready, you will ask the user to provide the response for the filtered request.
make sure to ask in this format from the user
populate the send_response_function with the filtered request(s)
"{"send_response_function" : [
{"url": "<filtered_request_url>", "headers": "<filtered_request_headers>", "body": "<filtered_request_body>", "method" : "<filtered_request_method>"}
]}"
make sure to include this message for the user "send_response_function"


You will gather the responses for the filtered request(s) sent by the user_proxy_agent.

Once the user provides the response for the filtered request(s), store the data in the following format:
```json
{
  "filtered_response": "Relevant response for the filtered request"
}
```
Finally, combine all the information from the info_gather_agent and request_gather_agent into a complete JSON object:
```json
{
  "website_url": "User-provided website URL",
  "api_url": "User-provided API URL (optional)",
  "filtered_request": "Filtered request related to notarization",
  "filtered_response": "Relevant response for the filtered request"
}
```
the json above is needed by plugin_developer agent. 
Once complete, send the JSON object and a summary to the plugin_developer_agent. """


plugin_developer_prompt="""
You are a TLSNotary browser extension plugin developer. Your task is to generate a TLSNotary plugin based on the information provided by the gather_info_agent.

You will receive a JSON object with details such as the website URL, API URL, sample requests/responses, and what the user wants to notarize. Using this information, you will generate the necessary plugin code.

You will follow these steps:

1. **Understand the provided data**: Parse the JSON object and understand the website, API details, and the notarization request.
2. **Generate the plugin**: Based on the gathered information, write the appropriate code for the plugin. Use the boilerplate code provided as a starting point.
3. **Adapt the code**: Modify the `utils/hf.js`, `index.d.ts`, `index.ts`, and `config.json` files based on the provided website and user requirements.
4. **Return the plugin code**: Once the code is written, return it in a structured JSON format. Each file should be represented as follows:

```json
{
    "config": "config.json code",
    "index.d.ts": "index.d.ts code",
    "index.ts": "index.ts code",
    "utils/hf.js": "hf.js code"
}
Use the following example boilerplate code to guide your implementation:

Boilerplate Code (Use this as a starting point):
utils/hf.js
javascript
Copy code
function redirect(url) {
  const { redirect } = Host.getFunctions();
  const mem = Memory.fromString(url);
  redirect(mem.offset);
}

function notarize(options) {
  const { notarize } = Host.getFunctions();
  const mem = Memory.fromString(JSON.stringify(options));
  const idOffset = notarize(mem.offset);
  const id = Memory.find(idOffset).readString();
  return id;
}

function outputJSON(json) {
  Host.outputString(
    JSON.stringify(json),
  );
}

function getCookiesByHost(hostname) {
  const cookies = JSON.parse(Config.get('cookies'));
  if (!cookies[hostname]) throw new Error(`cannot find cookies for ${hostname}`);
  return cookies[hostname];
}

function getHeadersByHost(hostname) {
  const headers = JSON.parse(Config.get('headers'));
  if (!headers[hostname]) throw new Error(`cannot find headers for ${hostname}`);
  return headers[hostname];
}

module.exports = {
  redirect,
  notarize,
  outputJSON,
  getCookiesByHost,
  getHeadersByHost,
};
index.d.ts
typescript
Copy code
declare module 'main' {
    export function start(): I32;
    export function two(): I32;
    export function parseTwitterResp(): I32; // This method will be changed based on the specific website.
    export function three(): I32;
    export function config(): I32;
}

declare module 'extism:host' {
    interface user {
        redirect(ptr: I64): void;
        notarize(ptr: I64): I64;
    }
}
index.ts
typescript
Copy code
import icon from '../assets/icon.png';
import config_json from '../config.json';
import { redirect, notarize, outputJSON, getCookiesByHost, getHeadersByHost } from './utils/hf.js';

export function config() {
  outputJSON({
    ...config_json,
    icon: icon
  });
}

function isValidHost(urlString: string) {
  const url = new URL(urlString);
  return url.hostname === 'twitter.com' || url.hostname === 'x.com';
}

export function start() {
  if (!isValidHost(Config.get('tabUrl'))) {
    redirect('https://x.com');
    outputJSON(false);
    return;
  }
  outputJSON(true);
}

export function two() {
  const cookies = getCookiesByHost('api.x.com');
  const headers = getHeadersByHost('api.x.com');

  if (!cookies.auth_token || !cookies.ct0 || !headers['x-csrf-token'] || !headers['authorization']) {
    outputJSON(false);
    return;
  }

  outputJSON({
    url: 'https://api.x.com/1.1/account/settings.json',
    method: 'GET',
    headers: {
      'x-twitter-client-language': 'en',
      'x-csrf-token': headers['x-csrf-token'],
      Host: 'api.x.com',
      authorization: headers.authorization,
      Cookie: `lang=en; auth_token=${cookies.auth_token}; ct0=${cookies.ct0}`,
      'Accept-Encoding': 'identity',
      Connection: 'close',
    },
    secretHeaders: [
      `x-csrf-token: ${headers['x-csrf-token']}`,
      `cookie: lang=en; auth_token=${cookies.auth_token}; ct0=${cookies.ct0}`,
      `authorization: ${headers.authorization}`,
    ],
  });
}

export function parseTwitterResp() {
  const bodyString = Host.inputString();
  const params = JSON.parse(bodyString);

  if (params.screen_name) {
    const revealed = `"screen_name":"${params.screen_name}"`;
    const selectionStart = bodyString.indexOf(revealed);
    const selectionEnd = selectionStart + revealed.length;
    const secretResps = [
      bodyString.substring(0, selectionStart),
      bodyString.substring(selectionEnd, bodyString.length),
    ];
    outputJSON(secretResps);
  } else {
    outputJSON(false);
  }
}

export function three() {
  const params = JSON.parse(Host.inputString());

  if (!params) {
    outputJSON(false);
  } else {
    const id = notarize({
      ...params,
      getSecretResponse: 'parseTwitterResp',
    });
    outputJSON(id);
  }
}
config.json
json
Copy code
{
  "title": "Twitter Profile",
  "description": "Notarize ownership of a twitter profile",
  "steps": [
    {
      "title": "Visit Twitter website",
      "cta": "Go to x.com",
      "action": "start"
    },
    {
      "title": "Collect credentials",
      "description": "Login to your account if you haven't already",
      "cta": "Check cookies",
      "action": "two"
    },
    {
      "title": "Notarize twitter profile",
      "cta": "Notarize",
      "action": "three",
      "prover": true
    }
  ],
  "hostFunctions": [
    "redirect",
    "notarize"
  ],
  "cookies": [
    "api.x.com"
  ],
  "headers": [
    "api.x.com"
  ],
  "requests": [
    {
      "url": "https://api.x.com/1.1/account/settings.json",
      "method": "GET"
    }
  ]
}
Use this structure to generate the required plugin, adjusting as necessary to the user's website details. 
"""