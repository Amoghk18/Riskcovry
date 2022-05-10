import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

isModelPresent, isModelSaved, model, tokenizer = False, False, None, None

paragraph = """
Individual Individual and Floater
Sum Insured (in Rs.) 300000/- 500000/-1000000/- 1500000/- 2000000/- 2500000/- 5000000/- 7500000/- 10000000/-
1 Plan Type Silver Plan
Room Rent (Per Day) - Up to
2 *Hospitalization expenses will be
considered in proportion to the eligible Single Private A/c Room II(A)
Room Rent
Surgeon, Anesthetist, Medical
3 Practitioner, Consultants, Specialist
Fees, Anesthesia, blood, oxygen,
operation theatre charges, Surgical Actual II(B & C)
Appliances, Medicines and Drugs
4 Road Ambulance charges(per policy
Actuals
period) II(D)
5 Pre-Hospitalization Expenses Up to 60 days prior to admission II(E)
6 Post-Hospitalization Expenses  Up to 90 days from the date of discharge  II(F)
7 Day Care Procedure All day care procedure covered. II(G)
8 Medical Opinion E -Medical Opinion" from the Company's expert panel. II(H)
Sum Insured/policy type Rs3,00,000/- Rs5,00,000/- Rs10,00,000/- Rs15,00,000/-and above
9. Health Check Individual 1,500/- 2,000/- 3,000/- 3,500/- II(I)
up
Floater N/A 3,000/- 4,000/- 5,000/-
Automatic Restoration of Basic Sum
10 Once during policy period  by 100% II(J)
Insured
The insured person will be eligible for Cumulative bonus calculated at 20% of basic sum insured for each claim
11 Cumulative bonus free year subject to a maximum of 100% of the basic sum insured. II(K)
Additional Basic Sum Insured for Road 25% of the Sum Insured subject to a
12 II(L)
Traffic Accident (RTA) maximum of Rs10,00,000/-
13 Star Wellness Program Discount in the Renewal premium for healthy life style through wellness activities. II(M)
14 Special Features 10% Discount at the time of renewal after 40years of age. V(22 A)
15. Coverage for Modern Treatment Covered up to the limits II(N)
16. Instalment Facility (If Opted) Available V(13)
"""

question = "plan type?"

def downloadModelIfAbsent():
    if isModelPresent == False and isModelSaved == False:
        if isModelSaved:
            model = torch.load('model_bert.pth')
        else:
            #Model
            model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
            isModelPresent = True
        
        #Tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
        
        torch.save(model, 'model_bert.pth')
        isModelSaved = True
        
        
def getParagraphList(paragraph):
    paras = []
    paragraph = paragraph.split("\n")
    flag = True
    count = 0
    para = ''
    for line in paragraph:
        length = len(line.split(" "))
        if length + count + 1 < 512:
            para += line + "\n "
            count += len(line.split(" "))
        else:
            paras.append(para)
            para = line
            count = len(line.split(" "))
    paras.append(para)
    return paras

def getAnswerForQuery(paragraph, question):
    answer = ''
    paraList = getParagraphList(paragraph)
    downloadModelIfAbsent()
    for para in paraList:
        encoding = tokenizer.encode_plus(text=question,text_pair=para, add_special=True)
        inputs = encoding['input_ids']
        sentence_embedding = encoding['token_type_ids']
        tokens = tokenizer.convert_ids_to_tokens(inputs)
        start_scores, end_scores = model(input_ids = torch.tensor([inputs]), 
                                     token_type_ids = torch.tensor([sentence_embedding]), return_dict = False)
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)
        answer = ' '.join(tokens[start_index:end_index+1])
        if answer[0] != "[":
            break
    return answer

getAnswerForQuery(paragraph, question)