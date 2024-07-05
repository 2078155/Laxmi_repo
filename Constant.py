context_generation_prompt = """
            You are context extractor, for the given QUESTIONS from the Source.
            The Question asked to an interviewee to check the FACT OF HAVING THE ABILITY
            OR SKILL for the JOBPOST.
            An Interview question framed on two following Source: JOBPOST and COMPETENCY.
            The QUESTION structured by the circumstances of COMPETENCY description to
            check an Interviewee have the ability or skill to the corresponding competency and QUESTION. It also
            includes TECHNICAL KEYWORDS from the
            JOBPOST for VALID QUESTIONS.

            I will give you an input as LIST of QUESTIONS, JOBPOST and COMPETENCY.
            Input data:
            JOBPOST : {JobPost}
            COMPETENCY: {competency}
            QUESTIONS: {QuestionList}

            Your job is to generate the CONTEXT for each QUESTIONS. You have to analyse
            the entire JOBPOST and COMPETENCY 
            dictionary. For generating the context you have to check and extract the
            sentences with case insensitive
            matches from the given JOBPOST and COMPETENCY dictionary Value description
            that supports to create the given QUESTION.
            
            A few additional guidelines:  
            - Don 't miss to generate the context for all the QUESTIONS in a list. Don' t 
            shuffle the order of the question
            while giving final output.  
            - While generating the context, don 't miss to extract all the sentences from  
            the Input data which supports to 
            create the corresponding question.  
            - While generating the context don't mention any words in double inverted  
            commas("").  
            - Ensure that generated CONTEXT validates that the given QUESTION is based on  
            the JOBPOST and COMPETENCY 
            dictionary value descriptions. If No such context can be found then please  
            mention context as "NO CONTEXT 
            FOUND FOR GIVEN QUESTION".  
            - Don 't write the reason why you picked this as CONTEXT.  
            - For each QUESTIONS, generate the context then assign in 'context' Key and  
            Corresponding Question in 
            'question' Key.  
            - Don 't generate any extra dictionaries, generate only for provided QUESTIONS.  
            - provide the Final output only in proper JSON FORMAT only as mentioned below  
            and don't give anything extra  
            supporting string as output.  
            {outputKey} 
            """

ques_context_generation_prompt = """ 
            You are context extractor, for the given QUESTIONS from the JOBPOST.  
            The Question asked to an interviewee to check the FACT OF HAVING THE ABILITY  
            OR SKILL for the JOBPOST. The  
            QUESTIONS are framed by referring the JOBPOST.  

            I will give you an Input_data as LIST of QUESTIONS and JOBPOST.
            Input_data:  
            JOBPOST: {JobPost}  
            QUESTIONS: {QuestionList}  

            Your job is to generate the CONTEXT for each QUESTIONS. You have to analyse  
            the entire JOBPOST. For generating  
            the context your have to check and extract the sentences, if sentence not  
            found then look for keywords with case  
            insensitive matches from the given JOBPOST that supports to create the given  
            QUESTION.  

            A few additional guidelines:  
            - Don't miss to generate the context for all the QUESTIONS in a list. Don't
            shuffle the order of the 
            question while giving final output.  
            - While generating the context don't mention any words in double inverted  
            commas(""). 
            - While generating the context, don't miss to extract all the sentences, if  
            sentence not found then look for  
            keywords from the Input_data which supports to create the corresponding  
            question .  
            - Ensure that generated CONTEXT validates that the given QUESTION is based on  
            the JOBPOST. If No such context  
            can be found then please mention context as "NO CONTEXT FOUND FOR GIVEN  
            QUESTION".  
            - Don 't write the reason why you picked this as CONTEXT.  
            - For each QUESTIONS, generate the context then assign in 'context' Key and  
            Corresponding Question in 
            'question' Key.  
            - Don't generate any extra dictionaries, generate only for provided QUESTIONS.  
            - provide the Final output only in proper JSON FORMAT only as mentioned below  
            and don 't give anything extra 
            supporting string as output.  
            {outputKey}  
            """
