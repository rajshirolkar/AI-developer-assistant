import sys
sys.path.insert(0, '')  # Ensure the current directory is in the sys.path
from datasets import load_dataset as huggingface_load_dataset
sys.path.remove('')
from dotenv import load_dotenv
from tqdm import tqdm
from eval_dataset_utilities import load_system_template
import json
import openai
import os
import csv


class WikiEvalDataset:
    def __init__(self,datasetDir="datasets/WikiEval",reload=False,loadNum=50,datasetType="train"):
        self._init_path(datasetDir,datasetType)
        if reload:
            self._reload_dataset(loadNum,datasetType)
        elif not os.path.exists(self.datasetPath):
            print("Warning: Dataset at {} not found, reloading automatically...".format(self.datasetPath))
            self._reload_dataset(loadNum,datasetType)
        self.dataset=self._load_dataset()


    def _init_path(self,datasetDir,datasetType):
        self.datasetPath = os.path.join(datasetDir,datasetType+".json")
        if not os.path.exists(datasetDir):
            os.makedirs(datasetDir)

    def _reload_dataset(self,loadNum,datasetType):
        dataset = huggingface_load_dataset("explodinggradients/WikiEval")
        data=dataset[datasetType][:loadNum]
        self._write2json(data)

    def _write2json(self,data):
        with open(self.datasetPath, 'w') as f:
            json.dump(data, f)

    def _load_dataset(self):
        with open(self.datasetPath) as f:
            dataset = json.load(f)
        return dataset

    def __getitem__(self, item):
        data={}
        for key in self.dataset.keys():
            data[key]=self.dataset[key][item]
        return data
    def __len__(self):
        return len(self.dataset['answer'])

class testWikiEvalDataset:
    def __init__(self,datasetDir="datasets/WikiEval",outFile="result.csv",reload=False,loadNum=50,datasetType="train"):
        self.wikiEval = WikiEvalDataset(datasetDir, True, loadNum, datasetType)
        self._init_dir(datasetDir,outFile)
        self._set_openai_api_key()

    def _init_dir(self,datasetDir,outFile):
        if not os.path.exists(datasetDir):
            os.makedirs(datasetDir)
        self.outPath=os.path.join(datasetDir,outFile)

    def _set_openai_api_key(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def _init_client(self,ground_truth):
        print("Creating new client...")
        self.client = openai.Client()
        system_prompt_ground_truth = load_system_template()
        # Generate the response from OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt_ground_truth.format(ground_truth=ground_truth)}]
            )
            generated_text = response.choices[0].message.content
        except Exception as e:
            raise Exception(str(e))

        print("Client created successfully...")

    def test(self):
        for i in tqdm(range(len(self.wikiEval)),desc="Testing WikiEval",ncols=100):
            context_v2=self.wikiEval[i]["context_v2"]
            question=self.wikiEval[i]["question"]
            ungrounded_answer=self.wikiEval[i]["ungrounded_answer"]
            poor_answer=self.wikiEval[i]["poor_answer"]
            self._init_client(context_v2)
            self.get_eval(context_v2, question, poor_answer)
            try:
                pass
            except Exception as e:
                print("Error: ",str(e))
    def test_with_try(self):
        num=0
        total_data_num=len(self.wikiEval)
        fail_time=0
        with tqdm(total=total_data_num,desc="Testing WikiEval",ncols=100) as pbar:
            while num<total_data_num:
                try:
                    i=num
                    context_v2 = self.wikiEval[i]["context_v2"]
                    question = self.wikiEval[i]["question"]
                    ungrounded_answer = self.wikiEval[i]["ungrounded_answer"]
                    poor_answer = self.wikiEval[i]["poor_answer"]
                    self._init_client(context_v2)
                    result=self.get_eval(context_v2, question, poor_answer)
                    self.write_result2csv(result, i)
                    num+=1
                    pbar.update(1)
                except Exception as e:
                    print("Error: ",str(e))
                    fail_time+=1
                    if fail_time>3:
                        print("Failed too many times, skip...")
                        num+=1
                        pbar.update(1)

    def write_result2csv(self,data_dict, number):
        # Check if the CSV file exists
        file_exists = os.path.isfile(self.outPath)

        # Open the CSV file in append mode
        with open(self.outPath, mode='a', newline='') as file:
            writer = csv.writer(file)
            # If the file doesn't exist, write the header (keys of the dictionary)
            if not file_exists:
                writer.writerow(['Number'] + list(data_dict.keys()))

            # Write the data (number and values of the dictionary)
            writer.writerow([number] + list(data_dict.values()))


    def get_eval(self,ground_truth,question,response):
        from evaluation_utils.azure.azure_eval_criteria import RELEVANCE_PROMPT_TEMPLATE
        from evaluation_utils.azure.azure_eval import azure_evaluation
        from evaluation_utils.eval_copilot.copilot_eval_criteria import (
            evaluation_system_prompt,
            evaluation_instructions,
            improvement_user_instructions,
            improvement_system_content,
            example_improvement_suggestions,
            new_coherence_prompt,
        )
        from evaluation_utils.eval_copilot.copilot_utils import (
            create_message,
            run_chat_completions,
        )
        from evaluation_utils.eval_copilot.eval_copilot import (
            copilot_evaluation,
            EvaluationCopilot,
        )
        from evaluation_utils.eval_copilot.generic_evaluation import (
            get_generic_evaluation_score,
        )
        from evaluation_utils.eval_copilot.improvement_copilot import ImprovementCopilot
        from evaluation_utils.eval_copilot.relevance_evaluation import (
            ImprovementCopilotNew as RelevanceImprovementCopilotNew,
            relevance_improvement_prompts,
        )
        from evaluation_utils.eval_copilot.simplicity_evaluation import (
            ImprovementCopilotNew as SimplicityImprovementCopilotNew,
            simplicity_improvement_prompts,
        )
        from models.evaluation_models import CopilotEvaluationResponse, CopilotEvaluation
        from models.prompt_models import GenerationResponse

        improvement_copilot = RelevanceImprovementCopilotNew(relevance_improvement_prompts)
        simplicity_improvement_copilot = SimplicityImprovementCopilotNew(simplicity_improvement_prompts)

        azure_eval_msg = create_message(
            "system",
            RELEVANCE_PROMPT_TEMPLATE.format(
                context=ground_truth, question=question, answer=response
            ),
        )
        azure_eval_score_response = run_chat_completions([azure_eval_msg])
        azure_eval_score = azure_eval_score_response.split("tars:")[1].strip()

        (
            eval1_score,
            eval1_justification,
            eval1_improvement_suggestion,
        ) = improvement_copilot.get_improvement_suggestion(
            ground_truth, question, response
        )

        (
            eval_simplicity_score,
            eval_simplicity_justification,
            eval_simplicity_improvement_suggestion,
        ) = simplicity_improvement_copilot.get_improvement_suggestion(
            ground_truth, question, response
        )

        generic_eval = get_generic_evaluation_score(question, response, self.client)

        eval_data = {
            "prompt": question,
            "response": response,
            "azure_evaluation_score": azure_eval_score,
            "score": eval1_score,
            "justification": eval1_justification,
            "improvement_suggestion": eval1_improvement_suggestion,
            "simplicity_score": eval_simplicity_score,
            "simplicity_justification": eval_simplicity_justification,
            "simplicity_improvement_suggestion": eval_simplicity_improvement_suggestion,
            "new_evaluation_score": generic_eval["rating"],
            "new_evaluation_justification": generic_eval["explanation"],
            "new_evaluation_improvement_suggestion": generic_eval[
                "improvement_suggestions"
            ],
        }

        return eval_data


