from openai import OpenAI

from utils import embedding_model, summarize_policy_model, get_response_format, system_prompt

# gpt client
gpt_client = OpenAI()

def get_vector_from_query(query):

    query_embedding = gpt_client.embeddings.create(
        input = query,
        model = embedding_model
        )

    query_vector = query_embedding.data[0].embedding

    return query_vector

def query_vector_embeddings(query, top_k_rag, client, query_collection, parliament, party = None, constituency = None, member = None, output_field = []):
    # convert query to vector
    query_vector = get_vector_from_query(query)

    variables = {
        'parliament': parliament,
        'party': party,
        'constituency': constituency,
        'name': member
    }

    filters = " AND ".join([f"{key}=='{value}'" if isinstance(value, str) else f"{key}=={value}" for key, value in variables.items() if value is not None])

    # Perform a similarity search with automatic query embedding
    retrieved_metadata = client.search(query_collection, data=[query_vector], 
                                       filter=filters, limit = top_k_rag, 
                                       output_fields = output_field) 

    return retrieved_metadata[0]

# gpt structured formats output

def summarize_policy_positions(query, uoa, summaries):
    completion = gpt_client.chat.completions.create(
        model=summarize_policy_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ','.join([f"[Summary {i+1}: {summaries[i]}]" for i in range(len(summaries))])},
        ],
        response_format=get_response_format(query, uoa)
        )
    
    output = eval(completion.choices[0].message.content)
    return output['policy_position'], output['policy_points']