relevance_template = """
        You are a RELEVANCE grader; providing the relevance of the given QUESTION to the
        given CONTEXT.
        Based on the CONTEXT the QUESTION was CREATED
        you have to check the RELEVANCE between the QUESTION and CONTEXT.
        Respond only as a number from 0 to 1 where 0 is the least relevant and 1 is the
        most relevant.
        A few additional scoring guidelines:
        - Long QUESTION should score equally well as short QUESTION .
        - RELEVANCE score should increase as much the given QUESTION able to frame from
        the given CONTEXT. If question is
        not able to frame from the given CONTEXT, RELEVANCE score should get reduced.
        - QUESTION that is not COVERED any part of the given CONTEXT should score a 0 and
        give the reason as "NO Relevance FOUND"
        - QUESTION has minimal level of RELEVANCE from the given CONTEXT should score of
        0.1 or 0.2 or 0.3 . Higher score indicates more RELEVANCE.
        - QUESTION has partial level of RELEVANCE from the given CONTEXT should get score
        of 0.4 or 0.5. Higher score indicates more RELEVANCE.
        - QUESTION has moderate level of RELEVANCE from the given CONTEXT should get score
        of 0.6 or 0.7 or 0.8. Higher score indicates more RELEVANCE.
        - QUESTION has extensive level of RELEVANCE from the given CONTEXT should get a
        score of 0.9
        - QUESTION has very extensive level of RELEVANCE from the given CONTEXT to get a 
        score of 1.
        - Never elaborate
        
        CONTEXT : {context}
        QUESTION : {question}
        
        Please answer using JSON Format below:
        Template :
        score : <The score 0—1 based on the given criteria>
        reason: <Provide your reasons for scoring based on the listed criteria.If score
        is less, then provide reason as why got less score .>
"""

JD_Question_relevance = """
        You are a RELEVANCE grader; providing the relevance score between QUESTION and the
        CONTEXT.
        you have to check the RELEVANCE between the QUESTION and CONTEXT.
        Respond only as a number from 0 to 1 where 0 is the least relevant and 1 is the
        most relevant.
        A few additional scoring guidelines:
        - Long QUESTION should score equally well as short QUESTION.
        - RELEVANCE score should increase as much the given QUESTION able to frame from
        the given CONTEXT.If question is 
        not able to frame from the given CONTEXT, RELEVANCE score should get reduced.
        - QUESTION that is not COVERED any part of the given CONTEXT should score a 0 and
        give the reason as "NO Relevance FOUND"
        - QUESTION has minimal level of RELEVANCE from the given CONTEXT should score of
        0.1 or 0.2 or 0.3. Higher score indicates more RELEVANCE.
        - QUESTION has partial level of RELEVANCE from the given CONTEXT should get score
        of 0.4 or 0.5. Higher score indicates more RELEVANCE.
        - QUESTION has moderate level of RELEVANCE from the given CONTEXT should get score
        of 0.6 or 0.7 or 0.8. Higher score indicates more RELEVANCE.
        - QUESTION has extensive level of RELEVANCE from the given CONTEXT should get a
        score of 0.9
        - QUESTION has very extensive level of RELEVANCE from the given CONTEXT should get a
        score of 1


        CONTEXT: {context}
        QUESTION: {question}
        Please answer using JSON FORMAT below:
        Template:
        score: <The score 0—1 based on the given criteria >
        reason: <Provide your reasons for scoring based on the listed criteria.If score 
        is less then provide reason as why got less score.>
        
"""

competency_template = """
            You are a RELEVANCE grader; providing the relevance of the given QUESTION to the
            given COMPETENCY.  
            To analyze the candidate's ability in an interview, you have to check whether the  
            given QUESTION is able to  
            measure the COMPETENCY level. So you have to check the QUESTION whether it is  
            align with COMPETENCY and give the  
            RELEVANCE score.  
            COMPETENCY which means the FACT OF HAVING THE ABILITY OR SKILL THAT IS NEEDED FOR  
            FACING SOMETHING.  

            Based on the COMPETENCY reference the QUESTION was CREATED.  
            you have to check the RELEVANCE between the QUESTION and COMPETENCY.  
            Respond only as a number from 0 to 1 where 0 is the least relevant and 1 is the  
            most relevant .  
            A few additional scoring guidelines:  
            - Long QUESTION should score equally well as short QUESTION .  
            - RELEVANCE score should increase as the QUESTION FACT OF HAVING THE ABILITY OR  
            SKILL more for the given COMPETENCY.  
            - QUESTION that is not able to check the FACT OF HAVING THE ABILITY OR SKILL ANY 
            part of the COMPETENCY should score a 0.  
            - QUESTION that is able to check the FACT OF HAVING minimal level of THE ABILITY  
            OR SKILL mentioned in the COMPETENCY should score of 0.1 or 0.2 or 0.3 . Higher 
            score indicates more RELEVANCE.  
            - QUESTION that is able to check the FACT of having partial level of THE ABILITY  
            OR SKILL mentioned in the COMPETENCY should score of 0.4 or 0.5 . Higher 
            score indicates more RELEVANCE.  
            - QUESTION that is able to check the FACT of having moderate level of THE ABILITY  
            OR SKILL mentioned in the COMPETENCY should score of 0.6 or 0.7 OR 0.8 . Higher 
            score indicates more RELEVANCE.  
            - QUESTION that is able to check the FACT of having extensive level of THE ABILITY  
            OR SKILL mentioned in the COMPETENCY should score of 0.9 . 
            - QUESTION that is able to check the FACT of having all the ability OR SKILL 
            mentioned in the COMPETENCY should get Score of 1.
            - Never elaborate
            
            COMPETENCY : {context}  
            QUESTION : {question}  
            
            Please answer using JSON Format below:  
            Template :  
            score : <The score 0—1 based on the given criteria>  
            reason: <Provide your reasons for scoring based on the listed criteria. If score  
            is less then provide reason as why got less score> 

"""
coherence_template = """
        Rate the coherence of the following QUESTION.
        Respond only as a number from 0 to 1 where 0 is the least coherent and 1 is the 
        most coherent.
        QUESTION:{Question}
        When evaluating coherence, consider the following criteria:
        1. The QUESTION should be well structured and organized.
        2. The QUESTION should convey the information in a clear and logical order .

        Please answer using JSON FORMAT below:
        Template :
        score :<The score 0—1 based on the given criteria>
        reason: <Provide your reasons for scoring based on the listed criteria. If score
        is less then provide reason as why got less score.> 
        """

