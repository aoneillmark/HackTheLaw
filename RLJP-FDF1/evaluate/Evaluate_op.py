# 分析回复文本的操作类
import re
import cn2an
from sklearn.metrics import f1_score, confusion_matrix, precision_recall_fscore_support, classification_report
from sklearn.metrics import precision_recall_fscore_support
import json
from collections import Counter
import os
import jieba

class Evaluate_op:
    def __init__(self,response):
        self.response = response
    
    def __init__(self):
        self.non = 'non'

    @classmethod
    def getArticle(cls,response):

        if len(response)==0:
            return -1

        Flag = True
        for char in response:
            if not char.isdigit():
                Flag = False
                break
        
        if Flag:
            return int(response)
        
        response = re.sub(r'第\w+款', '', response)  # 先删掉第x款
        response = re.sub(r'第\w+项', '', response)  # 先删掉第x项
        response = re.sub(r'第\w+起', '', response)  # 先删掉第x起
        response = re.sub(r'刑法', '', response)  # 先删掉第x起


        if '第' in response:
            pattern = r'第(\S+?)条'  # 匹配 '第x条' 的格式
        else: #if '条' in response:
            pattern = r'(\S+?)条'  # 匹配 '第x条' 的格式

        matches = re.findall(pattern, response)

        # 判断matches中是否有大于7个字的，若有，则删除第一个字，重新进行匹配
        match_articles = []
        for match in matches:
            match_new = re.sub(r'第', '', match) #.replace("第","")
            match_new = re.sub(r'条', '', match_new) # match.replace("条","")
            match_new = re.sub(r':', '', match_new)
            match_new = re.sub(r'：', '', match_new)


            if '，' in match_new:
                matche_news= match_new.split('，')
                for macti in matche_news:
                    match_articles.append(macti)
            elif ',' in match_new:
                matche_news= match_new.split(',')
                for macti in matche_news:
                    match_articles.append(macti)
            else:
                match_articles.append(match_new)
        
        answer = []
        if len(match_articles)> 0 :
            for item in match_articles:
                Flag = False
                for char in item: # item原先是response
                    if char.isdigit():
                        Flag = True
                    else:
                        Flag = False
                        break
                if Flag:
                    item = int(item)
                    answer.append(item)
                    continue
                else:
                    Flag = True
                    allowed_chars = ['零','一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百']
                    for char in item:
                        if char not in allowed_chars:
                            Flag = False  # 存在除了一到九 百 十 之外的字符
                            # print(f'匹配到{char}')
                            break
                    if Flag:
                        try:
                            item = cn2an.cn2an(item, mode='smart')
                            answer.append(item)
                        except:
                            print(f'Evaluate_op getArticle cn2cn {item}')
                            continue            
                answer.append(item)
        else: # 表示未匹配到
            answer.append(-1) 
        if len(answer)< 1:
            return -1
        counter = Counter(answer)
        most_common = counter.most_common(1)
        top_one_numbers = [item[0] for item in most_common]
        
        return top_one_numbers[0]
    
    @classmethod
    def getlabelbyArticle(cls, article,lawlabel):
        if article in lawlabel.keys():
            return article
        return -1
    
    # all_crime_list 所有罪名的列表
    @classmethod
    def getCharge(cls,response, all_crime_list):
        clean_list = ['认罪', '有罪', '犯罪', 'X罪', 'XX罪', 'XXX罪']
        for i in clean_list:
            response = re.sub(i, '', response)

        pattern = r'(.*?)罪'  # 匹配格式
        matches = re.findall(pattern, response)

         # 创建一个用于存放共同元素的新列表
        common_elements = []

        # 遍历第二个列表中的每个元素
        for word in all_crime_list:
            if len(matches) != 0:
                for sentence in matches:
                    if word in sentence:
                        common_elements.append(word)
                        break
            else:
                if word in response or response in word:
                    common_elements.append(word)
                    break

        # 如果为空，则输出0
        if not common_elements:
            return None
        counter = Counter(common_elements)
        most_common = counter.most_common(1)
        top_one_numbers = [item[0] for item in most_common]
        return top_one_numbers[0]

    @classmethod
    def get_ptcls(cls, pt): # pt(月)
        DEATH = -1
        WUQI = -2
        NULL_PENALTY = -3  # 没有给出答案
        
        if pt == DEATH:
            pt_cls = 10
        elif pt == WUQI:
            pt_cls = 11
        elif pt > 10 * 12:
            pt_cls = 9
        elif pt > 7 * 12:
            pt_cls = 8
        elif pt > 5 * 12:
            pt_cls = 7
        elif pt > 3 * 12:
            pt_cls = 6
        elif pt > 2 * 12:
            pt_cls = 5
        elif pt > 1 * 12:
            pt_cls = 4
        elif pt > 9:
            pt_cls = 3
        elif pt > 6:
            pt_cls = 2
        elif pt > 0:
            pt_cls = 1
        else:
            pt_cls = 0
        return pt_cls


    @classmethod
    def getPenalty2(cls, response):
        DEATH = -1
        WUQI = -2
        NULL_PENALTY = -3  # 没有给出答案

        clean_list = ['处']
        for i in clean_list:
            response = re.sub(i, '', response)
        unreal_pt_cls2str = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下",
                             "两年以上三年以下", "三年以上五年以下", "五年以上七年以下",
                             "七年以上十年以下", "十年以上", "死刑", "无期"]
        pt_str = ["其他", "六个月以下", "九个月以下", "一年以下", "两年以下", "三年以下", "五年以下", "七年以下", "十年以下", "十年以上","死刑","无期"]
        pt_numstr = ["其他", "6个月以下", "六个月以上", "九个月以上", "一年以上", "两年以上", "三年以上", "五年以上", "七年以上", "十年以上","死刑","无期"]
        final_result = '其他'
        finalindex = 0
        index = 0
        
        for i in unreal_pt_cls2str:
            if i in response or response in i or pt_str[index] in response or response in pt_str[index] or pt_numstr[index] in response or response in pt_numstr[index]:
                final_result = i
                finalindex = index
                break
            index += 1

        # if '某' in response:
        #     pattern = r'某(\S+?)有期徒刑'  
        # else:
        #     pattern = r'(\S+?)有期徒刑'
        # matches = re.findall(pattern, response)
        
        # for ma in matches:
        #     index = 0
        #     for pt in unreal_pt_cls2str:
        #         if ma in pt or pt in ma or pt_str[index] in ma or ma in pt_str[index] or pt_numstr[index] in ma or ma in pt_numstr[index]:
        #             final_result = i
        #             finalindex = index
        #         index += 1
        if finalindex == 0:
            words = [char for char in response]
            new_words = []
            for word in words:
                try:
                    converted_word = cn2an.cn2an(word, "smart")
                    converted_word = int(converted_word)
                    new_words.append(str(converted_word))
                except (ValueError, IndexError):
                    new_words.append(word)
            response = "".join(new_words)

            yue = NULL_PENALTY
            if '无期' in response:
                yue = WUQI
            elif '死刑' in response:
                yue = DEATH
            else:
                yue_pattern = r'(\d+)个月'  # r'(\d+|\w+)个月'
                yue_matches = re.findall(yue_pattern, response)
                if len(yue_matches) >= 1:
                    yue = yue_matches[-1]
                    if yue.isdigit():
                        yue = int(yue)
                
                nian_pattern = r'(\d+)年' # r'(\d+|\w+)年'
                nian_matches = re.findall(nian_pattern, response)
                if len(nian_matches) >= 1:
                    nian = nian_matches[-1]
                    if nian.isdigit():
                        nian = int(nian)
                        if yue == NULL_PENALTY:
                            yue = nian * 12
                        elif yue != NULL_PENALTY:
                            yue = nian * 12 + yue
                            
            finalindex = Evaluate_op.get_ptcls(yue)
            final_result = unreal_pt_cls2str[finalindex]

    
        return finalindex, final_result
        # response = response.replace("我的选择为","")

        
        # similist = []
        # for item in unreal_pt_cls2str:
        #     paragraph_words = set(jieba.cut(response))
        #     target_phrase_words = set(jieba.cut(item))
        #     common_words = paragraph_words & target_phrase_words
        #     similarity = len(common_words) / len(target_phrase_words)
        #     similist.append(similarity)
        
        # max = -1
        # maxi = -1
        # for index in range(len(similist)):
        #     sim = similist[index]
        #     if sim > max:
        #         max = sim
        #         maxi = index

        # return maxi,max # index, str

    # 都转换成 文字形式
    @classmethod
    def getPenalty(cls,response):
        unreal_pt_cls2str = ["其他", "六个月以下", "六个月以上九个月以下", "九个月以上一年以下", "一年以上两年以下",
                     "两年以上三年以下", "三年以上五年以下", "五年以上七年以下",
                     "七年以上十年以下", "十年以上", "死刑", "无期"]
        response = re.sub(r'其他', '', response)  # 和标签中的“其他”有冲突，先删掉
        line_answer = []
        
        # 先判死刑或无期
        pattern = r'死刑'
        matches1 = re.findall(pattern, response)
        if len(matches1) > 0:
            # line_answer = [True, "死刑", False]
            return len(unreal_pt_cls2str)-2, '死刑'
        pattern = r'无期'
        matches2 = re.findall(pattern, response)
        if len(matches2) > 0:
            # line_answer = [False, "无期", True]
            return len(unreal_pt_cls2str)-1, '无期'
        
        

        pattern = r'处(\S+?)有期徒刑'  # 处有期徒刑
        matches = re.findall(pattern, response)
        # 降一下重
        unique_list = []
        for l1 in matches:
            if l1 not in unique_list:
                unique_list.append(l1)
        # print(unique_list)

        # 判断期限
        modi_list = []
        modi2_list = []
        for pi in unique_list:
            if pi.isdigit():
                pindex = Evaluate_op.get_ptcls(int(pi))
                pp = unreal_pt_cls2str[pindex]
                modi_list.append(pp)
            else:
                for p_str in unreal_pt_cls2str:
                    if p_str in pi or pi in p_str:
                        pp = p_str
                        modi_list.append(pp)

                for l1 in modi_list: # 降重
                    if l1 not in modi2_list:
                        modi2_list.append(l1)

        if len(modi2_list) != 0:
            final_result = modi2_list[-1]  # 回答中可能有多个结果，取最后一项作为最终的结果

        else:
            final_result = '其他'
            for i in unreal_pt_cls2str:
                if i in response:
                    final_result = i
                    break

        finalindex = 0
        for index in range(len(unreal_pt_cls2str)):
            pstr = unreal_pt_cls2str[index]
            if pstr == final_result:
                finalindex = index
        return finalindex, final_result # final_result = pstr
    
    
    # 覆盖写
    @classmethod
    def writeLog(cls, loglist,file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(loglist, json_file, ensure_ascii=False, indent=4)
                json_file.write('\n')
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")

    @classmethod
    def writeJsonLog(cls, jsonlog,file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            with open(file_path, 'a', encoding='utf-8') as json_file:
                json.dump(jsonlog, json_file, ensure_ascii=False, indent=4)
                json_file.write('\n')
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")

    # 计算acc
    @classmethod
    def caculate_ACC(cls, predictlist, truelist):
        acc, _, _, _ = precision_recall_fscore_support(truelist, predictlist, average='micro')
        map, mar, maf, _ = precision_recall_fscore_support(truelist, predictlist, average='macro')

        acc = round(acc, 6) * 100
        map = round(map, 6) * 100
        mar = round(mar, 6) * 100
        maf = round(maf, 6) * 100

        return acc,map,mar,maf
    
    # 计算ACC+ 写log
    @classmethod
    def writeAnswer(cls, index,filepath, truelist, predictlist):
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        acc, _, _, _ = precision_recall_fscore_support(truelist, predictlist, average='micro')
        map, mar, maf, _ = precision_recall_fscore_support(truelist, predictlist, average='macro')

        acc = round(acc, 6) * 100
        map = round(map, 6) * 100
        mar = round(mar, 6) * 100
        maf = round(maf, 6) * 100

        # log = {"task":"Article / Charge / Penalty","true":[], "predict":[]}
        log = { "index":index,"acc":acc, "map":map, "mar":mar, "maf":maf}
        
        with open(filepath, 'a') as file:
            file.write(json.dumps(log)+'\n')

    # 更新写fol文件
    @classmethod
    def writeFOL(cls, follist,file_path):
        jsonlist = []
        for key,fol in follist.items():
            jsonitem = dict()            
            jsonitem["lawlabel"] = int(key)
            jsonitem["fol"] = fol
            jsonlist.append(jsonitem)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(jsonlist, json_file, ensure_ascii=False, indent=4)
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")

    # 更新chargeitem 文件
    @classmethod
    def writeChargeItemlist(cls, ChargeItemlist,file_path):
        jsonlist = []
        for key,itemlist in ChargeItemlist.items():
            jsonitem = dict()            
            jsonitem["ArticleCharge"] = (key[0],key[1])
            jsonitem["items"] = itemlist
            jsonlist.append(jsonitem)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(jsonlist, json_file, ensure_ascii=False, indent=4)
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")

    # 更新penaltyitem文件
    @classmethod
    def writePenaltyItemlist(cls, PenaltyItemlist, file_path):
        jsonlist = []
        for key,itemlist in PenaltyItemlist.items():
            jsonitem = dict()            
            jsonitem["ArticleChargePenalty"] = (key[0],key[1],key[2])
            jsonitem["items"] = itemlist
            jsonlist.append(jsonitem)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(jsonlist, json_file, ensure_ascii=False, indent=4)
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")

    # 更新 article--charge的文件
    @classmethod
    def writelaw2C(cls, law2c, file_path):
        jsonlist = []
        for key,crimelist in law2c.items():
            jsonitem = dict()            
            jsonitem["article"] = int(key)
            jsonitem["charge"] = crimelist
            jsonlist.append(jsonitem)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(jsonlist, json_file, ensure_ascii=False, indent=4)
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")
            
    @classmethod
    def writelawC2P(cls,lawC2P, file_path):
        jsonlist = []
        for key,penIndexlist in lawC2P.items():
            jsonitem = dict()
            jsonitem["ArticleCharge"] = (key[0],key[1])#元组(article, crime)
            jsonitem["penaltyStrIndex"] = penIndexlist
            jsonlist.append(jsonitem)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(jsonlist, json_file, ensure_ascii=False, indent=4)
            print(f"数据成功写入到 {file_path}")
        except Exception as e:
            print(f"写入文件时出现错误：{e}")


    @classmethod
    def multiitem(cls,number_list):
        frequency_dict = {}
        for num in number_list:
            if num == -1:
                frequency_dict [-1] = 1
            elif num in frequency_dict:
                frequency_dict[num] += 1
            else:
                frequency_dict[num] = 1
                frequency_dict [-1] = 0
        
        most_frequent_number = None
        max_frequency = 0
        for number, frequency in frequency_dict.items():
            if frequency > max_frequency:
                most_frequent_number = number
                max_frequency = frequency

        print(f"{number_list}列表中出现最频繁的一项是：{most_frequent_number}")
        return most_frequent_number