from google.cloud import bigquery
import os
from datetime import datetime
from flask_caching import Cache
import logging

from app_initialization import app, server

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up cache
cache = Cache(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',  # Ensure this directory exists and is writable
    'CACHE_DEFAULT_TIMEOUT': 86400  # Cache timeout in seconds (24 hours)
})

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tokens/gcp_token.json"

gbq_client = bigquery.Client()

def load_speech_agg():

    job = gbq_client.query("""
        WITH CTE AS (
            SELECT *, count_speeches - count_pri_questions AS count_only_speeches
            FROM `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`
            ),
            by_parl AS (
            SELECT member_name, CAST(parliament as STRING) as parliament, member_party, member_constituency,
                    ROUND(CASE 
                        WHEN SUM(count_sittings_present) = 0 THEN 0 
                        ELSE SUM(count_pri_questions) / SUM(count_sittings_present) 
                    END, 2) AS questions_per_sitting,
                    CAST(CASE 
                        WHEN SUM(count_only_speeches) = 0 THEN 0 
                        ELSE SUM(count_words) / SUM(count_only_speeches) 
                    END AS INTEGER) AS words_per_speech,
                    ROUND(CASE 
                        WHEN SUM(count_sittings_present) = 0 THEN 0 
                        ELSE SUM(count_only_speeches) / SUM(count_sittings_present) 
                    END, 2) AS speeches_per_sitting
            FROM CTE
            GROUP BY parliament, member_party, member_constituency, member_name
            ), 
            all_parl AS (
            SELECT member_name, 'All' AS parliament, member_party, 'All' as member_constituency,
                    ROUND(CASE 
                        WHEN SUM(count_sittings_present) = 0 THEN 0 
                        ELSE SUM(count_pri_questions) / SUM(count_sittings_present) 
                    END, 2) AS questions_per_sitting,
                    CAST(CASE 
                        WHEN SUM(count_only_speeches) = 0 THEN 0 
                        ELSE SUM(count_words) / SUM(count_only_speeches) 
                    END AS INTEGER) AS words_per_speech,
                    ROUND(CASE 
                        WHEN SUM(count_sittings_present) = 0 THEN 0 
                        ELSE SUM(count_only_speeches) / SUM(count_sittings_present) 
                    END, 2) AS speeches_per_sitting
            FROM CTE
            WHERE member_constituency is not NULL
            GROUP BY member_name, member_party
            ),
            speech_agg as(
            SELECT * FROM by_parl
            UNION ALL
            SELECT * FROM all_parl
            )
            select *
            from speech_agg
            where member_constituency is not NULL

    """)
    result = job.result()
    return result.to_dataframe()

def load_speech_summary():

    job = gbq_client.query("""
                       SELECT parliament, `date`, member_party, b.member_constituency, member_name, speech_summary, topic_assigned
                        FROM `singapore-parliament-speeches.prod_mart.mart_speech_summaries`
                        left join (select * from `singapore-parliament-speeches.prod_mart.mart_speeches`) as a
                        left join (select distinct member_name, member_party, parliament, member_constituency from `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`) as b
                        using (member_name, member_party, parliament)
                        using (speech_id)
                        where b.member_constituency is not NULL
    """)
    result = job.result()
    return result.to_dataframe()

# Data fetching function
def get_data():
    data = cache.get('all_data')
    if data is not None:
        logger.debug(f"{datetime.now()} - Data fetched from cache")
        return data
    else:
        logger.debug(f"{datetime.now()} - Data fetched from BigQuery")
        speech_agg_df = load_speech_agg()
        speech_summary_df = load_speech_summary()
        data = {
            'speech_agg': speech_agg_df,
            'speech_summaries': speech_summary_df
        }
        cache.set('all_data', data, timeout=86400)
        return data