factuality_template = """  
        You are a FACT CHECKER, you are given a CONTEXT and a QUESTION. The QUESTION was
        an Interview question which was written by giving the CONTEXT as input but it may be wrong.  
        A few additional scoring guidelines:  
        - FACTUALITY score should increase as the QUESTION factually supported by the  
        CONTEXT.  
        - FACTUALITY score should increase as you can find EVIDENCE for more parts of the  
        QUESTION.  
        - QUESTION for which you can't find any EVIDENCE should score a 0.  
        - If you find EVIDENCE for only part of the QUESTION should score of 0.2, 0.3, 0.4 or 0.5.  
        Higher score indicates more FACTUALITY.  
        - If you find EVIDENCE for most part of the QUESTION should score of 0.6, 0.7 or 0.8  
        Higher score indicates more FACTUALITY.  
        - If you find EVIDENCE for entire QUESTION should score of 0.9 or 1.  
        Higher score indicates more FACTUALITY.  

        Your task is to verify whether the given QUESTION are factually supported by the  
        CONTEXT or not.  
        QUESTION : {question}  
        CONTEXT : {context} 
        
        Please answer using JSON FORMAT below:  
        Template:  
        "score":<Provide a rating between 0 - 1 of type float, to show your confidence  
        that the QUESTION was written by correctly 
        interpreting the CONTEXT text>  
        "reason":<Provide your reasons for scoring based on the listed criteria. If score  
        is less, then provide reason as why got less score.>  
        "evidence":<Choose the exact unchanged sentences In the context that can prove the  
        QUESTION in a single string. if nothing matches, say NOTHING FOUND>  
        
        """

direct_indirect_template = """The following question has been given to an Interviewer to ask  
a candidate,  
            it is required that question they ask should be in direct speech. Classify it  
            as direct or indirect  
            speech. {Question}.  
            Follow the guidelines while generating the output:  
            - Generate the results only for given question.  
            - Don' t create any extra dictionaries.  

            Return your response as a JSON Format :  
            Template:  
            "speech":<Direct/ Indirect> 
            """

fluency_template = """  
        You are a Fluency grader; providing the fluency score of the given QUESTION.  
        Respond only as a number from 0 to 1 where 0 is the least fluent and 1 is the  
        Excellent fluency .  

        Use the following criteria to pick an appropriate score:  
        0-0.2: Poor fluency. The QUESTION has many errors in grammar, spelling,  
        punctuation, word choice and sentence structure,  
        making it difficult to understand or sounding unnatural.  
        0.3—0.4: Fair fluency. The QUESTION has some errors that affect the clarity or  
        smoothness of the writing, but the main points are 
        still comprehensible .  
        0.5—0.7: Good fluency. The QUESTION has few errors and is generally easy to read  
        and follow, but may have some minor issues.  
        0.8—1.0: Excellent fluency. The QUESTION is well written, with no noticeable  
        errors in grammar, spelling, punctuation.  
        word choice and sentence structure, making it easy to read and understand.  
        QUESTION: {question}  
        Please answer using JSON Format below:  
        Template :  
        score: <The score 0—1 based on the given criteria.If score is less, then provide reason as why got less score.>  
        reason: <Provide your reasons for scoring based on the listed criteria.>
        """

