import json

from agents.answer_generator_agent import AnswerGeneratorAgent
from agents.llm_reasoning import LLMReasoningAgent
from agents.quey_understand_agent.agent import QueryUnderstandAgent
from agents.retreival_agent import RetrievalAgent


def main():
    agent = QueryUnderstandAgent()
    retrieval_agent = RetrievalAgent()
    reasoning_agent = LLMReasoningAgent()
    answer_agent = AnswerGeneratorAgent()
    queries = [
        "What training is required for mine workers?",
    ]
    # queries = [
    #     "We had a forklift accident at the warehouse.",
    #     "What are the legal requirements for chemical storage?",
    #     "What training is required for mine workers?",
    # ]

    for query in queries:
        response = agent.detect_intent(query)
        print("Query:", query)
        print("Detected intent:", response)
        if response == "legal query":
            retrieval_payload = json.loads(retrieval_agent.retrieve(query))
            reasoning = reasoning_agent.answer(query, retrieval_payload)
            final_answer = answer_agent.generate(query, reasoning)
            print("Retrieved payload:", json.dumps(retrieval_payload, indent=2))
            print("Reasoned answer:", reasoning)
            print("Final answer:", final_answer)
        print("-")

if __name__ == "__main__":
    main()