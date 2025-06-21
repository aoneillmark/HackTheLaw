import json
import re
import cn2an

import random    
class File_op:

    config = {
        "TASK" : { "article": 0, "crime":1, "penalty":2 },
        "TASK_NAME" : ["article", "crime", "penalty"],
        "readroot" :'./mydata/CAIL2018/data/',
        "logroot": './log/smallmodel/',
        "model": "Bert",
        
        "testjson_path":"./mydata/CAIL2018/data/data_test.json",
        "lawlabelpath":"./mydata/CAIL2018/lawLabel.json",
        "crimelabelpath":"./mydata/CAIL2018/crimeLabel.json",
    }



    def __init__(self,response):
        self.response = response

    @classmethod
    def readjsoncase(cls, filepath):
        caselist = []
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                data = json.loads(line)
                caselist.append(data)
        return caselist

    @classmethod
    def readjsonlist(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    
    '''
        所有法条的文本
    '''
    @classmethod
    def readalllawtext(cls):
        lawtxtpath = './mydata/gpt2fol/lawalltxt.json'
        lawtext = dict()

        with open(lawtxtpath, 'r', encoding='utf-8') as file:
            lawtxts = json.load(file)
        for law in lawtxts:
            lawlabel = law['lawlabel']
            text = law['text']
            lawtext[lawlabel] = text
        return lawtext

    # 读初始化的规则，cail数据集的
    @classmethod
    def readcailRule_init(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            # lawrulepath = './mydata/gpt2fol/law2fol.json'
            lawlabelpath = './mydata/gpt2fol/lawlabeltxt.json'
            iinit_folpath = './mydata/gpt2fol/law2folLog.json'
            lawrulelsit,lawtxtlist = {},{}
            with open(iinit_folpath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                article = rule['lawlabel']
                article_text = rule['text']
                article_rule = rule['fol']
                lawrulelsit[article] = article_rule
                lawtxtlist[article] = article_text
            return lawtxtlist,lawrulelsit
        
        if taskint ==TASK['crime']:
            update_crimerulepath = './mydata/CaseItem/caseitem.json'
            init_crimepath = './mydata/CaseItem/init_crimeitem_cail.json'
            rulelist =[]
            with open(init_crimepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            ruledict = dict()
            for rule in rulelist:
                crime = rule['crime']
                rule = rule['rule']
                ruledict[crime] = rule
            return ruledict

        if taskint == TASK['penalty']:
            parulepath = './mydata/CaseItem/init_penaltyrule_cail.json'
            update_prulpath = './mydata/CaseItem/update_penaltyrule_cail.json'
            parulelist = {}
            with open(parulepath, 'r', encoding='utf-8') as file:
                init_rulelist = json.load(file)
            # with open(update_prulpath, 'r', encoding='utf-8') as file2:
            #     update_rulelist = json.load(file2)
            # for rule in update_rulelist:
            #     penaltyindex = rule['penaltyindex']
            #     prule = rule['rule']
            #     article = rule['article']
            #     article_text = rule['article_text']

            #     pakey = (penaltyindex,article)
            #     paitem = (prule,article_text)
            #     parulelist[pakey] = paitem
            
            for rule in init_rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']
                pakey = (penaltyindex,article)
                paitem = (prule,article_text)

                if pakey not in parulelist.keys():
                    parulelist[pakey] = paitem

            return parulelist

    @classmethod
    def readFol(cls):
        lawlabelpath = './mydata/gpt2fol/lawlabeltxt.json'
        init_folpath = './mydata/gpt2fol/law2folLog.json'
        folpath = './mydata/gpt2fol/law2fol.json'
        lawfol = dict()
        lawtext = dict()

        # with open(lawlabelpath, 'r', encoding='utf-8') as file:
        #     lawtextlabel = json.load(file)

        with open(folpath, 'r', encoding='utf-8') as file:
            follist = json.load(file)
                
        for item in follist:
            lawlabel = item['lawlabel']
            fol = item['fol']
            text = item['text']
            if not isinstance(lawlabel, int):
                try:
                    lawlabel = int(lawlabel)
                except ValueError:
                    print(f"无法将变量转换为 int 类型 {lawlabel}。")
            lawfol[lawlabel] = fol
            lawtext[lawlabel] = text

        return lawtext, lawfol


    @classmethod
    def write2file(cls, jsoncontent,filepath):
        json_data = json.dumps(jsoncontent, ensure_ascii=False, indent=4)
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)

    @classmethod
    def add2file(cls, jsoncontent,filepath):
        json_data = json.dumps(jsoncontent, ensure_ascii=False, indent=4)
        # 写入文件
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(',\n')
            f.write(json_data)


    @classmethod
    def getlabel(cls, taskint):
        label_list = []
        if taskint == cls.config["TASK"]['article']:
            with open(cls.config["lawlabelpath"], 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    label = line.strip()
                    try:
                        label = int(label)
                    except ValueError:
                        print(f'label无法转换int {label}')
                        label =  -1
                    label_list.append(label)

        elif taskint == cls.config["TASK"]['crime']:
            with open(cls.config["crimelabelpath"], 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    label = line.strip()
                    label_list.append(label)
        elif taskint == cls.config["TASK"]['penalty']:
            penaltyStrlabel = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下","两年以上三年以下", "三年以上五年以下", "五年以上七年以下","七年以上十年以下", "十年以上","死刑","无期"]
            label_list = [i for i in range(len(penaltyStrlabel))] 
        return label_list
    
    @classmethod
    def getPenaltyIntStrlabel(cls):
        penaltyStrlabel = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下","两年以上三年以下", "三年以上五年以下", "五年以上七年以下","七年以上十年以下", "十年以上","死刑","无期"]
        label_list = [i for i in range(len(penaltyStrlabel))]
        return label_list,penaltyStrlabel


    # 获得标签列表
    # 输出dict key=lawlabel, item=text
    @classmethod
    def altextDict(cls):
        filepath = './mydata/gpt2fol/lawlabeltxt.json'
        atextDict = dict()
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file) # 返回的是json数组
        for item in data:
            key = item['lawlabel']
            text = item['text']
            atextDict[key] = text
        return atextDict
    
    @classmethod
    def readcrimelabellist(cls):
        crimelabel_path = './mydata/CAIL2018/crimeLabel.json'
        crimelablelist = []
        crimelabeldict = dict()
        lineno = 0
        with open(crimelabel_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                crime = line.strip()
                crimelablelist.append(crime)
                crimelabeldict[crime] = lineno
                lineno +=1
        return crimelablelist, crimelabeldict
    
    @classmethod
    def getCrimelabelDict(cls,crimelablelist):
        lineno = 0
        crimelabeldict = dict()
        for crime in crimelablelist:
            crimelabeldict[crime] = lineno
            lineno +=1
        return crimelabeldict

    @classmethod
    def readCrimeRule(cls):
        path = './mydata/CaseItem/caseitem.json'
        with open(path, 'r', encoding='utf-8') as file:
            rulelist = json.load(file)
        ruledict = dict()
        for rule in rulelist:
            crime = rule['crime']
            rule = rule['fol']
            ruledict[crime] = rule
        return ruledict

    @classmethod
    def readCrimeArticleDict(cls):
        returndict = dict()
        # key: crime_name str
        # item: article list
        filepath = './mydata/CaseItem/crime_rule_1.json'
        with open(filepath, 'r', encoding='utf-8') as file:
            crime_articles = json.load(file)

        for rule in crime_articles:
            crime = rule['crime']
            articles = rule['articles']
            returndict[crime] = articles
        
        return returndict

    @classmethod
    def readtext(cls,path):
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']  # 常见的中文编码列表

        lines = []
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as file:
                    lines = file.readlines()
                    lines = [line.strip() for line in lines]
                    break  # 如果成功读取，跳出循环
            except UnicodeDecodeError:
                continue  # 如果当前编码无法读取，尝试下一个编码

        return lines
    
    @classmethod
    def extract_data(cls,text):
        # 定义一个字典来保存提取的数据
        result = {}
        tiao_pattern = re.compile(r'^第([零一二三四五六七八九十百千万]+)条')
        zhang_patter = re.compile(r'^第([零一二三四五六七八九十百千万]+)章')
        jie_patter = re.compile(r'^第([零一二三四五六七八九十百千万]+)节')

        lineindex = 0
        while lineindex < len(text):
            line = text[lineindex].strip()
            match_zhang = re.findall(zhang_patter,line)
            match_tiao = re.findall(tiao_pattern,line)
            match_jie = re.findall(jie_patter,line)


            if line == '\n':
                lineindex +=1
                continue                
            elif len(match_zhang)!=0 or len(match_jie)!=0:
                lineindex +=1
                continue
            elif len(match_tiao)!=0:
                item = line.replace('\u3000','')
                key = cn2an.cn2an(match_tiao[0])
                result[key] = item
                lineindex +=1
                if lineindex >= len(text):
                    break
                line = text[lineindex]
                match_zhang = re.findall(zhang_patter,line)
                match_tiao = re.findall(tiao_pattern,line)
                match_jie = re.findall(jie_patter,line)
                while len(match_zhang)==0 and len(match_tiao)==0 and len(match_jie) ==0: # 直到下一条或者下一章
                    item += line
                    result[key] = item
                    lineindex +=1
                    if lineindex >= len(text):
                        break
                    line = text[lineindex]
                    match_zhang = re.findall(zhang_patter,line)
                    match_tiao = re.findall(tiao_pattern,line)
                    match_jie = re.findall(jie_patter,line)

            print(lineindex)
            print(match_tiao)
        return result

    @classmethod
    def readlawtxt(cls,path):
        encodings = ['utf-8-sig']  # 常见的中文编码列表

        # pattern = re.compile(r'第([一二三四五六七八九十百千万]+)条.*?(?=\n\n|$)', re.DOTALL)
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as file:                   
                    lines = file.readlines()
                    # content = file.read()
                    
                    break  # 如果成功读取，跳出循环
            except UnicodeDecodeError:
                continue  # 如果当前编码无法读取，尝试下一个编码

        return lines
    
    '''
        CAIL2018数据集中的label集合，
    '''
    @classmethod
    def getlabel_cail2018(cls, taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        readpath = './mydata/pljp/CAIL18_test.json'
        lawlabel_list = []
        crimelabel_list = []

        with open(readpath, 'r') as file:
            datas = json.load(file)
            for json_data in datas:
                relevant_article = json_data['article']
                accusation = json_data['charge']

                if relevant_article not in lawlabel_list:
                    lawlabel_list.append(relevant_article)
                if accusation not in crimelabel_list:
                    crimelabel_list.append(accusation)

        if taskint == TASK['article']:
            return lawlabel_list
        elif taskint == TASK['crime']:
            return crimelabel_list
        elif taskint == TASK['penalty']:
            penaltyStrlabel = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下","两年以上三年以下", "三年以上五年以下", "五年以上七年以下","七年以上十年以下", "十年以上","死刑or无期"]
            label_list = [i for i in range(len(penaltyStrlabel))] 
            return label_list
    
    @classmethod
    def getlabel_cjo22(cls, taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        readpath = './mydata/pljp/CJO22_test.json'
        crimepath ='./mydata/CaseItem/init_crimerule_cjo22.json'
        lawlabel_list = []
                
        with open(readpath, 'r') as file:
            datas = json.load(file)
            for json_data in datas:
                relevant_article = json_data['article']
                if relevant_article not in lawlabel_list:
                    lawlabel_list.append(relevant_article)

        crimelabel_list = []
        crimelabeldict = dict()
        with open(crimepath, 'r') as cfile:
            datas = json.load(cfile)
            for json_data in datas:
                crime = json_data['crime']
                crime_int = json_data['crimeint']
                crimelabel_list.append(crime)
                crimelabeldict[crime]=crime_int
        if taskint == TASK['article']:
            return lawlabel_list
        elif taskint == TASK['crime']:
            return crimelabel_list, crimelabeldict
        elif taskint == TASK['penalty']:
            penaltyStrlabel = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下","两年以上三年以下", "三年以上五年以下", "五年以上七年以下","七年以上十年以下", "十年以上","死刑or无期"] #cjo22没"死刑or无期"
            label_list = [i for i in range(len(penaltyStrlabel))] 
            return label_list
    
    @classmethod
    def getArticle_Crime_cjo(cls):
        crimepath ='./mydata/CaseItem/init_crimerule_cjo22.json'
        crimeint2Name =dict()
        crimeName2int = dict()
        crime_articlelist = list() # crime和article的对
        with open(crimepath, 'r') as cfile:
            datas = json.load(cfile)
            for json_data in datas:
                crime = json_data['crime']
                crime_int = json_data['crimeint']
                article = json_data['article']
                crimeint2Name[crime_int] = crime
                crimeName2int[crime] = crime_int
                ca = (crime_int,article)
                crime_articlelist.append(ca)
        return crimeint2Name, crimeName2int,crime_articlelist
    

    @classmethod
    def getrule_cail18(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            lawrulepath = './mydata/gpt2fol/law2fol.json'
            lawrulelsit = {}
            with open(lawrulepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                article = rule['lawlabel']
                article_text = rule['text']
                article_rule = rule['fol']
                lawrulelsit[article] = article_rule
            return lawrulelsit
        
        if taskint ==TASK['crime']:
            updaterule_path = './mydata/CaseItem/caseitem.json'
            with open(updaterule_path, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            ruledict = dict()
            for rule in rulelist:
                crime = rule['crime']
                rule = rule['fol']
                ruledict[crime] = rule
            return ruledict
        
        if taskint == TASK['penalty']:
            parulepath = './mydata/CaseItem/init_penaltyrule_cail.json'
            update_prulpath = './mydata/CaseItem/update_penaltyrule_cail.json'
            parulelist = {}
            with open(parulepath, 'r', encoding='utf-8') as file:
                init_rulelist = json.load(file)
            with open(update_prulpath, 'r', encoding='utf-8') as file2:
                update_rulelist = json.load(file2)
            for rule in update_rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']

                pakey = (penaltyindex,article)
                paitem = (prule,article_text)
                parulelist[pakey] = paitem
            
            for rule in init_rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']
                pakey = (penaltyindex,article)
                paitem = (prule,article_text)

                if pakey not in parulelist.keys():
                    parulelist[pakey] = paitem

            return parulelist

    @classmethod
    def getinitrule_cjo22(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            lawrulepath = './mydata/CaseItem/init_articlerule_cjo22.json' # 初始规则
            lawrulelsit = {}
            with open(lawrulepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                article = rule['article']
                article_text = rule['article_text']
                article_rule = rule['rule']
                lawrulelsit[article] = article_rule
            return lawrulelsit
        if taskint == TASK['crime']:
            init_crimerulepath = './mydata/CaseItem/init_crimerule_cjo22.json'
            crimerulepath = './mydata/CaseItem/update_crimerule_cjo22.json'

            crimerulelist = {}
            crimelabeldict = dict()                
            with open(init_crimerulepath, 'r', encoding='utf-8') as file:
                prerulelist = json.load(file)
                for json_data in prerulelist:
                    crime = json_data['crime']
                    crime_int = json_data['crimeint']
                    crimelabeldict[crime]=crime_int # key:crime_name, item:int
            with open(init_crimerulepath, 'r', encoding='utf-8') as file2:
                rulelist = json.load(file2)
            for rule in rulelist:
                article = rule['article']
                article_text = rule['article_text']
                crime_int = rule['crimeint']
                crule = rule['rule']
                cakey = (crime_int,article)
                caitem =(crule,article_text)
                crimerulelist[cakey] = caitem
            return crimerulelist
        
        if taskint == TASK['penalty']:
                parulepath = './mydata/CaseItem/init_penaltyrule_cjo22.json'
                parulelist = {}
                with open(parulepath, 'r', encoding='utf-8') as file:
                    rulelist = json.load(file)
                for rule in rulelist:
                    penaltyindex = rule['penaltyindex']
                    prule = rule['rule']
                    article = rule['article']
                    article_text = rule['article_text']

                    pakey = (penaltyindex,article)
                    paitem = (prule,article_text)
                    parulelist[pakey] = paitem
                
                return parulelist

    @classmethod
    def getrule_cjo22(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            # lawrulepath = './mydata/CaseItem/init_articlerule_cjo22.json' # 初始规则
            lawrulepath = './mydata/CaseItem/update_articlerule_cjo22.json' # 更新后
            lawrulelsit = {}
            with open(lawrulepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                article = rule['article']
                article_text = rule['article_text']
                article_rule = rule['rule']
                lawrulelsit[article] = article_rule
            return lawrulelsit
        if taskint == TASK['crime']:
            init_crimerulepath = './mydata/CaseItem/init_crimerule_cjo22.json'
            crimerulepath = './mydata/CaseItem/update_crimerule_cjo22.json'

            crimerulelist = {}
            crimelabeldict = dict()                
            with open(init_crimerulepath, 'r', encoding='utf-8') as file:
                prerulelist = json.load(file)
                for json_data in prerulelist:
                    crime = json_data['crime']
                    crime_int = json_data['crimeint']
                    crimelabeldict[crime]=crime_int # key:crime_name, item:int
            with open(crimerulepath, 'r', encoding='utf-8') as file2:
                rulelist = json.load(file2)
            for rule in rulelist:
                article = rule['article']
                article_text = rule['article_text']
                crime_int = rule['crimeint']
                crule = rule['rule']
                cakey = (crime_int,article)
                caitem =(crule,article_text)
                crimerulelist[cakey] = caitem

            return crimerulelist

        if taskint == TASK['penalty']:
            parulepath = './mydata/CaseItem/init_penaltyrule_cjo22.json'
            parulelist = {}
            with open(parulepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']

                pakey = (penaltyindex,article)
                paitem = (prule,article_text)
                parulelist[pakey] = paitem
            
            return parulelist

    # 没有对比学习的更新
    @classmethod
    def getwoCLrule_cjo22(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            lawrulepath = './mydata/CaseItem/init_articlerule_cjo22.json' # 初始规则
            update_lawrulepath = './mydata/CaseItem/update_articlerule_cjo22.json' # 更新后

            lawrulelsit,up = {},{}
            with open(lawrulepath, 'r', encoding='utf-8') as file:
                init_rulelist = json.load(file)
            with open(update_lawrulepath, 'r', encoding='utf-8') as file:
                update_rulelist = json.load(file)
            
            for rule in update_rulelist:
                article = rule['article']
                article_text = rule['article_text']
                article_rule = rule['rule']
                up[article] = article_rule

            for rule in init_rulelist:
                article = rule['article']
                article_text = rule['article_text']
                article_rule = rule['rule']
                if random.random() > 0.7:
                    lawrulelsit[article] = up[article]
                else:
                    lawrulelsit[article] = article_rule
            return lawrulelsit
        
        if taskint == TASK['crime']:
            init_crimerulepath = './mydata/CaseItem/init_crimerule_cjo22.json'
            crimerulepath = './mydata/CaseItem/update_crimerule_cjo22.json'

            crimerulelist = {}
            crimelabeldict = dict()
            with open(init_crimerulepath, 'r', encoding='utf-8') as file:
                prerulelist = json.load(file)
            for json_data in prerulelist:
                crime = json_data['crime']
                crime_int = json_data['crimeint']
                crimelabeldict[crime]=crime_int # key:crime_name, item:int

                article = json_data['article']
                article_text = json_data['article_text']
                crule = json_data['rule']
                cakey = (crime_int,article)
                caitem =(crule,article_text)
                crimerulelist[cakey] = caitem

            with open(crimerulepath, 'r', encoding='utf-8') as file2:
                rulelist = json.load(file2)
            for rule in rulelist:
                article = rule['article']
                article_text = rule['article_text']
                crime_int = rule['crimeint']
                crule = rule['rule']
                cakey = (crime_int,article)
                caitem =(crule,article_text)
                if random.random() > 0.7:
                    crimerulelist[cakey] = caitem
            return crimerulelist
        
        if taskint == TASK['penalty']:
                parulepath = './mydata/CaseItem/init_penaltyrule_cjo22.json'
                parulelist = {}
                with open(parulepath, 'r', encoding='utf-8') as file:
                    rulelist = json.load(file)
                for rule in rulelist:
                    penaltyindex = rule['penaltyindex']
                    prule = rule['rule']
                    article = rule['article']
                    article_text = rule['article_text']

                    pakey = (penaltyindex,article)
                    paitem = (prule,article_text)
                    parulelist[pakey] = paitem
                
                return parulelist

    @classmethod
    def penalty2index(cls,death,wuqi,month): # 可参考 ExtractCase.py penalty2str
        if death or wuqi:
            i = 10
        elif month > 10*12:
            i = 9
        elif month > 7*12:
            i = 8
        elif month > 5*12:
            i = 7
        elif month > 3*12:
            i = 6
        elif month > 2*12:
            i = 5
        elif month > 1*12:
            i = 4
        elif month > 9:
            i = 3
        elif month > 6:
            i = 2
        elif month > 0 :
            # print(f"刑期是{month}")
            i = 1
        else:
            i = 0
        return i
    
    '''
        读取penalty的rule
        key = (penalty,article)
        item = (rule,article_text)
    '''
    @classmethod
    def readPenaltyrule(cls):
        path_cjo = './mydata/CaseItem/init_penaltyrule_cjo22.json'
        with open(path_cjo, 'r', encoding='utf-8') as file:
            rulelist = json.load(file)
        returndict = {}
        for rule in rulelist:
            penaltyindex = rule['penaltyindex']
            prule = rule['rule']
            article = rule['article']
            article_text = rule['article_text']

            pakey = (penaltyindex,article)
            paitem = (prule,article_text)
            returndict[pakey] = paitem
        
        return returndict


# 读没有经过优化的规则，cail数据集的
    @classmethod
    def read_woCL_cailRule(cls,taskint):
        TASK = { "article": 0, "crime":1, "penalty":2 }
        if taskint == TASK['article']:
            # lawrulepath = './mydata/gpt2fol/law2fol.json'
            lawlabelpath = './mydata/gpt2fol/lawlabeltxt.json'
            init_folpath = './mydata/gpt2fol/law2folLog.json'
            lawrulelsit,lawtxtlist = {},{}
            with open(init_folpath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            for rule in rulelist:
                article = rule['lawlabel']
                article_text = rule['text']
                article_rule = rule['fol']
                lawrulelsit[article] = article_rule
                lawtxtlist[article] = article_text
            
            update_folpath = './mydata/gpt2fol/law2fol.json'
            with open(update_folpath, 'r', encoding='utf-8') as file:
                follist = json.load(file)
            for item in follist:
                lawlabel = item['lawlabel']
                fol = item['fol']
                text = item['text']
                if not isinstance(lawlabel, int):
                    try:
                        lawlabel = int(lawlabel)
                    except ValueError:
                        print(f"无法将变量转换为 int 类型 {lawlabel}。")
                
                if random.random() > 0.7:
                    lawrulelsit[lawlabel] = fol

            return lawtxtlist,lawrulelsit
        
        if taskint ==TASK['crime']:
            update_crimerulepath = './mydata/CaseItem/caseitem.json'
            init_crimepath = './mydata/CaseItem/init_crimeitem_cail.json'
            rulelist =[]
            with open(init_crimepath, 'r', encoding='utf-8') as file:
                rulelist = json.load(file)
            ruledict = dict()
            for rule in rulelist:
                crime = rule['crime']
                rule = rule['rule']
                ruledict[crime] = rule

            with open(update_crimerulepath, 'r', encoding='utf-8') as file:
                uprulelist = json.load(file)
            for rule in uprulelist:
                crime = rule['crime']
                rule = rule['fol']
                if random.random() > 0.7:
                    ruledict[crime] = rule
            return ruledict

        if taskint == TASK['penalty']:
            parulepath = './mydata/CaseItem/init_penaltyrule_cail.json'
            update_prulpath = './mydata/CaseItem/update_penaltyrule_cail.json'
            parulelist = {}
            with open(parulepath, 'r', encoding='utf-8') as file:
                init_rulelist = json.load(file)
            with open(update_prulpath, 'r', encoding='utf-8') as file2:
                update_rulelist = json.load(file2)
            for rule in update_rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']

                pakey = (penaltyindex,article)
                paitem = (prule,article_text)
                parulelist[pakey] = paitem
            
            for rule in init_rulelist:
                penaltyindex = rule['penaltyindex']
                prule = rule['rule']
                article = rule['article']
                article_text = rule['article_text']
                pakey = (penaltyindex,article)
                paitem = (prule,article_text)

                if pakey not in parulelist.keys():
                    parulelist[pakey] = paitem
                if pakey in parulelist.keys() and random.random()>=0.3:
                    parulelist[pakey] = paitem

            return parulelist

import pandas as pd
import numpy as np

def connect():
    TASK_NAME = ["article", "crime", "penalty"]
    train_path= "./mydata/CAIL2018/data/smallmodeldata/train_crime.csv"
    test_path="/data2/zhZH/PLJP/data/csv/CAIL18/test_crime.csv"
    df = pd.read_csv(train_path.format(taskname = "crime"))
    df2 =  pd.read_csv(test_path.format(taskname = "crime"))
    df_test = pd.read_csv(test_path.format(taskname = "crime"))
    df_train1 = df.sample(frac=0.6, random_state= None )
    df_split = np.split(df2.sample(frac=0.2, random_state= None), [int(0.2*0.2*len(df2)), int(0.3*0.2*len(df2))])
    df_train2 = df_split[0]
    df_val = df_split[1]

    df_train = df_train2.append(df_train1)

    print(f'len(df_train) = {len(df_train)}')
    print(f'len(df_val) = {len(df_val)}')
    print(f'len(df_test) = {len(df_test)}')

