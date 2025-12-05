from urllib.request import urlopen, Request
import sys
import json

# List of sponsors that shouldn't be shown in the sponsor section. Eg. accounts we suspect are related to scams.
HIDE = {"ADS-Fund"}

def main(token: str):
    sponsors = []
    after = "null"
    has_next_page = True
    while has_next_page:
        query = """
        query {
            organization(login: "Amulet-Team") {
                sponsorshipsAsMaintainer(first: 100, after: AFTER) {
                    nodes {
                        sponsorEntity {
                            ... on User { login }
                            ... on Organization { login }
                        }
                        privacyLevel
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
        sponsor_node = response["data"]["organization"]["sponsorshipsAsMaintainer"]
        sponsors.extend(
            user["sponsorEntity"]["login"]
            for user in sponsor_node["nodes"]
            if user["privacyLevel"] != "PRIVATE" and user["sponsorEntity"] is not None and user["sponsorEntity"]["login"] not in HIDE
        )
        page_info = sponsor_node["pageInfo"]
        after = f'"{page_info["endCursor"]}"'
        has_next_page = page_info["hasNextPage"]
    with open("sponsors.json", "w") as f:
        json.dump(sorted(sponsors), f)


if __name__ == "__main__":
    main(sys.argv[1])