PL_competency = {
    "Vision and Purpose": "Articulates a compelling and inspired vision and sense of purpose based on our values and "
                          "to better serve our clients.",
    "Strategic Agility": "Creates competitive strategies, specific plans, and establishes intelligent risk levels for "
                         "achieving the organizational vision, mission and goals.",
    "Priority Setting": "Identifies and prioritizes critical business issues and aligns the organization accordingly.",
    "Developing Direct Reports and Others": "Committed to employee development and career growth.",
    "Engaging and Empowering Others": "Fosters a work environment where people feel energized and empowered.",
    "Championing Change": "Relentlessly pursues change that is best for the organization and its customers.",
    "Business Acumen": "Knowledgeable of industry standards and how we can better compete in the marketplace and best serve our clients.",
    "Effective Decision Making": "Able to make risk-based business decisions that create value.",
    "Drive for Results": "Meets and/or exceeds business goals consistently.",
    "Ethics and Trust": "Inspires trust, acts ethically, and consistently demonstrates our values.",
    "Embraces Diversity": "Values and manages employee diversity and cross-functional collaboration to achieve results.",
    "Leadership Fortitude": "Provides current, direct, complete, and actionable feedback to others."
}

IC_competency = {
    "Effective Communication": "Understanding of effective communication concepts, tools and techniques; ability to "
                               "effectively transmit, receive, and accurately interpret ideas, information, "
                               "and needs through the application of appropriate communication behaviors.",
    "Initiative": "Understanding of the value of self-motivation and initiative; ability and willingness to seek out "
                  "work and the drive to accomplish goals.",
    "Addressing Customer Needs": "Knowledge of and ability to meet customer needs by offering appropriate solutions "
                                 "in an appropriate manner.",
    "Accuracy & Attention to Detail": "Understanding of the necessity and value of accuracy and attention to detail; "
                                      "ability to process information with high levels of accuracy.",
    "Interpersonal Relationships": "Knowledge of the techniques and the ability to work with a variety of individuals "
                                   "and groups in a constructive and collaborative manner.",
    "Problem Solving": "Knowledge of approaches, tools, techniques for recognizing, anticipating, and resolving "
                       "organizational, operational or process problems; ability to apply this knowledge "
                       "appropriately to diverse situations.",
    "Flexibility & Adaptability": "Knowledge of successful approaches, tools, and techniques for dealing with changes "
                                  "and adapting to a changing environment;ability to adapt as needed. "
}

JD_prompt_template = """<Job Requisition>
            {content}
            </Job Requisition>
            <Instructions>
            As you are a job post reviewer, based on the provided Job post (provided under <Job  
            Requisition> Tag),
            Your job is to categorize skills based on provided under <Sections> Tag.  
            Guideline to follow while categorizing:  
            - While categorizing Don't consider the educational qualification. (provided under  
            <Job Requisition> Tag).
            - From the job post don't consider Work Experience section  
            Please Do not be Descriptive.  
            <Sections>  
            Tools/ Framework  
            Software  
            Knowledge/ qualification  
            Responsibilities  
            project Experience  
            Certifications  
            Soft skills  
            </Sections>  
            Present the output in the valid JSON format .  
            </Instructions>  

"""

Duplicate_PROMPT = """From the given set of questions {questions} identify of there are any duplicate questions.  
determine if they are duplicate based on the following rules: 1.Two questions can be fully or partially  
duplicate. 2. fully means they are nearly rephrased versions of each other 3. partially means part of the  
question is the same and the answer to one question would partially answer the other. 4. Multiple  
questions can be duplicates of each other list each pair separately. 5. Return the responses as JSON  
containing all duplicate whether they are full or partial duplicates, a reason and a score between 0-10  
showing how similar they are based on the criteria given below.  

Score criteria: Give a score 1-3 if questions are partial duplicates but very slightly similar. Give a  
score of 4-6 if questions are partial duplicates but are asking similar questions about the same topic or  
highly related topics. Give a score of 8-9 if questions are partial or fully asking very similar  
questions about the exact same topics. Give a score of 10 if the questions are fully duplicate.
Provide the output in below json format only
Format for JSON  
{{ 
"duplicates":[ 
    {{ 
        "questions": <List of 2 questions that are duplicates>,  
        "type" : <full/partial>,
        "reason": "", 
        "similarity_score":<int 0-10>,

    }} 
] 
}} 

"""

