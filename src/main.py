from agents.quey_understand_agent.agent import QueryUnderstandAgent


def main():
    agent = QueryUnderstandAgent()
    queries = [
        "We had a forklift accident at the warehouse.",
        "What are the legal requirements for chemical storage?",
    ]

    for query in queries:
        response = agent.detect_intent(query)
        print("Query:", query)
        print("Detected intent:", response)

if __name__ == "__main__":
    main()