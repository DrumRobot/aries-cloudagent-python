import asyncio
import requests
import os
import sys

API_URL = "http://host.docker.internal:3000/urls"
NGROK_URL = "http://ngrok:4040/api/tunnels"

variables = [
    "GENESIS_URL",
    "LEDGER_URL",
    "PUBLIC_TAILS_URL",
]

if __name__ == "__main__":
    json_data = requests.get(NGROK_URL).json()
    ngrok_info = next(item for item in json_data["tunnels"] if item["name"] == "nginx")
    os.environ["AGENT_ENDPOINT"] = ngrok_info["public_url"]

    response = requests.get(API_URL)
    json_data = response.json()

    for name in variables:
        tails_info = next((item for item in json_data if item["id"] == name), {})
        value = tails_info.get("value")
        if value:
            print(f"{name}, {value}")
            os.environ[name] = value

    args = ["--aip", "10", "--revocation", "--seed", "testseed000000000000000000000001"]
    sys.argv = [sys.argv[0]] + args

    from runners.faber import main
    from runners.agent_container import arg_parser

    parser = arg_parser(ident="faber", port=8020)
    args = parser.parse_args()

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