question_generation_template = {
    "question_prompts": "<Interviewer Introduction>As a TIAA hiring manager, it's essential to assess a candidate's "
                        "fit for the role beyond just their technical skills. Behavioral interview questions allow us "
                        "to gauge a candidate's competencies, problem—solving abilities, and potential for success in "
                        "the position. By evaluating how they have handled real—life situations, we can better "
                        "understand their thought processes, decision—making, and overall approach to "
                        "work.</Interviewer Introduction>\n<Job Requisition>\n{content}\n</Job "
                        "requisition>\n<Skills>\n{skills}\n</Skills>\n<Instructions>\nUsing Job requisition text, "
                        "Your task is to generate technical—focused behavioral interview questions using below steps: "
                        "\n1. Infer the appropriate role type (junior, mid—level, or senior) and domain. \n2. Then "
                        "based on the provided corresponding competencies name and its description for {career_level} "
                        "for all competencies, Craft each one with 3 relevant technical—focused behavioral interview "
                        "questions tailored to inferred role type and domain. While forming Question Please Ensure to "
                        "Include Skills keywords from each relevant section (refer from given above <Skills> Tag "
                        "only) . Please also follow <Examples> Tag while creating questions . \n3. Always Ensure that "
                        "using the Given Job requisition (refer from given <Job Requisition> Tag only), "
                        "Out of 21 Generated Behavioral questions, 8 Questions Should be taken from The Key "
                        "Responsibilities and Duties Section, 8 Questions from Required Skills Section, 3 Questions "
                        "from Preferred or Minimum or Desired Skills Section and 2 Questions from Related Skills "
                        "Section. If Required Skill Section is not present, Then Take 8 Questions from Key "
                        "Responsibilities and Duties, 7 Questions from Preferred or Minimum or Desired Skills and 6 "
                        "Questions from Related Skills Section. Please also follow <Examples> Tag while creating "
                        "questions . \n4. Always Ensure the questions emphasize technical situations, challenges, "
                        "and decision-making relevant to the all technical skills, inferred role, and domain, "
                        "while aligning with the provided job requisition and relevant competency descriptions . \n5. "
                        "Always Ensure the All 21 Generated Final Behavioral Questions should have included All Exact "
                        "Skills Keywords taken from relevant sections (refer from given Above <Skills> Tag only) . "
                        "Please Do not include Skills Keywords of Each section which is not present in above <Skills> "
                        "Tag. \n6. Do not output the inferred role type and domain in the response. Present the "
                        "output in the following valid JSON format:{{ Individual_contributor :[{{\"Competency1\": ["
                        "\"Technical Behavioral Question 1\", \"Technical Behavioral Question 2\",\"Technical "
                        "Behavioral Question 3\"]}},{{\"Competency2\": [\"Technical Behavioral Question 1\", "
                        "\"Technical Behavioral Question 2\",\"Technical Behavioral Question 3\"]}},"
                        "...]}} <Examples>Here are three general examples: \n Problem-solving: Describe a situation "
                        "when you were faced with a complex problem related to ' insert technical skill here' , "
                        "what steps did you take to solve it, and what was the result? Technical proficiency: Can you "
                        "share an instance where your expertise in ' insert technical skill here' was crucial for the "
                        "successful completion of a project? Adaptability: Tell us about a time when you had to "
                        "quickly learn a new technical skill or tool ' insert technical skill here' for a project. "
                        "How did you approach the learning process and how did it impact the project "
                        "outcome?\n</Examples>\n<Individual Contributor Competencies>\n— Effective Communication: "
                        "Understanding of effective communication concepts, tools and techniques; ability to "
                        "effectively transmit, receive, and accurately interpret ideas, information, "
                        "and needs through the application of appropriate communication behaviors . \n— Initiative: "
                        "Understanding of the value of self—motivation and initiative; ability and willingness to "
                        "seek out work and the drive to accomplish goals . Addressing Customer Needs: Knowledge of "
                        "and ability to meet customer needs by offering appropriate solutions in an appropriate "
                        "manner. \n—Accuracy Attention to Detail: Understanding of the necessity and value of "
                        "accuracy and attention to detail; ability to process information with high levels of "
                        "accuracy. \n— Interpersonal Relationships: Knowledge of the techniques and the ability to "
                        "work with a variety of individuals and groups in a constructive and collaborative manner. "
                        "\n— Problem Solving: Knowledge of approaches, tools, techniques for recognizing, "
                        "anticipating, and resolving organizational, operational or process problems; ability to "
                        "apply this knowledge appropriately to diverse situations. Flexibility & Adaptability: "
                        "Knowledge of successful approaches, tools, and techniques for dealing with changes and "
                        "adapting to a changing environment; ability to adapt as needed. \n</Individual Contributor "
                        "Competencies>\n",
    "skills_prompt_template": "<Job Requisition>{JobPost}</Job Requisition>. <Instructions> Based on the provided Job "
                              "requisition (provided under <Job Requisition> Tag).For Each section (provided under "
                              "Tag) , Your Task is to only Extract all Exact Skills Keywords Present in it. Please Do "
                              "not Extract Skills Keywords Which is not present in Job requisition. \nAlways Ensure "
                              "to Output extracted skills with its Section name. Please Do not be Descriptive. "
                              "<Sections>Key Duties & Responsibilities\n Key Responsibilities and Duties\n Required "
                              "Qualifications\n Required Skills\nRelated Skills\n preferred Qualifications\n Desired "
                              "Skills\n Minimum Qualifications\n preferred Skills\nMinimum "
                              "Requirements</Sections></Instructions> "
}

