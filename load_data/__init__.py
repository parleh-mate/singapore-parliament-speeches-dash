from google.cloud import bigquery
import os
from datetime import datetime, timedelta
from flask_caching import Cache
import logging
import pytz

from app_initialization import app, server

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# set time
gmt_plus_8 = pytz.timezone('Asia/Singapore')

# Set up cache
cache = Cache(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',  # Ensure this directory exists and is writable
    'CACHE_TIME': datetime.now(gmt_plus_8) # Cache today's datetime
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

def load_participation():
    job = gbq_client.query("""
                       with by_parl as (
                        SELECT member_name, cast(parliament as STRING) as parliament, member_party, member_constituency, sum(count_sittings_total) as sittings_total, sum(count_sittings_present) as sittings_present, sum(count_sittings_spoken) as sittings_spoken
                                                FROM `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`
                                                group by member_name, parliament, member_party, member_constituency
                        ),
                        all_parl as(
                        SELECT member_name, 'All' as parliament, member_party, member_constituency, sum(count_sittings_total) as sittings_total, sum(count_sittings_present) as sittings_present, sum(count_sittings_spoken) as sittings_spoken
                                                FROM `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`
                                                group by member_name, member_party, member_constituency
                        ),
                        participation as(
                        SELECT * FROM by_parl
                        UNION ALL
                        SELECT * FROM all_parl
                        )
                        select member_name, parliament, member_party, member_constituency, round(sittings_present/nullif(sittings_total, 0), 2) as attendance, 
                        round(sittings_spoken/nullif(sittings_present, 0), 2) as participation
                        from participation
                        WHERE member_constituency is not NULL
    """)
    result = job.result()
    return result.to_dataframe()

def load_demographics():
    job = gbq_client.query("""
                    SELECT member_name, parliament, party, member_constituency, member_ethnicity, gender, member_birth_year, extract(year from first_parl_date) - member_birth_year as year_age_entered
                    FROM `singapore-parliament-speeches.prod_dim.dim_members`
                    left join (SELECT member_name, parliament, member_constituency, min(`date`) as first_parl_date
                        FROM `singapore-parliament-speeches.prod_mart.mart_attendance`
                        where member_constituency is not null
                        group by member_name, parliament, member_constituency)
                    using (member_name)
                    order by member_name, parliament
""")
    result = job.result()
    return result.to_dataframe()

# Data fetching function
def get_data():
    data = cache.get('all_data')
    time_loaded = cache.get('time_loaded')

    current_time = datetime.now(gmt_plus_8)
    # Create a datetime object for 1:00 AM today
    today_1am = current_time.replace(hour=1, minute=0, second=0, microsecond=0)
    # If current time is before 1:00 AM, go to the previous day's 1:00 AM
    if current_time < today_1am:
        previous_1am = today_1am - timedelta(days=1)
    else:
        previous_1am = today_1am   

    if data is not None and time_loaded>previous_1am:
        logger.debug(f"{datetime.now()} - Data fetched from cache")
        return data
    else:
        logger.debug(f"{datetime.now()} - Data fetched from BigQuery")
        data = {
            'participation': load_participation(),
            'speech_agg': load_speech_agg(),
            'speech_summaries': load_speech_summary(),
            'demographics': load_demographics()
        }
        cache.set('all_data', data)
        cache.set('time_loaded', datetime.now(gmt_plus_8))
        return data
    
