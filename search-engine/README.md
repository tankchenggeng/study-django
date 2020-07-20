## 关键词搜索

### 安装django搜索引擎依赖
------

**1. jieba中文分词**

安装分词框架
安装jieba库
```shell
sudo pip3 install jieba
```
jieba三种分词模式：
```python
import jieba

searchinfo = "djando开发过程,遇到了系统crash的bug"
print("精简模式: ", jieba.lcut(searchinfo)) # 精简模式
print("全模式: ", jieba.lcut(searchinfo, cut_all=True)) # 全模式
print("搜索引擎模式: ", jieba.lcut_for_search(searchinfo)) # 搜索引擎模式
```
输出如下：
```shell
精简模式:  ['djando', '开发', '过程', ',', '遇到', '了', '系统', 'crash', '的', 'bug']
全模式:  ['djando', '开发', '发过', '过程', ',', '遇到', '了', '系统', 'crash', '的', 'bug']
搜索引擎模式:  ['djando', '开发', '过程', ',', '遇到', '了', '系统', 'crash', '的', 'bug']
```
-------------------
**2. django-haystack**

安装搜索框架
```shell
sudo pip3 install django-haystack
```
------------------
**3. 安装搜索引擎**

```shell
sudo pip3 install whoosh
```

### 配置全文检索

**1. 加入haystack应用, 配置搜索引擎**

打开settings.py，按如下方式添加
```python
INSTALLED_APPS = [
    ...
    'haystack',
]


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}
# 当添加．修改．删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
```

**2. 在要建立检索的表对应的应用下，创建search_indexes.py文件**

对于此项目，我们在应用issuesystem目录下新建search_indexes.py文件(名称固定不可更改)
添加如下代码：
```python
# encoding=utf-8
"""
    定义ISSUE索引类
"""
from haystack import indexes
from issuesystem.models import Issue

class IssueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # 针对那张表进行查询
    def get_model(self):
        return Issue
    #　针对哪些行进行查询(建立索引的数据)
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
```

**3. 指定要索引的字段**

在项目目录下templates文件夹下面新建目录search/indexes/应用名
对于issuesystem，我们新建search/indexes/issuesystem文件夹，并在此文件夹下新建一个issue_text.txt文件，添加我们要检索的字段，issue系统准备使用标题和描述进行查询

```txt
# 指定表中的哪些字段建立索引
{{ object.title }} # 根据标题建立索引
{{ object.description }} # 根据描述建立索引
```

**4. 生成索引文件**

终端运行，提示是否要删除原有信息，输入y
```shell
$ python3 manage.py rebuild_index
```

### 使用检索
**1. 搜索表单编写**

在html中的搜索表单按如下方式编写
method="get", name="q", action="/search/"
```html
<form method="get" action="/search/">
  <input type="text" class="input_text fl" name="q">
  <input type="submit" class="input_btn fr" name="" value="搜索">
</form>
```

在项目配置文件夹下的urls.py配置路由
```python
urlpatterns = [
    ...
    path('search/', include('haystack.urls')),
]

```

**2. 搜索结果处理**

搜出结果后，haystack会把搜索出的结果传递给templates/search目录下的search.html．
传递的上下文包含：
a. query: 搜索关键字
b. page: 当前页的page对象
c. paginator: 分页paginator对象
在settings.py设置HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10可以控制每页显示数量为10

search.html
```html
{% extends "issuesystem/base.html" %}
  {% block title %}Issue{% endblock %}
  {% block content %}
  <div class="row">
    <div class="col-12 col-lg-12 col-xl-12">
      <div class="card">
        <div class="table-responsive">
          <table class="table align-items-center">
            <tbody>
              {% for item in page %}
              <tr>
                <td><a href="/issuesystem/showissue/{{ item.object.id }}">{{item.object.title}}</a>
                  <p>{{item.object.description}}</p>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
  {% endblock %}

```

到这里就实现了基本的搜索框搜索功能(但是只能搜索title和description中完全匹配的结果)

**3. 切换分词引擎**

找到haystack的安装路径，python3.5的安装路径为：
/usr/local/lib/python3.5/dist-packages/haystack
打开该目录的backends文件夹

第一步：新建ChineseAnalyzer.py文件，添加如下代码：
```python
import jieba
from whoosh.analysis import Tokenizer, Token

class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
        seglist = jieba.cut(value, cut_all=True)
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
                t.endchar = start_char + value.find(w) + len(w)
            yield t

def ChineseAnalyzer():
    return ChineseTokenizer()
```
第二步：拷贝一个whoosh_backend.py副本，重命名为whoosh_cn_backend.py,并做以下修改
```python
from haystack.utils.app_loading import haystack_get_model
from .ChineseAnalyzer import ChineseAnalyzer  # 添加此行
```
并搜索StemmingAnalyzer，找到analyzer=StemmingAnalyzer()语句，修改为：
analyzer=ChineseAnalyzer()
第三步：
修改settings.py,将搜索引擎由whoosh_backend改为whoosh_cn_backend
```python
#'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
```
执行命令重新生成索引文件
```shell
$ python3 manage.py rebuild_index
```
到这里发生搜索的效果比之前要好一些了．

