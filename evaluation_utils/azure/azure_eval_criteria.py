COHERENCE_PROMPT_TEMPLATE = """
System:
You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Coherence of an answer is measured by how well all the sentences fit together and sound naturally as a whole. Consider the overall quality of the answer when evaluating coherence. Given the question and answer, score the coherence of answer between one to five stars using the following rating scale:
One star: the answer completely lacks coherence
Two stars: the answer mostly lacks coherence
Three stars: the answer is partially coherent
Four stars: the answer is mostly coherent
Five stars: the answer has perfect coherency

This rating value should always be an integer between 1 and 5. 
So the rating produced should be 1 or 2 or 3 or 4 or 5.

question: What is your favorite indoor activity and why do you enjoy it?
answer: I like pizza. The sun is shining.
stars: 1

question: Can you describe your favorite movie without giving away any spoilers?
answer: It is a science fiction movie. There are dinosaurs. The actors eat cake. People must stop the villain.
stars: 2

question: What are some benefits of regular exercise?
answer: Regular exercise improves your mood. A good workout also helps you sleep better. Trees are green.
stars: 3

question: How do you cope with stress in your daily life?
answer: I usually go for a walk to clear my head. Listening to music helps me relax as well. Stress is a part of life, but we can manage it through some activities.
stars: 4

question: What can you tell me about climate change and its effects on the environment?
answer: Climate change has far-reaching effects on the environment. Rising temperatures result in the melting of polar ice caps, contributing to sea-level rise. Additionally, more frequent and severe weather events, such as hurricanes and heatwaves, can cause disruption to ecosystems and human societies alike.
stars: 5

question: {question}
answer: {answer}
stars:
"""

RELEVANCE_PROMPT_TEMPLATE = """
System:
You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Relevance measures how well the answer addresses the main aspects of the question, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between one to five stars using the following rating scale:
One star: the answer completely lacks relevance
Two stars: the answer mostly lacks relevance
Three stars: the answer is partially relevant
Four stars: the answer is mostly relevant
Five stars: the answer has perfect relevance

This rating value should always be an integer between 1 and 5. So the rating produced should be 1 or 2 or 3 or 4 or 5.

context: Marie Curie was a Polish-born physicist and chemist who pioneered research on radioactivity and was the first woman to win a Nobel Prize.
question: What field did Marie Curie excel in?
answer: Marie Curie was a renowned painter who focused mainly on impressionist styles and techniques.
stars: 1

context: The Beatles were an English rock band formed in Liverpool in 1960, and they are widely regarded as the most influential music band in history.
question: Where were The Beatles formed?
answer: The band The Beatles began their journey in London, England, and they changed the history of music.
stars: 2

context: The recent Mars rover, Perseverance, was launched in 2020 with the main goal of searching for signs of ancient life on Mars. The rover also carries an experiment called MOXIE, which aims to generate oxygen from the Martian atmosphere.
question: What are the main goals of Perseverance Mars rover mission?
answer: The Perseverance Mars rover mission focuses on searching for signs of ancient life on Mars.
stars: 3

context: The Mediterranean diet is a commonly recommended dietary plan that emphasizes fruits, vegetables, whole grains, legumes, lean proteins, and healthy fats. Studies have shown that it offers numerous health benefits, including a reduced risk of heart disease and improved cognitive health.
question: What are the main components of the Mediterranean diet?
answer: The Mediterranean diet primarily consists of fruits, vegetables, whole grains, and legumes.
stars: 4

context: The Queen's Royal Castle is a well-known tourist attraction in the United Kingdom. It spans over 500 acres and contains extensive gardens and parks. The castle was built in the 15th century and has been home to generations of royalty.
question: What are the main attractions of the Queen's Royal Castle?
answer: The main attractions of the Queen's Royal Castle are its expansive 500-acre grounds, extensive gardens, parks, and the historical castle itself, which dates back to the 15th century and has housed generations of royalty.
stars: 5

context: {context}
question: {question}
answer: {answer}
stars:
"""

FLUENCY_PROMPT_TEMPLATE = """
System: 
You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

User:
Fluency measures the quality of individual sentences in the answer, and whether they are well-written and grammatically correct. Consider the quality of individual sentences when evaluating fluency. Given the question and answer, score the fluency of the answer between one to five stars using the following rating scale:
One star: the answer completely lacks fluency
Two stars: the answer mostly lacks fluency
Three stars: the answer is partially fluent
Four stars: the answer is mostly fluent
Five stars: the answer has perfect fluency

This rating value should always be an integer between 1 and 5. So the rating produced should be 1 or 2 or 3 or 4 or 5.

question: What did you have for breakfast today?
answer: Breakfast today, me eating cereal and orange juice very good.
stars: 1

question: How do you feel when you travel alone?
answer: Alone travel, nervous, but excited also. I feel adventure and like its time.
stars: 2

question: When was the last time you went on a family vacation?
answer: Last family vacation, it took place in last summer. We traveled to a beach destination, very fun.
stars: 3

question: What is your favorite thing about your job?
answer: My favorite aspect of my job is the chance to interact with diverse people. I am constantly learning from their experiences and stories.
stars: 4

question: Can you describe your morning routine?
answer: Every morning, I wake up at 6 am, drink a glass of water, and do some light stretching. After that, I take a shower and get dressed for work. Then, I have a healthy breakfast, usually consisting of oatmeal and fruits, before leaving the house around 7:30 am.
stars: 5

question: {question}
answer: {answer}
stars:
"""