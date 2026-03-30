from providers.llm import LLMProvider


def main():
    llm = LLMProvider()
    response = llm.generate_response("Say hello in one short sentence.")
    print("LLM response:", response)

if __name__ == "__main__":
    main()