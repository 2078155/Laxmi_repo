import pandas as pd
from src.GENAI.EvaluationEngineAsync import Feedback
from src.daolayer import MongoReadWrite
from datetime import datetime
import time
import asyncio
from src.LlmLayer.LiteLLM import LiteLlm
from src.GENAI.DataGenerator import obj1


class EvaluationAsync:
    mongo_obj = MongoReadWrite.mongoReadWrite()

    def evaluation_calculation(self, input_param):
        try:
            botData_df = pd.DataFrame(list(self.mongo_obj.read_data('bot_question_answer', input_param['datasetId'], 'datasetId')))
            data_df = botData_df[['question', 'answer', 'context']]
            evaluation_data = {
                'jobId': input_param['jobID'],
                'datasetId': input_param['datasetId'],
                'executionStatus': 'Inprogress',
                'executedBy': input_param['executedBy'],
                'projectName': input_param['projectName'],
                'executedDate': datetime.utcnow().isoformat(),
                'modifiedDate': datetime.utcnow().isoformat(),
                'errorMessage': 'evaluation started successfully',
                'executionType': input_param['executionType'],
                'executionTime': 0,
                'totalRecords': len(data_df)
            }
            execution_Id = self.mongo_obj.write_single_data('evaluation', evaluation_data)
            overall_start_time = time.time()
            async_execution = asyncio.run(self.asyncExeFun(data_df, input_param['jobID'], execution_Id))
            overall_execution_time = (time.time() - overall_start_time) * 100
            self.mongo_obj.write_multiple_data('evaluationRecord', async_execution)
            evaluation_data['executionStatus'] = 'Completed'
            evaluation_data['errorMessage'] = 'Metrics evaluation completed successfully.'
            evaluation_data['modifiedDate'] = datetime.utcnow().isoformat()
            evaluation_data['executionTime'] = overall_execution_time
            self.mongo_obj.update_single_data('evaluation', evaluation_data, execution_Id)
        except Exception as e:
            import sys
            print('in error', str(e), sys.exc_info()[-1].tb_lineno)
            if input_param['jobID'] is not None:
                try:
                    evaluation_detail = self.mongo_obj.read_single_data_with_filter('evaluation', input_param['jobID'],
                                                                                    'jobId')
                    evaluation_detail['executionStatus'] = 'Failed'
                    evaluation_detail['errorMessage'] = 'Evaluation Calculation failed with error: ' + str(e)
                    self.mongo_obj.update_single_data('evaluation', evaluation_detail, evaluation_detail['_id'])
                except Exception as exc:
                    print('in error', str(exc), sys.exc_info()[-1].tb_lineno)

    # async def asyncExeFun(self, data_df, jobId, execution_Id):
    #     tasks = [self.process_feedback(data_df, i, jobId, execution_Id) for i in range(data_df.shape[0])]
    #     combineList = await asyncio.gather(*tasks)
    #     return combineList

    async def asyncExeFun(self, data_df, jobId, execution_Id):
        combineList = []
        for i in range(data_df.shape[0]):
            feedback = await self.process_feedback(data_df, i, jobId, execution_Id)
            combineList.append(feedback)
            await asyncio.sleep(1)  # Delays for 1 second between each process_feedback call
        return combineList

    async def process_feedback(self, data_df, i, jobId, execution_Id):
        start_time = time.time()
        evaluation = self.mongo_obj.read_single_data_with_filter('evaluation', jobId, 'jobId')
        dataset = self.mongo_obj.read_single_data('dataset', evaluation['datasetId'])
        model = dataset['model']
        feedback = Feedback(data_df['question'].iloc[i], data_df['answer'].iloc[i], data_df['context'].iloc[i],model)
        all_metrices = await asyncio.gather(
            feedback.qs_relevance(),feedback.qa_relevance(), feedback.groundedness(),
            feedback.coherence(), feedback.summarization(), feedback.concisenses(),
            feedback.controversiality(), feedback.correctness(), feedback.criminality(),
            feedback.harmfulness(), feedback.helpfulness(), feedback.insensitivity(),
            feedback.maliciousness(), feedback.misogyny(), feedback.sentiment(),
            feedback.stereotype(),
            feedback.pii_detection(),
            feedback.toxicity(), feedback.language_match(),feedback.llm_controversiality()
        )
        print("Done Feedback calls")
        truLens_metrics = {
            'qs_relevance': all_metrices[0][0],
            'qs_relevance_reason': all_metrices[0][1],
            'qa_relevance': all_metrices[1][0],
            'qa_relevance_reason': all_metrices[1][1],
            'groundedness': all_metrices[2][0],
            'groundedness_reason': all_metrices[2][1],
            'coherence': all_metrices[3][0],
            'coherence_reason': all_metrices[3][1],
            'summarization': all_metrices[4][0],
            'summarization_reason': all_metrices[4][1],
            'conciseness': all_metrices[5][0],
            'conciseness_reason': all_metrices[5][1],
            'controversiality': all_metrices[6][0],
            'controversiality_reason': all_metrices[6][1],
            'correctness': all_metrices[7][0],
            'correctness_reason': all_metrices[7][1],
            'criminality': all_metrices[8][0],
            'criminality_reason': all_metrices[8][1],
            'harmfulness': all_metrices[9][0],
            'harmfulness_reason': all_metrices[9][1],
            'helpfulness': all_metrices[10][0],
            'helpfulness_reason': all_metrices[10][1],
            'insensitivity': all_metrices[11][0],
            'insensitivity_reason': all_metrices[11][1],
            'maliciousness': all_metrices[12][0],
            'maliciousness_reason': all_metrices[12][1],
            'misogyny': all_metrices[13][0],
            'misogyny_reason': all_metrices[13][1],
            'sentiment': all_metrices[14][0],
            'sentiment_reason': all_metrices[14][1],
            'stereotype': all_metrices[15][0],
            'stereotype_reason': all_metrices[15][1],
            'pii_detection': all_metrices[16][0],
            'pii_detection_reason': all_metrices[16][1],
            'toxicity': all_metrices[17],
            'language_match': all_metrices[18],
            'llm_contoversiality':all_metrices[19],
            'latency':feedback.latency,
            'totalcost':feedback.totalcost
        }
        end_time = (time.time() - start_time) * 100
        combined_data = {
            'jobId': jobId,
            'executionId': execution_Id,
            'question': data_df['question'].iloc[i],
            'answer': data_df['answer'].iloc[i],
            'context': data_df['context'].iloc[i],
            'metrics': truLens_metrics,
            'executionTime': end_time
        }
        return combined_data

    def download_evaluation_data(self, input_param):
        try:
            evaluation_output = list(self.mongo_obj.read_data('evaluationRecord', input_param['jobId'], 'jobId'))
            final_list = [
                {
                    'Question': doc['question'],
                    'Answer': doc['answer'],
                    'Context': doc['context'],
                    'qs_relevance': doc['metrics']['qs_relevance'],
                    'qs_relevance_reason': doc['metrics']['qs_relevance_reason'],
                    'qa_relevance': doc['metrics']['qa_relevance'],
                    'qa_relevance_reason': doc['metrics']['qa_relevance_reason'],
                    'groundedness': doc['metrics']['groundedness'],
                    'groundedness_reason': doc['metrics']['groundedness_reason'],
                    'coherence': doc['metrics']['coherence'],
                    'coherence_reason': doc['metrics']['coherence_reason'],
                    'summarization': doc['metrics']['summarization'],
                    'summarization_reason': doc['metrics']['summarization_reason'],
                    'conciseness': doc['metrics']['conciseness'],
                    'conciseness_reason': doc['metrics']['conciseness_reason'],
                    'controversiality': doc['metrics']['controversiality'],
                    'controversiality_reason': doc['metrics']['controversiality_reason'],
                    'correctness': doc['metrics']['correctness'],
                    'correctness_reason': doc['metrics']['correctness_reason'],
                    'criminality': doc['metrics']['criminality'],
                    'criminality_reason': doc['metrics']['criminality_reason'],
                    'harmfulness': doc['metrics']['harmfulness'],
                    'harmfulness_reason': doc['metrics']['harmfulness_reason'],
                    'helpfulness': doc['metrics']['helpfulness'],
                    'helpfulness_reason': doc['metrics']['helpfulness_reason'],
                    'insensitivity': doc['metrics']['insensitivity'],
                    'insensitivity_reason': doc['metrics']['insensitivity_reason'],
                    'maliciousness': doc['metrics']['maliciousness'],
                    'maliciousness_reason': doc['metrics']['maliciousness_reason'],
                    'misogyny': doc['metrics']['misogyny'],
                    'misogyny_reason': doc['metrics']['misogyny_reason'],
                    'sentiment': doc['metrics']['sentiment'],
                    'sentiment_reason': doc['metrics']['sentiment_reason'],
                    'stereotype': doc['metrics']['stereotype'],
                    'stereotype_reason': doc['metrics']['stereotype_reason'],
                    'pii_detection': doc['metrics']['pii_detection'],
                    'pii_detection_reason': doc['metrics']['pii_detection_reason'],
                    'toxicity': doc['metrics']['toxicity'],
                    'language_match': doc['metrics']['language_match'],
                    'llm_contoversiality':doc['metrics']['llm_contoversiality'],
                    'latency':doc['metrics']['latency'],
                    'totalcost':doc['metrics']['totalcost']
                }
                for doc in evaluation_output
            ]
            result_df = pd.DataFrame(final_list,
                                     columns=['Question', 'Answer', 'Context', 'qs_relevance', 'qs_relevance_reason',
                                              'qa_relevance', 'qa_relevance_reason', 'groundedness',
                                              'groundedness_reason',
                                              'coherence', 'coherence_reason', 'summarization', 'summarization_reason',
                                              'conciseness', 'conciseness_reason', 'controversiality',
                                              'controversiality_reason',
                                              'correctness', 'correctness_reason', 'criminality', 'criminality_reason',
                                              'harmfulness', 'harmfulness_reason', 'helpfulness', 'helpfulness_reason',
                                              'insensitivity', 'insensitivity_reason', 'maliciousness',
                                              'maliciousness_reason',
                                              'misogyny', 'misogyny_reason', 'sentiment', 'sentiment_reason',
                                              'stereotype', 'stereotype_reason',
                                              'pii_detection',
                                              'pii_detection_reason',
                                              'toxicity', 'language_match','llm_contoversiality','latency','totalcost'
                                              ])

            # WhylogsConfig_obj = WhylogsConfig()
            # WhylogsConfig_obj.whyLogOutput(result_df, input_param['jobId'])
            return result_df
        except Exception as e:
            import sys
            print('in error', str(e), sys.exc_info()[-1].tb_lineno)

