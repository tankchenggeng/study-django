#encoding=utf-8

import jieba

def index_of_str(s1, s2):
    lt = s1.split(s2, 1)
    if len(lt) == 1:
        return 0, -1
    return len(s2), len(lt[0])

searchinfo = "What can I， do for you智障"
print("精简模式: ", jieba.lcut(searchinfo)) # 精简模式
print("全模式: ", jieba.lcut(searchinfo, cut_all=True)) # 全模式
print("搜索引擎模式: ", jieba.lcut_for_search(searchinfo)) # 搜索引擎模式
words = jieba.lcut_for_search(searchinfo)
searchinfo = searchinfo.replace(" ", "")
while " " in words:
    words.remove(" ")
for word in words:
    wordlen, index = index_of_str(searchinfo, word)
    if 64<ord(word[0])<91 or 66<ord(word[0])<123:
        count = 1
    else:
        count = wordlen
    print(wordlen, index, count)
a = list([5, 35, 29])
print(sorted(a)[::-1])


