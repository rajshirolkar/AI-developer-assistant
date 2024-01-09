evaluation_system_prompt = """You are an AI assistant tasked with evaluating the coherence of answers in a 
question-and-answer format. Your evaluation should be based on how well the sentences in the answer integrate to form 
a unified and logical whole. Your responsibilities include: (1) assigning a coherence score using a 1-5 star rating 
system, (2) providing a detailed justification for the assigned score. Always provide a score as an integer between 1 and 5. Along with each score, include a clear justification, 
pointing out the aspects of the answer that influenced your rating."""

improvement_system_content = """System: You are an AI assistant tasked with suggesting improvements to user prompts based on coherence scores and justifications provided. Your goal is to analyze the given score and its justification, then identify and suggest specific changes to the user prompt that could lead to clearer and more coherent answers in the future. Consider factors like specificity, clarity, and guidance offered in the prompt. Provide actionable suggestions to refine the user's prompt, making it more effective for eliciting coherent responses."""

improvement_user_instructions = """User: When you receive a coherence score and justification for a response, 
use this information to suggest specific improvements to the original user prompt. Focus on how the prompt can be 
rephrased or structured differently to guide respondents towards providing more coherent and relevant answers. 
Consider aspects such as clarity, specificity, and the framing of the question. Your suggestions should aim to 
enhance the quality of future responses by refining the prompt."""

evaluation_instructions = """When scoring the coherence of an answer, consider how seamlessly the sentences connect and contribute to a 
unified understanding of the topic. Use the following scale for scoring: - One star: The answer completely lacks 
coherence. - Two stars: The answer mostly lacks coherence. - Three stars: The answer is partially coherent. - Four 
stars: The answer is mostly coherent. - Five stars: The answer has perfect coherency."""
user_content_1 = """Question: What is your favorite indoor activity and why do you enjoy it? 
Answer: I like pizza. The sun is shining. """
user_content_2 = """Question: Can you describe your favorite movie without giving away any spoilers? 
Answer: It is a science fiction movie. There are dinosaurs. The actors eat cake. People must stop the villain. """
user_content_3 = """Question: What are some benefits of regular exercise?
Answer: Regular exercise improves your mood. A good workout also helps you sleep better. Trees are green."""
user_content_4 = """Question: How do you cope with stress in your daily life? Answer: I usually go for a walk to clear my head. Listening 
to music helps me relax as well. Stress is a part of life, but we can manage it through some activities."""
user_content_5 = """Question: What can you tell me about climate change and its effects on the environment? Answer: Climate change has 
far-reaching effects on the environment. Rising temperatures result in the melting of polar ice caps, contributing to 
sea-level rise. Additionally, more frequent and severe weather events, such as hurricanes and heatwaves, 
can cause disruption to ecosystems and human societies alike."""

assistant_content_1 = """Stars: 1 
Justification: The answer completely lacks coherence. The response doesn't address the question about a 
favorite indoor activity or provide a reason for enjoying it. The mention of pizza is irrelevant, and the statement 
about the sun shining is disconnected from the context of indoor activities"""
assistant_content_2 = """Stars: 2 
Justification: The answer mostly lacks coherence. While it starts relevantly by mentioning it's a science fiction movie with dinosaurs, 
the subsequent sentences become increasingly disjointed. The mention of actors eating cake is unrelated to a typical 
movie plot, and the final sentence is too vague to provide a coherent description. """
assistant_content_3 = """Stars: 3 Justification: The answer is partially coherent. The first two 
sentences coherently describe benefits of regular exercise (mood improvement and better sleep). However, 
the last sentence about green trees is completely unrelated to the topic of exercise benefits, disrupting the overall 
coherence."""
assistant_content_4 = """Stars: 4 
Justification: The answer is mostly coherent. It provides relevant personal strategies for coping with stress (
walking, listening to music) and concludes with a general statement about stress management. The answer maintains 
focus on the topic, though it could be slightly more detailed or specific to achieve perfect coherence."""
assistant_content_5 = """Stars: 5 Justification: The answer has perfect 
coherency. It directly addresses the question with a clear and concise explanation of climate change and its 
environmental impacts. The answer is well-structured, logically flowing from one point to the next, and covers a 
broad range of relevant effects, making it a coherent response."""