### 搜索结果高亮

**1. 使用高亮**

haystack自带高亮功能，在我们的html中load highlight样式，如下
```html
...
{% load highlight %}

{% for item in page %}
  {% highlight item.object.title with query %}
{% endfor %}

```
{% load highlight %}这一行往html中导入了高亮的功能，在不需要高亮的时候我们的搜索结果展示方式为{{ item.object.title }},关键字高亮就是把我们要高亮的部分修改为：
{% highlight item.object.title with query %}．这样我们的标题中关键字部分就可以高亮了．
高亮实际上是在原有的基础之上，用span标签包裹了关键字，并添加了highlighted的className，所以我们可以通过设置span.highlighted的样式来修改高亮的样式．

**2. 标题不使用省略号代替**

使用haystack Highliahted搜索结果高亮时，默认会把前面的字符用...代替，但是我们希望标题不使用省略号代替

第一步：
备份haystack下utils文件夹下的highlighting.py
```shell
$ sudo cp highlighting.py highlighting.py_backup
```
第二步：打开highlighting.py
在Highlighter类的初始化函数中增加变量
```python
    ellipsis = 'true'
    def __init__(self, query, **kwargs):
        self.query = query
        ...
        if 'ellipsis' in kwargs:
            self.ellipsis = kwargs['ellipsis']
```
在Highlighter类的render_html函数中修改以下代码
```python
# 原代码
if start_offset > 0:
    highlighted_chunk = '...%s' % highlighted_chunk

if end_offset < len(self.text_block):
    highlighted_chunk = '%s...' % highlighted_chunk
# 修改为
if not self.ellipsis:
    if start_offset > 0:
        highlighted_chunk = self.text_block[0:start_offset] + highlighted_chunk
    if end_offset < len(self.text_block):
        highlighted_chunk = self.text_block[end_offset:] + highlighted_chunk
else:
    if start_offset > 0:
        highlighted_chunk = '...%s' % highlighted_chunk
    if end_offset < len(self.text_block):
        highlighted_chunk = '%s...' % highlighted_chunk
```
第三步：修改highlight.py
打开haystack下的templatetags目录，修改highlight.py,修改以下代码

找到highlight(parser, token)函数下的
```python
    for bit in arg_bits:
        if bit == 'css_class':
            kwargs['css_class'] = six.next(arg_bits)

        if bit == 'html_tag':
            kwargs['html_tag'] = six.next(arg_bits)

        if bit == 'max_length':
            kwargs['max_length'] = six.next(arg_bits)
        # 添加ellipsis
        if bit == 'ellipsis':
            kwargs['ellipsis'] = six.next(arg_bits)
```
找到HighlightNode类，模仿css_class，html_tag，max_length的写法写ellipsis
```python
...
    def __init__(self, text_block, query, html_tag=None, css_class=None, max_length=None, ellipsis=None):
...
self.ellipsis = ellipsis
if ellipsis is not None:
    self.ellipsis = template.Variable(ellipsis)
if self.ellipsis is not None:
    kwargs['ellipsis'] = self.ellipsis.resolve(context)
```

第四步: 使用
模板用法改为
{% highlight item.object.description with query ellipsis 'false' %}

**3. 搜索结果关键词分词**

打开highlighting.py，导入jieba库，找到初始化函数并修改：
```python
# 原代码
self.query_words = set([word.lower() for word in self.query.split() if not　word.startswith('-')])
# 修改为
words = jieba.lcut_for_search(self.query)
self.query_words = set([word.lower() for word in words if len(word)>1])
```

**4. 定义省略号开始的位置和结束位置**

打开highlighting.py,找到find_window()函数
```python
# 原代码
                else:
                    current_density = 0
# 修改为
                else:
                    current_density = 0
                    break
```
find_window函数定义了要显示的区间信息．max_length参数定义了最多显示的文字长度，当前的规则是选取max_length长度内关键字数量最多的一段文字，并将起点设置为显示文字包含的第一个关键字位置．上面代码只是修正了源码中存在的Bug．
改变显示位置
第一步：
我们将起点设置为关键字前10位或从头开始
打开highlighting.py,找到find_window()函数
```python
# 原代码
　　　　　　　　for count, start in enumerate(words_found[:-1]):
            current_density = 1
# 修改为
　　　　　　　　for count, start in enumerate(words_found[:-1]):
            current_density = 1
            start = max(0, start-10)
```

第二步：
修改显示的长度为80
打开highlighting.py,找到Highlighter()类
```python
# 原代码
    css_class = 'highlighted'
    html_tag = 'span'
    max_length = 200
# 修改为
    css_class = 'highlighted'
    html_tag = 'span'
    max_length = 80  # 修改此处
```
由于max_length我们是作为输入参数来使用，所以也可以直接在html上进行设置
模板如下：显示最大为160
```html
<p>{% highlight item.object.description with query max_length 160 %}</p>
```

