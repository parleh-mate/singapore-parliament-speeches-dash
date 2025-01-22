import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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

# member metrics scatterplot min and max size parameters in pixels
SIZE_MIN = 5
SIZE_MAX = 40

# Define parliaments
parliaments = {
    "12th (2011-2015)": '12',
    "13th (2016-2020)": '13',
    "14th (2020-present)": '14',
    "All": 'All'
}

parliaments_bills = {
    "10th (2002-2006)": '10',
    "11th (2006-2011)": '11',
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

# member metrics options
member_metrics_options = {
    'speeches per sitting': 'speeches_per_sitting',
    'words per speech': 'words_per_speech',
    'readability score': 'readability_score',
    'attendance': 'attendance',
    'participation': 'participation',
    'questions per sitting': 'questions_per_sitting'
}

# query embedding model
embedding_model = "text-embedding-3-small"

summarize_policy_model = "gpt-4o"

# get prompts for GPT summary

try_again_message = 'Your query did not return any relevant entries, please try again with something else or perhaps something less specific.'

system_prompt = "You are a non-partisan political analyst who will take policy positions summarized from speeches (in bullet points) made by politician(s) in the Singapore parliament on a given topic and by a given party, and then output an overall summary of the party or politican's political position on the issue and policy points that support your view."

def get_response_format(query, uoa):

    policy_position_description = f"""Description of the party, constituency, or politician's position on the issue '{query}' in no more than 150 words. Note that policy positions passed to you are the top-k results from a RAG model and may not always be relevant to the query. I will provide a step by step guide to guide your summarization. 

    1. Determine if a policy position is DIRECTLY relevant to the query and use a strict criteria for what is accepted. For example a query about 'regulation of social media for children' must only accept a policy position that is related to both social media and children, not one or the other.

    2. Gather all policy positions that are deemed relevant to the query and summarize these into a coherent policy approach by the party or politician on the issue.

    3. In the case of esoteric queries, it may be the case that no policy positions retrieved are relevant. In this case, do not hallucinate non-existent policy positions. Instead, return an output saying '{try_again_message}'

    Writing style: Begin your summary with 'The [insert unit of analysis]'s position on...'. The unit of analysis can either be the Party, Constituency, or MP. In this case the unit of analysis is the {uoa}. Use the third-person like 'the Party', 'the Constituency', or 'the MP' when referring to them rather than their actual names. Write in concise manner, avoiding tautology. On rare occassions, a Party or Constituency has no united position on an issue due to the party whip being lifted. State this if this is the case.
    """

    policy_point_description = """Based on the description you have created for the policy position, list specific bullet point examples of no more than 5 policies that justify your decision to describe the policy position in that specific way. You should not take wholesale the policy points that were passed into the model, rather, look at the policy positions from all the speeches that were passed, and construct coherent policies that were suggested that support your description above.

    Note that a policy is always a call to action or a suggestion and not just a statement. For example, 'Management of the financial crisis has been prudent' is a statement and not a call to action. Only list policies and not merely statements.

    If no relevant policy positions were retrieved, return nothing.
    """

    response_format = {"type": "json_schema", "json_schema": {"name": "response", "strict": True, "schema": {"type": "object", "properties": {"policy_position": {"type": "string", "description": policy_position_description}, "policy_points": {"type": "string", "description": policy_point_description}}, "required": ["policy_position", "policy_points"], "additionalProperties": False}}}

    return response_format

# top k for RAG

top_k_rag_policy_positions = 10
top_k_rag_bill_summaries = 50

policy_positions_rag_index = "singapore-speeches-positions"
bill_summaries_rag_index = "singapore-bill-summaries"

# bills page size
bills_page_size = 10

# policy position thresholds
position_threshold_low = 70
position_threshold_high = 2000

# generate sitemap

# site priorities

sitemap_priorities = {"/": '1',
                      "policy_positions": '0.9',
                      "bill_summaries": '0.8',
                      "member_metrics": '0.7',
                      "topics_questions": '0.5',
                      "demographics": '0.5',
                      "methodology": '0.5',
                      "about": '0.5',
                      "404": '0'}

urls = [{'loc': i, 'lastmod': str(datetime.datetime.now().date()),'changefreq': 'daily','priority': sitemap_priorities[i]} for i in sitemap_priorities.keys()]

def generate_sitemap():
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in urls:
        url_element = SubElement(urlset, 'url')
        loc = SubElement(url_element, 'loc')
        loc.text = url['loc']

        lastmod = SubElement(url_element, 'lastmod')
        lastmod.text = url['lastmod']

        changefreq = SubElement(url_element, 'changefreq')
        changefreq.text = url['changefreq']

        priority = SubElement(url_element, 'priority')
        priority.text = url['priority']

    # Pretty-print the XML
    rough_string = tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    return pretty_xml