improvement_content_1 = """Improvement Suggestion: To ensure a coherent answer, the question could be more specific and guiding. For instance: "What is your favorite indoor activity that helps you relax or feel entertained, and can you explain why you find it enjoyable?" """
improvement_content_2 = """Improvement Suggestion: To guide the respondent towards a coherent answer, the question might include a prompt for structured response, such as: "Can you describe the genre, setting, and main theme of your favorite movie, without giving away any spoilers?" """
improvement_content_3 = """Improvement Suggestion: The question is already well-structured for coherent answers. To further guide the response, it could be slightly modified to: "Can you list and briefly explain at least three health benefits of regular exercise?" """
improvement_content_4 = """Improvement Suggestion: This question generally prompts coherent answers. To enhance it, consider adding: "How do you cope with stress in your daily life, and can you describe how these methods effectively help you manage stress?" """
improvement_content_5 = """Improvement Suggestion: The question is already conducive to coherent answers. To maintain this quality, it could be rephrased for clarity and depth: "What are the key impacts of climate change on the environment, and how do these effects manifest in different ecological and societal aspects?" """


few_shot_examples = [
    (user_content_1, assistant_content_1),
    (user_content_2, assistant_content_2),
    (user_content_3, assistant_content_3),
    (user_content_4, assistant_content_4),
    (user_content_5, assistant_content_5)
]

example_improvement_suggestions = [
    (user_content_1, assistant_content_1, improvement_content_1),
    (user_content_2, assistant_content_2, improvement_content_2),
    (user_content_3, assistant_content_3, improvement_content_3),
    (user_content_4, assistant_content_4, improvement_content_4),
    (user_content_5, assistant_content_5, improvement_content_5)
]

COHERENCE_SJ_PROMPT_TEMPLATE = """System: You are an AI assistant tasked with evaluating the coherence of answers in a 
question-and-answer format. Your evaluation should be based on how well the sentences in the answer integrate to form 
a unified and logical whole. Your responsibilities include: (1) assigning a coherence score using a 1-5 star rating 
system, (2) providing a detailed justification for the assigned score.

User: When scoring the coherence of an answer, consider how seamlessly the sentences connect and contribute to a 
unified understanding of the topic. Use the following scale for scoring: - One star: The answer completely lacks 
coherence. - Two stars: The answer mostly lacks coherence. - Three stars: The answer is partially coherent. - Four 
stars: The answer is mostly coherent. - Five stars: The answer has perfect coherency.

Always provide a score as an integer between 1 and 5. Along with each score, include a clear justification, 
pointing out the aspects of the answer that influenced your rating.

Sample Evaluations:

Question: What is your favorite indoor activity and why do you enjoy it? 
Answer: I like pizza. The sun is shining. 
Stars: 1 
Justification: The answer completely lacks coherence. The response doesn't address the question about a 
favorite indoor activity or provide a reason for enjoying it. The mention of pizza is irrelevant, and the statement 
about the sun shining is disconnected from the context of indoor activities. 


Question: Can you describe your favorite movie without giving away any spoilers? Answer: It is a science fiction 
movie. There are dinosaurs. The actors eat cake. People must stop the villain. Stars: 2 Justification: The answer 
mostly lacks coherence. While it starts relevantly by mentioning it's a science fiction movie with dinosaurs, 
the subsequent sentences become increasingly disjointed. The mention of actors eating cake is unrelated to a typical 
movie plot, and the final sentence is too vague to provide a coherent description.


Question: What are some benefits of regular exercise? Answer: Regular exercise improves your mood. A good workout 
also helps you sleep better. Trees are green. Stars: 3 Justification: The answer is partially coherent. The first two 
sentences coherently describe benefits of regular exercise (mood improvement and better sleep). However, 
the last sentence about green trees is completely unrelated to the topic of exercise benefits, disrupting the overall 
coherence.


Question: How do you cope with stress in your daily life? Answer: I usually go for a walk to clear my head. Listening 
to music helps me relax as well. Stress is a part of life, but we can manage it through some activities. Stars: 4 
Justification: The answer is mostly coherent. It provides relevant personal strategies for coping with stress (
walking, listening to music) and concludes with a general statement about stress management. The answer maintains 
focus on the topic, though it could be slightly more detailed or specific to achieve perfect coherence.


Question: What can you tell me about climate change and its effects on the environment? Answer: Climate change has 
far-reaching effects on the environment. Rising temperatures result in the melting of polar ice caps, contributing to 
sea-level rise. Additionally, more frequent and severe weather events, such as hurricanes and heatwaves, 
can cause disruption to ecosystems and human societies alike. Stars: 5 Justification: The answer has perfect 
coherency. It directly addresses the question with a clear and concise explanation of climate change and its 
environmental impacts. The answer is well-structured, logically flowing from one point to the next, and covers a 
broad range of relevant effects, making it a coherent response.


New Evaluation:
Question: {{question}}
Answer: {{answer}}

For the above question and answer give the coherence score between 1 to 5 stars and provide a justification for the score. Also, provide an improvement suggestion for the question to guide the respondent towards a more coherent answer in the future in this format :
Stars: 
Justification: 
"""

