gather_info_prompt="""
You will ask user for the website for which the tlsn plugin needs to be generated. You will ask for 
website url, api url if available, some sample requests and response that are made on the website. What thing you want to notarize using tlsn.

Example:

Input: https://twitter.com/

Output:

Twitter Profile

Notarize ownership of a twitter profile

Input: https://twitter.com/username

Output:

Twitter Profile

you will store the information in a json and ask the user for confirmation if the json and information is correct. then write a python code
to save that json in a file called info.json
"""

plugin_developer_prompt="""
you are TLSNotary browser extension plugin developer. I will give you the existing boilerplate code along with examples. 

You can use it to generate TLSNotary plugins.
first you have utils/hf.js code below
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

next is index.d.ts
declare module 'main' {
    // Extism exports take no params and return an I32
    export function start(): I32;
    export function two(): I32;
    export function parseTwitterResp(): I32;
    export function three(): I32;
    export function config(): I32;
}

declare module 'extism:host' {
    interface user {
        redirect(ptr: I64): void;
        notarize(ptr: I64): I64;
    }
}

next is index.ts, this is the main source code for the plugin. 
import icon from '../assets/icon.png';
import config_json from '../config.json';
import { redirect, notarize, outputJSON, getCookiesByHost, getHeadersByHost } from './utils/hf.js';

/**
 * Plugin configuration
 * This configurations defines the plugin, most importantly:
 *  * the different steps
 *  * the user data (headers, cookies) it will access
 *  * the web requests it will query (or notarize)
 */
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

/**
 * Implementation of the first (start) plugin step
  */
export function start() {
  if (!isValidHost(Config.get('tabUrl'))) {
    redirect('https://x.com');
    outputJSON(false);
    return;
  }
  outputJSON(true);
}

/**
 * Implementation of step "two".
 * This step collects and validates authentication cookies and headers for 'api.x.com'.
 * If all required information, it creates the request object.
 * Note that the url needs to be specified in the `config` too, otherwise the request will be refused.
 */
export function two() {
  const cookies = getCookiesByHost('api.x.com');
  const headers = getHeadersByHost('api.x.com');

  if (
    !cookies.auth_token ||
    !cookies.ct0 ||
    !headers['x-csrf-token'] ||
    !headers['authorization']
  ) {
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

/**
 * This method is used to parse the Twitter response and specify what information is revealed (i.e. **not** redacted)
 * This method is optional in the notarization request. When it is not specified nothing is redacted.
 *
 * In this example it locates the `screen_name` and excludes that range from the revealed response.
 */
export function parseTwitterResp() {
  const bodyString = Host.inputString();
  const params = JSON.parse(bodyString);

  if (params.screen_name) {
    const revealed = `"screen_name":"${params.screen_name}"`;
    const selectionStart = bodyString.indexOf(revealed);
    const selectionEnd =
      selectionStart + revealed.length;
    const secretResps = [
      bodyString.substring(0, selectionStart),
      bodyString.substring(selectionEnd, bodyString.length),
    ];
    outputJSON(secretResps);
  } else {
    outputJSON(false);
  }
}

/**
 * Step 3: calls the `notarize` host function
 */
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

below is example config.json, you will need users help to fill it properly.
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
"""