# question_generation_template = {


#   "question_prompts": "<Interviewer Introduction>As a TIAA hiring manager, it's essential to assess a candidate's fit "
#                       "for the role beyond just their technical skills. Behavioral interview questions allow us to "
#                       "gauge a candidate's competencies, problem-solving abilities, and potential for success in the "
#                       "position. By evaluating how they have handled real-life situations, we can better understand "
#                       "their thought processes, decision-making, and overall approach to work.</Interviewer "
#                       "Introduction>\n<Job Requisition>\n{content}\n</Job Requisition>\n<Skills>\n{"
#                       "skills}\n</Skills>\n<Instructions>\nUsing Job requisition text, Your task is to generate "
#                       "technical-focused behavioral interview questions using below steps:\n1. Infer the appropriate "
#                       "role type (junior, mid-level, or senior) and domain.\n2. Then based on the provided "
#                       "corresponding competencies name and its description for {career_level} for all competencies, "
#                       "Craft each one with 3 relevant technical-focused behavioral interview questions tailored to "
#                       "inferred role type and domain. While forming Question Please Ensure to Include Skills keywords "
#                       "from each relevant section (refer from given above <Skills> Tag only). Please also follow "
#                       "<Examples> Tag while creating questions.\n3. Always Ensure that using the Given Job "
#                       "requisition (refer from given <Job Requisition> Tag only), Out of 21 Generated Behavioral "
#                       "questions, 8 Questions Should be taken from The Key Responsibilities and Duties Section, "
#                       "8 Questions from Required Skills Section, 3 Questions from Preferred or Minimum or Desired "
#                       "Skills Section and 2 Questions from Related Skills Section. If Required Skill Section is not "
#                       "present, Then Take 8 Questions from Key Responsibilities and Duties, 7 Questions from "
#                       "Preferred or Minimum or Desired Skills and 6 Questions from Related Skills Section. Please "
#                       "also follow <Examples> Tag while creating questions.\n4. Always Ensure the questions emphasize "
#                       "technical situations, challenges, and decision-making relevant to the all technical skills, "
#                       "inferred role, and domain, while aligning with the provided job requisition and relevant "
#                       "competency descriptions.\n5. Always Ensure the All 21 Generated Final Behavioral Questions "
#                       "should have included All Exact Skills Keywords taken from relevant sections (refer from given "
#                       "Above <Skills> Tag only). Please Do not include Skills Keywords of Each section which is not "
#                       "present in above <Skills> Tag.\n6. Do not output the inferred role type and domain in the "
#                       "response. Present the output in the following valid JSON format: { Individual_contributor :[{"
#                       "\"Competency1\": [\"Technical Behavioral Question 1\", \"Technical Behavioral Question 2\", "
#                       "\"Technical Behavioral Question 3\"]}, {\"Competency2\": [\"Technical Behavioral Question 1\", "
#                       "\"Technical Behavioral Question 2\", \"Technical Behavioral Question 3\"]}, "
#                       "...]}\n<Examples>Here are three general examples:\nProblem-solving: Describe a situation when "
#                       "you were faced with a complex problem related to ' insert technical skill here', what steps "
#                       "did you take to solve it, and what was the result?\nTechnical proficiency: Can you share an "
#                       "instance where your expertise in ' insert technical skill here' was crucial for the successful "
#                       "completion of a project?\nAdaptability: Tell us about a time when you had to quickly learn a "
#                       "new technical skill or tool ' insert technical skill here' for a project. How did you approach "
#                       "the learning process and how did it impact the project outcome?\n</Examples>\n<Individual "
#                       "Contributor Competencies>\n- Effective Communication: Understanding of effective communication "
#                       "concepts, tools and techniques; ability to effectively transmit, receive, and accurately "
#                       "interpret ideas, information, and needs through the application of appropriate communication "
#                       "behaviors.\n- Initiative: Understanding of the value of self-motivation and initiative; "
#                       "ability and willingness to seek out work and the drive to accomplish goals.\n- Addressing "
#                       "Customer Needs: Knowledge of and ability to meet customer needs by offering appropriate "
#                       "solutions in an appropriate manner.\n- Accuracy Attention to Detail: Understanding of the "
#                       "necessity and value of accuracy and attention to detail; ability to process information with "
#                       "high levels of accuracy.\n- Interpersonal Relationships: Knowledge of the techniques and the "
#                       "ability to work with a variety of individuals and groups in a constructive and collaborative "
#                       "manner.\n- Problem Solving: Knowledge of approaches, tools, techniques for recognizing, "
#                       "anticipating, and resolving organizational, operational or process problems; ability to apply "
#                       "this knowledge appropriately to diverse situations.\n- Flexibility & Adaptability: Knowledge "
#                       "of successful approaches, tools, and techniques for dealing with changes and adapting to a "
#                       "changing environment; ability to adapt as needed.\n</Individual Contributor Competencies>\n",
#
#   "skills_prompt_template": "<Job Requisition>{JobPost}</Job Requisition>. <Instructions> Based on the provided Job "
#                             "requisition (provided under <Job Requisition> Tag). For Each section (provided under "
#                             "Tag), Your Task is to only Extract all Exact Skills Keywords Present in it. Please Do "
#                             "not Extract Skills Keywords Which is not present in Job requisition.\nAlways Ensure to "
#                             "Output extracted skills with its Section name. Please Do not be "
#                             "Descriptive.\n<Sections>Key Duties & Responsibilities\nKey Responsibilities and "
#                             "Duties\nRequired Qualifications\nRequired Skills\nRelated Skills\nPreferred "
#                             "Qualifications\nDesired Skills\nMinimum Qualifications\nPreferred Skills\nMinimum "
#                             "Requirements</Sections></Instructions> "
#
# }

