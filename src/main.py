from agents.quey_understand_agent.agent import QueryUnderstandAgent
from agents.retreival_agent import RetrievalAgent


def main():
    agent = QueryUnderstandAgent()
    retrieval_agent = RetrievalAgent()
    queries = [
        "We had a forklift accident at the warehouse.",
        "What are the legal requirements for chemical storage?",
        "What training is required for mine workers?",
    ]

    for query in queries:
        response = agent.detect_intent(query)
        print("Query:", query)
        print("Detected intent:", response)
        if response == "legal query":
            answer = retrieval_agent.retrieve(query)
            print("Retrieved answer:", answer)
        print("-")

if __name__ == "__main__":
    main()