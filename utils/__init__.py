# party colors for speeches graph

PARTY_COLOURS = {
    "All": '#FF964F', # pastel orange
    "PAP": "#FF9999",  # pastel red
    "PSP": "#FFFF99",  # pastel yellow
    "WP": "#99CCFF",  # pastel blue
    "NMP": "#BAFFC9",  # pastel green
    "SPP": "#D8BFD8"  # pastel purple
}

ETHNIC_COLOURS = {
    "chinese": "#FFCBDB",  # pastel pink
    "malay": "#6CD0D0",  # pastel turquoise
    "indian": "#B1DDC9",  # pastel green
    "others": "#FBCEB1",  # pastel orange
}

# Define parliaments
parliaments = {
    "12th (2011-2015)": '12',
    "13th (2016-2020)": '13',
    "14th (2020-present)": '14',
    "All": 'All'
}

parliament_parties = {
    '12': ['NMP', 'PAP', 'PSP', 'WP'],
    '13': ['NMP', 'PAP', 'WP'],
    '14': ['NMP', 'SPP', 'PAP', 'WP']
}

parliament_sessions = sorted(parliaments.keys(), reverse=True)

# query embedding model
embedding_model = "text-embedding-3-small"

# get prompts for GPT summary

system_prompt = "You are a non-partisan political analyst who will take summaries of speeches made in the Singapore parliament on a given topic and by a given party, and then output an overall summary of the party's political position on the issue and policy points that support your view."

def get_response_format(query):

    policy_position_description = f"""Policy summary of the party's position on the issue '{query}' in no more than 150 words. Note that summaries passed to you are the top-k results from a RAG model and may not always be relevant to the query. I will provide a step by step guide to guide your summarization. 

    1. Determine if a summary is DIRECTLY relevant to the query and use a strict criteria for what is accepted. For example a query about 'regulation of social media for children' must only accept summaries that are related to both social media and children, not one or the other. 

    2. Gather all summaries that are deemed relevant and from these, extract information on the party's policy position on the query. Summarize these into a coherent policy approach by the party on the issue.

    3. In the case of esoteric queries, it may be the case that all summaries retrieved are irrelevant. In this case, do not hallucinate non-existent policy positions. Instead, return an output saying 'Your query did not return any relevant speeches, please try again with something less specific.'

    Writing style: Begin your summary with 'The Party's position on...' and the party should always be referred to as 'the Party' rather than the name of the party or 'the Government'. Write in concise manner, avoiding tautology.
    """

    policy_point_description = "Based on the summary you have created for the description of the policy position, list short, specific bullet point examples of no more than 5 policies that justify your decision to summarize the party's policies in that specific way."

    retrieval_rate_description = "A list of booleans corresponding to each summary that was passed to the model indicating if that summary was accepted as relevant or not. Output should be wrapped by parentheses and take the form of a Python list. For example [True, False, True, ...]"

    response_format = {"type": "json_schema", "json_schema": {"name": "response", "strict": True, "schema": {"type": "object", "properties": {"policy_position": {"type": "string", "description": policy_position_description}, "policy_points": {"type": "string", "description": policy_point_description}, "retrieval_rate": {"type": "string", "description": retrieval_rate_description}}, "required": ["policy_position", "policy_points", "retrieval_rate"], "additionalProperties": False}}}

    return response_format

# top k for RAG

top_k_rag = 50

[x for x, y in zip(summaries, eval(output[2])) if y][-1:]