jobPost = """Senior Specialist - Full Stack Development - IN
Full Stack Development are involved in full stack development and implement end-to-end components of custom applications. Their job involves designing and developing the UI, business logic, data & integration layer along with testing and maintenance of these layers.
Key Responsibilities and Duties
They are adept in the use of tools and technologies across tiers, and are proficient in working with systems infrastructure, creating, querying & manipulating databases, APIs and integration, Front-end code (HTML/CSS, bootstrap, React JS, Angular JS) and web stack back-end technologies (PHP, Python, Java, ruby on rails etc.).
They have a sound understanding of CI/CD processes, agile development.
They possess deep understanding of programming fundamentals and can learn new frameworks, languages and tools as required on projects.
Educational Requirements
University (Degree) Preferred
Work Experience
5+ Years Required; 7+ Years Preferred
Physical Requirements
Physical Requirements: Sedentary Work
Career Level
8IC
SMA Backend Engineer – Product Technology - Job Description
A SMA Backend Engineer will be reporting to the SMA Engineering Lead (Backend), the role is responsible for executing backend application design and development for all SMA applications under product technology group.              This person would be a part of a team of backend engineers supporting building core services supporting the applications under the product technology group. This work would entail building applications on a scalable micro services-based architecture using industry best practices, as well as aligning these to enterprise design frameworks.
Additional Responsibilities
Execute rigorous processes to support unit-testing and peer reviewing code working with all members of the team to drive successful execution of user stories supporting business requirements.
Integrate, deploy, maintain, and improve software continuously.
Responsible for quality solution deliverables – support QA and business testing to ensure high quality deliverables.
Deep knowledge of coding best practices and ability to drive Proof of concepts to drive innovation in the team.
Support the global product technology team to increase market-share and margin through adoption of technology.
Implement a process for continuous improvement, lower costs to serve and improving efficiency.
Develop and deliver scalable solutions that can be applied to clients and the business. 
Support modernization of platforms to align with the firm’s tech strategy.
Focused on building a new stack of applications for supporting product launches, SMA platforms, Advisor portal.
Drive a passion and core competency across the organization for technology transformation. 
Coordinate comprehensive changes to update how we work or develop new ways of working.
Execute priorities and focus for local and regional teams to support global engineering and delivery of core internal and client products and services. 
Required Skills:
6+ years of technology experience building high performance multi-threaded applications/micro services using the Java/J2EE technologies.
6+ years experience in Spring framework, Spring Boot, Rest Services and API gateway.
6+ years experience in Database environment - SQL, PL/SQL programming, No SQL.
Hands-on Experience with Container Platform like OpenShift.
Hand-on Experience with containerization tools like Docker, Kubernetes, etc.
Experience using system tools, source control systems like Git/SVN, and utilities.
Good understanding of cloud providers and services – AWS (ECS/EKS, EC2, S3, NoSQL Database, IAM, IaaS, Cloud formation/Terraform etc.,)
Exposure to enterprise architecture, solution architecture, cloud, data engineering 
Agile proficient
Preferred Skills:
Global outlook and mind set.
Operated in an environment of unprecedented, rapid change, where innovation and quick responses yielded success. 
Experience in navigating across large, complex matrixed organizations.
Strong cultural alignment: unwavering ethical standards; drives excellence and innately collaborative.
Bachelor’s degree in a relevant field (engineering or computer science or engineering discipline)
Exposure to multiple infrastructure, cloud, mobile and network technologies
Related Skills
Agile Methodology, Continuous Integration & Deployment, Data Analysis, Debugging, DevOps, Enterprise Application Integration, Operating Systems Management, Problem Solving, Programming, Software Development, Software Development Life Cycle, Web Application Development"""

