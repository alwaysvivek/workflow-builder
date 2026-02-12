from enum import Enum

class ActionType(str, Enum):
    CLEAN = "clean"
    SUMMARIZE = "summarize"
    KEYPOINTS = "keypoints"
    SIMPLIFY = "simplify"
    EXAMPLES = "analogy"
    CLASSIFY = "classify"
    SENTIMENT = "tone"

PROMPTS = {
    ActionType.CLEAN: """
    You are a text cleaner. Your task is to correct grammar, fix spelling errors, remove unnecessary whitespace, and ensure the text is coherent and professional, without changing its original meaning or tone.
    
    Input Text:
    {input_text}
    """,

    ActionType.SUMMARIZE: """
    You are a summarizer. Your task is to provide a concise summary of the input text, capturing the main ideas and crucial details while discarding redundant information.
    
    Input Text:
    {input_text}
    """,

    ActionType.KEYPOINTS: """
    You are an analyst. Your task is to extract the key points from the input text and present them as a clear, bulleted list.
    
    Input Text:
    {input_text}
    """,

    ActionType.SIMPLIFY: """
    You are a simplifier. Your task is to rewrite the input text in simple, plain language that is easy for a general audience (including non-experts) to understand. Avoid jargon and complex sentence structures.
    
    Input Text:
    {input_text}
    """,

    ActionType.EXAMPLES: """
    You are a creative teacher. Your task is to provide a clear analogy or real-world example that illustrates the concepts discussed in the input text, making it easier to grasp.
    
    Input Text:
    {input_text}
    """,

    ActionType.CLASSIFY: """
    You are a classifier. Your task is to categorize the input text into a single, specific category that best describes its content (e.g., specific specific topic, intent, or domain). Return ONLY the category name.
    
    Input Text:
    {input_text}
    """,

    ActionType.SENTIMENT: """
    You are a sentiment analyst. Your task is to analyze the emotional tone of the input text. Describe the sentiment (e.g., positive, negative, neutral, urgent, sarcastic) and briefly explain why.
    
    Input Text:
    {input_text}
    """
}
