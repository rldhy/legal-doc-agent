from agent.llm import get_llm
from agent.rag import answer_question, print_answer
from agent.retrieval import retrieve_documents
from agent.vectorstore import load_vector_store


def run_query(query: str) -> None:

    if len(query) == 0:
        print("Please provide a query")
        return

    vector_store = load_vector_store()
    llm = get_llm()

    retrieved = retrieve_documents(
        vector_store=vector_store,
        query=query
    )

    answer = answer_question(
        query=query,
        documents=retrieved,
        llm=llm,
    )

    print(f"\nQuestion: {query}\n")

    print_answer(
        answer=answer,
        documents=retrieved,
    )
