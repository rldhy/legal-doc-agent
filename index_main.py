from pathlib import Path

from agent.index import index_documents


def main():
    project_path = Path.cwd()
    documents_dir = Path(f"{project_path}/data/documents")
    index_documents(
        documents_dir=documents_dir
    )

if __name__ == "__main__":
    main()
