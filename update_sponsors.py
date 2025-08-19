from urllib.request import urlopen, Request
import sys
import json

# List of sponsors that shouldn't be shown in the sponsor section
HIDE = {"ADS-Fund"}

def main(token: str):
    sponsors = []
    after = "null"
    has_next_page = True
    while has_next_page:
        query = """
        query {
            organization (login:"Amulet-Team") {
                sponsors(first: 100, after: AFTER) {
                    nodes {
                        ... on User { login }
                        ... on Organization { login }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
        """.replace("AFTER", after)
        req = urlopen(Request(
            "https://api.github.com/graphql",
            json.dumps({"query": query}).encode(),
            headers={
                "Authorization": "bearer " + token
            }
        ))
        with req as f:
            response = json.loads(f.read().decode())
        sponsor_node = response["data"]["organization"]["sponsors"]
        sponsors.extend(user["login"] for user in filter(lambda s: s["login"] not in HIDE, sponsor_node["nodes"]))
        page_info = sponsor_node["pageInfo"]
        after = f'"{page_info["endCursor"]}"'
        has_next_page = page_info["hasNextPage"]
    with open("sponsors.json", "w") as f:
        json.dump(sorted(sponsors), f)


if __name__ == "__main__":
    main(sys.argv[1])
