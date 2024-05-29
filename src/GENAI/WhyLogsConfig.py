import os
import whylogs as why
from langkit.config import check_or_prompt_for_api_keys
from whylogs.api.writer.whylabs import WhyLabsWriter
from datetime import datetime, timezone
from src.config_file import WHYLABS_DEFAULT_ORG_ID, WHYLABS_DEFAULT_DATASET_ID, WHYLABS_API_KEY, OPENAI_API_KEY


class WhylogsConfig:
    def whyLogOutput(self, result_df, jobId):
        try:
            drop_columns=['Question', 'Answer', 'Context', 'qs_relevance_reason',
                         'qa_relevance_reason', 'groundedness_reason',
                          'coherence_reason', 'summarization_reason',
                          'conciseness_reason', 'controversiality_reason',
                          'correctness_reason', 'criminality_reason',
                          'harmfulness_reason', 'helpfulness_reason',
                          'insensitivity_reason', 'maliciousness_reason',
                          'misogyny_reason', 'sentiment_reason',
                          'stereotype_reason', 'pii_detection_reason']
            output_df = result_df.drop(drop_columns, axis=1)
            os.environ["WHYLABS_DEFAULT_ORG_ID"] = WHYLABS_DEFAULT_ORG_ID
            os.environ["WHYLABS_DEFAULT_DATASET_ID"] = WHYLABS_DEFAULT_DATASET_ID
            os.environ["WHYLABS_API_KEY"] = WHYLABS_API_KEY
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            check_or_prompt_for_api_keys()
            why.init(force_local=True)
            profile = why.log(output_df, name=jobId, dataset_timestamp=datetime.now(tz=timezone.utc)).profile()
            writer = WhyLabsWriter()
            writer.write(profile)
            print(writer.write(profile))
            return

        except Exception as e:
            import sys
            print('in error', str(e), sys.exc_info()[-1].tb_lineno)
