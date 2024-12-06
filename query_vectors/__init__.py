from pinecone import Pinecone
from openai import OpenAI
import os

from utils import embedding_model, get_response_format, system_prompt, rag_index

# load api keys if in development

if os.environ.get('ENVIRONMENT') == 'development':
    # pinecone api key
    os.environ['PINECONE_API_KEY'] = open("tokens/pinecone_token.txt", 'r').readlines()[0]
    # gpt key
    os.environ["OPENAI_API_KEY"] = open("tokens/gpt_api_token.txt", 'r').readlines()[0]

# pinecone client
pc = Pinecone()
index = pc.Index(rag_index)

# gpt client
gpt_client = OpenAI()

def get_vector_from_query(query):

    query_embedding = gpt_client.embeddings.create(
        input = query,
        model = embedding_model
        )

    query_vector = query_embedding.data[0].embedding

    return query_vector

def query_vector_embeddings(query, top_k_rag, parliament, party, constituency = None, member = None):
    # convert query to vector
    query_vector = get_vector_from_query(query)

    variables = {
        'parliament': parliament,
        'party': party,
        'constituency': constituency,
        'name': member
    }

    filters = {key: value for key, value in variables.items() if value is not None}

    # Perform a similarity search with automatic query embedding
    response = index.query(
        vector=query_vector,
        top_k=top_k_rag,
        include_metadata=True,
        filter=filters
    )

    # fetch summaries
    responses = response['matches']    
    return [i['metadata']['policy_positions'] for i in responses]

# gpt structured formats output

def summarize_policy_positions(query, uoa, summaries):
    completion = gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ','.join([f"[Summary {i+1}: {summaries[i]}]" for i in range(len(summaries))])},
        ],
        response_format=get_response_format(query, uoa)
        )
    
    output = eval(completion.choices[0].message.content)
    return output['policy_position'], output['policy_points']