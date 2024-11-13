from google.cloud import bigquery
import os

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tokens/gcp_token.json"

gbq_client = bigquery.Client()

def load_speech_agg():

    job = gbq_client.query("""
        WITH cte_speeches AS (
            SELECT *, count_speeches - count_pri_questions AS count_only_speeches
            FROM `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`
            ),
cte_readability as (
SELECT member_name, parliament, 206.835 - 1.015*(count_speeches_words / count_speeches_sentences) - 84.6*(count_speeches_syllables/count_speeches_words) as readability_score
FROM `singapore-parliament-speeches.prod_mart.mart_speeches`
where not is_vernacular_speech
and not is_primary_question
and count_speeches_words>0
and member_constituency is not NULL
and 'Speaker' not in UNNEST(member_appointments)
),
by_parl_speeches AS (
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
FROM cte_speeches
GROUP BY parliament, member_party, member_constituency, member_name
), 
by_parl_join_readability as (
select *
from by_parl_speeches
left join (select member_name, CAST(parliament as STRING) as parliament, round(avg(readability_score), 1) as readability_score
from cte_readability
group by member_name, parliament)
using (member_name, parliament)
),
all_parl_speeches AS (
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
FROM cte_speeches
WHERE member_constituency is not NULL
GROUP BY member_name, member_party
),
all_parl_join_readability as (
select *
from all_parl_speeches
left join (select member_name, 'All' as parliament, round(avg(readability_score), 1) as readability_score
from cte_readability
group by member_name)
using (member_name, parliament)
),
speech_agg as(
SELECT * FROM by_parl_join_readability
UNION ALL
SELECT * FROM all_parl_join_readability
)
select *
from speech_agg
where member_constituency is not NULL

    """)
    result = job.result()
    return result.to_dataframe()

def load_speech_summary():
    # limit to 5000 for now since in app this is very slow and prevents the page from generating
    job = gbq_client.query("""
                       SELECT parliament, `date`, member_party, member_constituency, member_name, speech_summary, topic_assigned
                        FROM `singapore-parliament-speeches.prod_mart.mart_speech_summaries`
                        left join (select * from `singapore-parliament-speeches.prod_mart.mart_speeches`)
                        using (speech_id)
                        where member_constituency is not NULL
                        limit 5000
    """)
    result = job.result()
    return result.to_dataframe()

def load_topics():

    job = gbq_client.query("""
                       with cte as (SELECT parliament, `date`, member_party, b.member_constituency, member_name, topic_assigned
                        FROM `singapore-parliament-speeches.prod_mart.mart_speech_topics`
                        left join (select * from `singapore-parliament-speeches.prod_mart.mart_speeches`) as a
                        left join (select distinct member_name, member_party, parliament, member_constituency from `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`) as b
                        using (member_name, member_party, parliament)
                        using (speech_id)
                        where b.member_constituency is not NULL
                        ),
                        by_parl as(
                        select cast(parliament as STRING) as parliament, member_party, member_constituency, member_name, topic_assigned, count(*) as count_speeches
                        from cte
                        group by parliament, member_party, member_constituency, member_name, topic_assigned
                        ),
                        all_parl as(
                        select 'All' as parliament, member_party, 'All' as member_constituency, member_name, topic_assigned, count(*) as count_speeches
                        from cte
                        group by member_party, member_name, topic_assigned
                        )
                        select * from by_parl
                        union all
                        select * from all_parl

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
                        SELECT member_name, 'All' as parliament, member_party, 'All' as member_constituency, sum(count_sittings_total) as sittings_total, sum(count_sittings_present) as sittings_present, sum(count_sittings_spoken) as sittings_spoken
                                                FROM `singapore-parliament-speeches.prod_agg.agg_speech_metrics_by_member`
                                                group by member_name, member_party
                        ),
                        participation as(
                        SELECT * FROM by_parl
                        UNION ALL
                        SELECT * FROM all_parl
                        )
                        select member_name, parliament, member_party, member_constituency, round(100*sittings_present/nullif(sittings_total, 0), 1) as attendance, 
                        round(100*sittings_spoken/nullif(sittings_present, 0), 1) as participation
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

def load_questions():
    job = gbq_client.query("""
                       with by_parl_questions as (SELECT member_name, cast(parliament as STRING) as parliament, member_constituency, member_party, ministry_addressed, count(*) as count_questions
FROM `singapore-parliament-speeches.prod_mart.mart_speeches`
where is_primary_question
and member_party is not NULL
and ministry_addressed is not NULL
group by member_name, parliament, member_constituency, member_party, ministry_addressed
),
all_parl_questions as (SELECT member_name, 'All' as parliament, 'All' as member_constituency, member_party, ministry_addressed, count(*) as count_questions
FROM `singapore-parliament-speeches.prod_mart.mart_speeches`
where is_primary_question
and member_party is not NULL
and ministry_addressed is not NULL
group by member_name, member_party, ministry_addressed
)
select * from by_parl_questions
union all
select * from all_parl_questions
    """)
    result = job.result()
    return result.to_dataframe()


def load_gpt_prompts():
    job = gbq_client.query("""
                       SELECT system_message, output_summary_description, output_topic_description 
FROM `singapore-parliament-speeches.prod_dim.dim_speech_summaries`
order by batch_id desc
limit 1
    """)
    result = job.result()
    return result.to_dataframe()

def load_speech_lengths():
    job = gbq_client.query("""
                       SELECT count_speeches_words
FROM `singapore-parliament-speeches.prod_mart.mart_speeches`
WHERE topic_type_name not like "%Correction by Written Statements%"
AND topic_type_name not like "%Bill Introduced%"
AND member_name != ''
AND member_name != 'Speaker'
    """)
    result = job.result()
    return result.to_dataframe()
    
