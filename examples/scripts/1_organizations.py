# examples/scripts/1_organizations.py
from open_ksa import organizations


def main():
    # Call the organizations function and print the result
    orgs = organizations()
    print("\n\nList of Organizations:\n")
    for org in orgs["content"][:10]:
        print(org["name"])


if __name__ == "__main__":
    main()
