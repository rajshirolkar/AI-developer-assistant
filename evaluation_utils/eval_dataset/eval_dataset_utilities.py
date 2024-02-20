

def load_system_template():
    system_prompt_ground_truth = """
    You are a helpful assistant. You will be given a groundtruth and a prompt. Your job is to provide a response that is relevant to the groundtruth and prompt.

    Ground Truth:
    {ground_truth}
    """
    return system_prompt_ground_truth
