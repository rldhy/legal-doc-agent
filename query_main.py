from agent.query import run_query


def main():
    print("Legal Document Agent")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue

        if query.lower() in {"quit", "exit"}:
            break

        run_query(
            query=query
        )


if __name__ == "__main__":
    main()