COHERENCE_MOD_PROMPT_TEMPLATE = """System: As an AI assistant, your task is to suggest improvements to questions 
based on previously given coherence scores and justifications. Analyze the coherence score and its accompanying 
justification to understand where the original question fell short in eliciting a coherent response. Use this 
understanding to propose modifications that enhance the question's ability to guide respondents towards more 
coherent, structured answers. Your suggestions should directly address the weaknesses highlighted in the 
justification, refining the question's focus, clarity, and specificity. This process is crucial for improving the 
quality of future interactions and responses.

When suggesting improvements to the original question, follow these detailed instructions:

Analyze the Coherence Score and Justification: Carefully review the provided coherence score and its justification. Identify the specific aspects that led to the given score, focusing on areas where the answer lacked coherence.

Identify Key Areas for Improvement: Based on the justification, pinpoint the elements of the question that could be 
refined. This might include clarity, specificity, or guidance towards a more structured response.

Formulate Your Suggestion: Craft a revised version of the question. Ensure that your suggestion directly addresses the issues highlighted in the justification. The goal is to rephrase the question in a way that naturally guides the respondent to provide a more coherent and comprehensive answer.

Provide Clear Rationale: Accompany your suggestion with a brief explanation of why this change would likely result in a more coherent response in future instances.

Sample Evaluations:

Question: What is your favorite indoor activity and why do you enjoy it? 
Answer: I like pizza. The sun is shining. 
Stars: 1 
Justification: The answer completely lacks coherence. The response doesn't address the question about a 
favorite indoor activity or provide a reason for enjoying it. The mention of pizza is irrelevant, and the statement 
about the sun shining is disconnected from the context of indoor activities. 
Improvement Suggestion: To ensure a coherent answer, the question could be more specific and guiding. For instance: "What is your favorite indoor activity that helps you relax or feel entertained, and can you explain why you find it enjoyable?"

Question: Can you describe your favorite movie without giving away any spoilers? 
Answer: It is a science fiction movie. There are dinosaurs. The actors eat cake. People must stop the villain. 
Stars: 2 
Justification: The answer mostly lacks coherence. While it starts relevantly by mentioning it's a science fiction movie with dinosaurs, 
the subsequent sentences become increasingly disjointed. The mention of actors eating cake is unrelated to a typical 
movie plot, and the final sentence is too vague to provide a coherent description. 
Improvement Suggestion: To guide the respondent towards a coherent answer, the question might include a prompt for structured response, such as: "Can you describe the genre, setting, and main theme of your favorite movie, without giving away any spoilers?"

Question: What are some benefits of regular exercise?
Answer: Regular exercise improves your mood. A good workout also helps you sleep better. Trees are green.
Stars: 3
Justification: The answer is partially coherent. The first two sentences coherently describe benefits of regular exercise (mood improvement and better sleep). However, the last sentence about green trees is completely unrelated to the topic of exercise benefits, disrupting the overall coherence.
Improvement Suggestion: The question is already well-structured for coherent answers. To further guide the response, it could be slightly modified to: "Can you list and briefly explain at least three health benefits of regular exercise?"

Question: How do you cope with stress in your daily life?
Answer: I usually go for a walk to clear my head. Listening to music helps me relax as well. Stress is a part of life, but we can manage it through some activities.
Stars: 4
Justification: The answer is mostly coherent. It provides relevant personal strategies for coping with stress (walking, listening to music) and concludes with a general statement about stress management. The answer maintains focus on the topic, though it could be slightly more detailed or specific to achieve perfect coherence.
Improvement Suggestion: This question generally prompts coherent answers. To enhance it, consider adding: "How do you cope with stress in your daily life, and can you describe how these methods effectively help you manage stress?"

Question: What can you tell me about climate change and its effects on the environment?
Answer: Climate change has far-reaching effects on the environment. Rising temperatures result in the melting of polar ice caps, contributing to sea-level rise. Additionally, more frequent and severe weather events, such as hurricanes and heatwaves, can cause disruption to ecosystems and human societies alike.
Stars: 5
Justification: The answer has perfect coherency. It directly addresses the question with a clear and concise explanation of climate change and its environmental impacts. The answer is well-structured, logically flowing from one point to the next, and covers a broad range of relevant effects, making it a coherent response.
Improvement Suggestion: The question is already conducive to coherent answers. To maintain this quality, it could be rephrased for clarity and depth: "What are the key impacts of climate change on the environment, and how do these effects manifest in different ecological and societal aspects?"

New Evaluation:
Question: {{question}}
Answer: {{answer}}

For the above question and answer give the coherence score between 1 to 5 stars and provide a justification for the score. Also, provide an improvement suggestion for the question to guide the respondent towards a more coherent answer in the future in this format :
Stars: 
Justification: 
Improvement Suggestion:
"""


