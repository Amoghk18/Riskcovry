import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

class QueryAnswerer():

    def __init__(self) -> None:
        self.isModelSaved = True
        self.isModelLoaded = False
        self.model = None
        self.tokenizer = None
        self.paragraph = ""
        self.question = ""

    def getAnswer(self, text, query):
        self.paragraph = text
        self.question = query
        return self.getAnswerForQuery()


    def downloadModelIfAbsent(self):
        if self.isModelLoaded: return
        elif self.isModelSaved:
            self.model = torch.load('model_bert.pth')
            self.tokenizer = BertTokenizer.from_pretrained("./tokenizer/")
            self.isModelLoaded = True
        else:
            self.model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
            self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
            torch.save(self.model, 'model_bert.pth')
            self.tokenizer.save_pretrained("./tokenizer/")
            self.isModelSaved = True

    def getParagraphList(self):
        paras = []
        paragraph_new = self.paragraph.split("\n")
        count = 0
        para = ''
        for line in paragraph_new:
            length = len(line.split(" "))
            if length + count + 1 < 200:
                para += line + "\n "
                count += length
            else:
                paras.append(para)
                para = line
                count = len(line.split(" "))
        paras.append(para)
        return paras

    def cleanAnswers(self, answers):
        new_answers = []
        for ans in answers:
            new_ans = ''
            if not ans.startswith('['):
                words = ans.split(' ##')
                new_ans = ''.join(words)
                new_answers.append(new_ans)
        return new_answers

    def getAnswerForQuery(self):
        answer = ''
        paraList = self.getParagraphList()
        self.downloadModelIfAbsent()
        answers = []
        for para in paraList:
            encoding = self.tokenizer.encode_plus(text=self.question,text_pair=para, add_special=True)
            inputs = encoding['input_ids']
            sentence_embedding = encoding['token_type_ids']
            tokens = self.tokenizer.convert_ids_to_tokens(inputs)
            start_scores, end_scores = self.model(input_ids = torch.tensor([inputs]), 
                                        token_type_ids = torch.tensor([sentence_embedding]), return_dict = False)
            start_index = torch.argmax(start_scores)
            end_index = torch.argmax(end_scores)
            answer = ' '.join(tokens[start_index:end_index+1])
            answers.append(answer)
        answers = self.cleanAnswers(answers)
        return answers