generated_output = {
    "Individual_contributor": [
        {
            "Effective Communication": [
                "Describe a situation where you had to communicate complex technical concepts related to full stack development, such as UI design, business logic implementation, or data integration, to non-technical stakeholders. How did you ensure clear understanding?",
                "Can you share an instance where your communication skills played a crucial role in collaborating with cross-functional teams during the development of a React JS or Angular JS application? What challenges did you face, and how did you overcome them?",
                "Tell us about a time when you had to present a technical solution or architecture involving technologies like Spring framework, REST APIs, or AWS services to a team or client. How did you tailor your communication style to effectively convey complex concepts?"
            ]
        },
        {
            "Initiative": [
                "Can you provide an example of a time when you took the initiative to learn a new programming language or framework like PHP, Python, or Ruby on Rails to enhance your full stack development skills? How did this initiative benefit the project or organization?",
                "Describe a situation where you proactively identified and suggested improvements to an existing CI/CD process or agile development methodology. What steps did you take to implement these changes?",
                "Tell us about a time when you independently explored emerging technologies or tools related to your domain, such as containerization (Docker, Kubernetes) or cloud services (AWS), and how you applied that knowledge to drive innovation."
            ]
        },
        {
            "Addressing Customer Needs": [
                "Can you share an instance where you had to understand and address specific customer needs or requirements while developing a full stack application? How did you ensure that the solution met their expectations?",
                "Describe a situation where you had to gather and analyze customer feedback or user data to enhance the user experience (UX) or user interface (UI) of an application. What steps did you take, and what was the outcome?",
                "Tell us about a time when you had to collaborate with customers or stakeholders to understand their business requirements and translate them into technical specifications for a full stack development project. How did you ensure successful delivery?"
            ]
        },
        {
            "Accuracy Attention to Detail": [
                "Can you provide an example of a time when your attention to detail was critical in identifying and resolving a bug or issue related to front-end development (HTML/CSS, React JS, Angular JS) or back-end development (PHP, Python, Java, Ruby on Rails)?",
                "Describe a situation where you had to ensure accuracy and precision while working with databases (SQL, PL/SQL, NoSQL) or integrating with APIs during a full stack development project. How did you approach this task?",
                "Tell us about an instance where your keen attention to detail helped you identify and address potential issues or edge cases during the testing or maintenance phase of a full stack application development."
            ]
        },
        {
            "Interpersonal Relationships": [
                "Can you share an example of a time when you had to collaborate effectively with a diverse team of developers, designers, or stakeholders during a full stack development project? How did you navigate interpersonal dynamics and build strong working relationships?",
                "Describe a situation where you had to provide mentorship or guidance to junior developers, particularly in areas such as front-end technologies (HTML/CSS, React JS, Angular JS) or back-end technologies (PHP, Python, Java, Ruby on Rails). How did you approach this responsibility?",
                "Tell us about an instance when you had to resolve a conflict or disagreement within a cross-functional team during a full stack development project. How did you handle the situation while maintaining positive interpersonal relationships?"
            ]
        },
        {
            "Problem Solving": [
                "Can you describe a complex problem you faced during a full stack development project, such as integrating multiple systems, optimizing performance, or addressing security concerns? What steps did you take to analyze and resolve the issue?",
                "Tell us about a time when you had to troubleshoot and debug a challenging issue related to front-end development (HTML/CSS, React JS, Angular JS) or back-end development (PHP, Python, Java, Ruby on Rails). How did you approach the problem-solving process?",
                "Describe a situation where you had to develop an innovative solution to address a technical challenge or requirement during a full stack development project. What problem-solving techniques or tools did you employ, and what was the outcome?"
            ]
        },
        {
            "Flexibility & Adaptability": [
                "Can you share an example of a time when you had to quickly adapt to changes in project requirements, technologies, or architectures during a full stack development project? How did you approach the situation, and what was the result?",
                "Describe a situation where you had to learn and apply a new technology or framework, such as a front-end framework (React JS, Angular JS) or a back-end language (PHP, Python, Java, Ruby on Rails), in a short timeframe to meet project deadlines. How did you adapt and ensure successful delivery?",
                "Tell us about an instance when you had to transition between different development methodologies, such as agile or waterfall, or between different cloud platforms or services (AWS, OpenShift). How did you adapt to these changes while maintaining productivity?"
            ]
        }
    ]
}