if __name__ == "__main__":
    test = testWikiEvalDataset()
    test.test_with_try()
    # load_dotenv()
    # client = openai.Client()
    #
    #
    # # Ensure the API key is set
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # ground_truth,system_prompt_ground_truth=load_system_template()
    #
    # # Generate the response from OpenAI
    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{"role": "system", "content": system_prompt_ground_truth.format(ground_truth=ground_truth)},
    #                   {"role": "user", "content": prompt}]
    #     )
    #     generated_text = response.choices[0].message.content
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    #
    # azure_eval_msg = create_message(
    #     "system",
    #     RELEVANCE_PROMPT_TEMPLATE.format(
    #         context=ground_truth, question=prompt, answer=response
    #     ),
    # )
    # azure_eval_score_response = run_chat_completions([azure_eval_msg])
    # azure_eval_score = azure_eval_score_response.split("tars:")[1].strip()
    #
    # (
    #     eval1_score,
    #     eval1_justification,
    #     eval1_improvement_suggestion,
    # ) = improvement_copilot.get_improvement_suggestion(
    #     ground_truth, prompt, generated_text
    # )
    #
    # (
    #     eval_simplicity_score,
    #     eval_simplicity_justification,
    #     eval_simplicity_improvement_suggestion,
    # ) = simplicity_improvement_copilot.get_improvement_suggestion(
    #     ground_truth, prompt, generated_text
    # )
    #
    # generic_eval = get_generic_evaluation_score(prompt, generated_text, client)
    #
    # response_data = {
    #     "request": request,
    #     "prompt": prompt,
    #     "response": generated_text,
    #     "azure_evaluation_score": azure_eval_score,
    #     "score": eval1_score,
    #     "justification": eval1_justification,
    #     "improvement_suggestion": eval1_improvement_suggestion,
    #     "simplicity_score": eval_simplicity_score,
    #     "simplicity_justification": eval_simplicity_justification,
    #     "simplicity_improvement_suggestion": eval_simplicity_improvement_suggestion,
    #     "new_evaluation_score": generic_eval["rating"],
    #     "new_evaluation_justification": generic_eval["explanation"],
    #     "new_evaluation_improvement_suggestion": generic_eval[
    #         "improvement_suggestions"
    #     ],
    # }
    #
    # test.test()