COHERENCE_PROMPT_TEMPLATE = """System: You are an AI assistant tasked with evaluating the coherence of answers in a 
question-and-answer format. Your evaluation should be based on how well the sentences in the answer integrate to form 
a unified and logical whole. Your responsibilities include: (1) assigning a coherence score using a 1-5 star rating 
system, (2) providing a detailed justification for the assigned score, and (3) suggesting improvements to the 
original question to better elicit a coherent response in the future.

User: When scoring the coherence of an answer, consider how seamlessly the sentences connect and contribute to a 
unified understanding of the topic. Use the following scale for scoring: - One star: The answer completely lacks 
coherence. - Two stars: The answer mostly lacks coherence. - Three stars: The answer is partially coherent. - Four 
stars: The answer is mostly coherent. - Five stars: The answer has perfect coherency.

Always provide a score as an integer between 1 and 5. Along with each score, include a clear justification, 
pointing out the aspects of the answer that influenced your rating. Additionally, propose modifications to the 
original question that could guide respondents towards providing more coherent answers in future instances.

Sample Evaluations:

Question: What is your favorite indoor activity and why do you enjoy it? 
Answer: I like pizza. The sun is shining. 
Stars: 1 
Justification: The answer completely lacks coherence. The response doesn't address the question about a 
favorite indoor activity or provide a reason for enjoying it. The mention of pizza is irrelevant, and the statement 
about the sun shining is disconnected from the context of indoor activities. 
Improvement Suggestion: To ensure a coherent answer, the question could be more specific and guiding. For instance: "What is your favorite indoor activity that helps you relax or feel entertained, and can you explain why you find it enjoyable?"

Question: Can you describe your favorite movie without giving away any spoilers? 
Answer: It is a science fiction movie. There are dinosaurs. The actors eat cake. People must stop the villain. 
Stars: 2 
Justification: The answer mostly lacks coherence. While it starts relevantly by mentioning it's a science fiction movie with dinosaurs, 
the subsequent sentences become increasingly disjointed. The mention of actors eating cake is unrelated to a typical 
movie plot, and the final sentence is too vague to provide a coherent description. 
Improvement Suggestion: To guide the respondent towards a coherent answer, the question might include a prompt for structured response, such as: "Can you describe the genre, setting, and main theme of your favorite movie, without giving away any spoilers?"

Question: What are some benefits of regular exercise?
Answer: Regular exercise improves your mood. A good workout also helps you sleep better. Trees are green.
Stars: 3
Justification: The answer is partially coherent. The first two sentences coherently describe benefits of regular exercise (mood improvement and better sleep). However, the last sentence about green trees is completely unrelated to the topic of exercise benefits, disrupting the overall coherence.
Improvement Suggestion: The question is already well-structured for coherent answers. To further guide the response, it could be slightly modified to: "Can you list and briefly explain at least three health benefits of regular exercise?"

Question: How do you cope with stress in your daily life?
Answer: I usually go for a walk to clear my head. Listening to music helps me relax as well. Stress is a part of life, but we can manage it through some activities.
Stars: 4
Justification: The answer is mostly coherent. It provides relevant personal strategies for coping with stress (walking, listening to music) and concludes with a general statement about stress management. The answer maintains focus on the topic, though it could be slightly more detailed or specific to achieve perfect coherence.
Improvement Suggestion: This question generally prompts coherent answers. To enhance it, consider adding: "How do you cope with stress in your daily life, and can you describe how these methods effectively help you manage stress?"

Question: What can you tell me about climate change and its effects on the environment?
Answer: Climate change has far-reaching effects on the environment. Rising temperatures result in the melting of polar ice caps, contributing to sea-level rise. Additionally, more frequent and severe weather events, such as hurricanes and heatwaves, can cause disruption to ecosystems and human societies alike.
Stars: 5
Justification: The answer has perfect coherency. It directly addresses the question with a clear and concise explanation of climate change and its environmental impacts. The answer is well-structured, logically flowing from one point to the next, and covers a broad range of relevant effects, making it a coherent response.
Improvement Suggestion: The question is already conducive to coherent answers. To maintain this quality, it could be rephrased for clarity and depth: "What are the key impacts of climate change on the environment, and how do these effects manifest in different ecological and societal aspects?"

New Evaluation:
Question: {{question}}
Answer: {{answer}}

For the above question and answer give the coherence score between 1 to 5 stars and provide a justification for the score. Also, provide an improvement suggestion for the question to guide the respondent towards a more coherent answer in the future in this format :
Stars: 
Justification: 
Improvement Suggestion:
"""


