### 多级评论

**1. 安装django官方多级评论库**

```shell
$ sudo pip3 install django-mptt
```

**2. 修改配置文件settings.py**

```python
...
INSTALLED_APPS = [
    ...
    'mptt',
    ...
]
```

**3. 添加评论模型**

第一步:创建评论模型，需要继承MPTTModel，并且有一个parent字段
打开issuesystem下的models.py,添加以下代码
```python

from mptt.models import MPTTModel, TreeForeignKey

class Comment(MPTTModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField()
    parent = TreeForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    reply_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='replied')
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # 对象显示内容
        return self.content
```
模型各字段解析:
1.issue作为外键与每一个具体的issue关联,因为每一条评论都对应着一个Issue
2.user是comment评论发布人
3.content是评论内容
4.parent存放一级评论,当此评论本身为一级评论时,为空,这样从数据库获取评论时可以根据该值为空过滤一级评论
5.reply_to用于非一级评论,即当我们的评论对象是某一条评论时,我们使用reply_to存放真实的被评论人.虽然评论可以无限级,但是无限级评论的展示无法排版,所以我们将所有超过二级的评论重置为二级评论,即将其parent设置为对应的一级评论,而不再是所回复的评论,并将reply_to设置为真实的评论人.
6.created_time存储评论发生的时间

第二步:执行数据库迁移
```shell
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

**4. 添加评论视图**

打开应用issuesystem下的views.py,添加视图
```python

@login_required
def comment(request, issueid, commentid=None):
    issue = get_object_or_404(models.Issue, id=issueid)  # 确认所属issue
    if request.method == 'POST':
        user = request.user
        content = request.POST.get("content")
        # 非一级评论
        if commentid:
            parent_comment = models.Comment.objects.get(id=commentid)
            # 若回复层级超过二级，则转换为二级
            parent_id = parent_comment.get_root().id
            # 被回复人
            reply_to = parent_comment.user
            models.Comment.objects.create(issue=issue,
                                          user=user,
                                          content=content,
                                          parent_id=parent_id,
                                          reply_to=reply_to)
        else:
            models.Comment.objects.create(issue=issue,
                                          user=user,
                                          content=content)
        return redirect('/issuesystem/showissue/%s'%(issueid))
    return render(request, apptemplates('comment.html'), {"issueid": issueid,
                                                          "commentid":commentid})
```
在视图函数中我们分别实现了一级评论和二级评论的创建过程,并在创建成功后继续跳转至查看issue的界面

**5. 添加评论路由**

打开应用issuesystem下的urls.py,添加路由
```python
path('comment/<int:issueid>', views.comment),
path('comment/<int:issueid>/<int:commentid>', views.comment),
```
在第4点中我们给视图函数设置了一个固定参数issueid和可选参数commentid,所以在urls.py中我们也添加了2个路由

**6. 添加评论模板文件**

在templates的issuesystem目录下创建模板文件comment.html
```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8"/>
  <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>
  <meta name="description" content="FOXCONN AI"/>
  <meta name="author" content="Tank"/>
  <title>COMMENT</title>
  <!-- loader-->
  {% load staticfiles %}
  <!--favicon-->
  <link rel="icon" href="{% static 'assets/images/favicon.ico' %}" type="image/x-icon">
  <!-- Custom Style-->
  <link href="{% static 'assets/css/app-style.css' %}" rel="stylesheet"/>
</head>
<body class="bg-theme bg-theme2">
    <div style="text-align: center;">
        <form action="{% if commentid %}
        /issuesystem/comment/{{issueid}}/{{commentid}}
        {% else %}
        /issuesystem/comment/{{issueid}}
        {% endif %}" method="post">
            {% csrf_token %} <!-- 跨域请求，-->
            <div class="form-group">
              <label>评论:</label>
              <input type="text" name='content' class="form-control" required>
            </div>
            <input type="submit" name="提交" value="发布">
          </form>
    <div>
</body>
</html>
```
这里注意,在设置表单跳转时,我们的action是根据commentid动态设置的,这个与路由是对应的,我们从哪个路由进行的表单填写,表单就应该提交到哪个路由中.


**7. 评论展示**

第一步:修改视图函数
打开应用issuesystem下的views.py,找到showissue,添加获取comment的代码
```python
# 修改前

    return render(request, apptemplates('showissue.html'), 
                  {"issue":issue, "publishtime":publishtime, 
                   "images":images})
# 修改后
    comments = issue.comments.filter(parent=None).order_by('-created_time')
    return render(request, apptemplates('showissue.html'), 
                  {"issue":issue, "publishtime":publishtime, 
                   "images":images, "comments": comments})
```

第二步:修改模板文件
打开templates的issuesystem目录下的模板文件showissue.html,添加如下代码
```html
...
{% load mptt_tags %}
...

<div><a href="/issuesystem/comment/{{ issue.id }}">添加我的评论</a></div>
<h4>共有{{ comments.count }}条评论</h4>
<div class="list-comments">
   <!-- 遍历树形结构 -->
   {% recursetree comments %}
   <!-- 给 node 取个别名 comment -->
   {% with comment=node %}
      <div class="col-12">
        <hr>
          <p><strong style="color: pink">{{ comment.user }}</strong>:{{ comment.content|safe }}</p>
          <div>
            <span style="color: gray">{{ comment.created_time|date:"Y-m-d H:i" }}</span>
            <a href="/issuesystem/comment/{{ issue.id }}/{{comment.id}}">回复</a>
          </div>
          {% if comment.children.all.count %}
            评论数：<i>{{comment.children.all.count}}</i>
            {% for cc in comment.children.all %}
              <div class="col-11">
              <hr>
              <p>
                <strong style="color: pink">{{ cc.user }}</strong>回复
                <strong style="color: pink">{{ cc.reply_to }}</strong>:{{ cc.content|safe }}
              </p>
              <div>
                <span style="color: gray">{{ cc.created_time|date:"Y-m-d H:i" }}</span>
                <a href="/issuesystem/comment/{{ issue.id }}/{{cc.id}}">回复</a>
              </div>
            </div>
            {% endfor %}
          {% endif %}
        </div>
    {% endrecursetree %}
</div>
```
首先为issue添加了一个评论链接,和issue的评论数.
紧接着遍历comments树形结构,由于在视图函数中我们已经过滤出了一级评论,所以此处本可以不用树形结构遍历,但是我们还是用树形结构演示一下.首先循环展示每一个一级评论,并给每一个一级评论添加评论数的统计和回复链接.同时获取一级评论对应的二级评论,同样为二级评论添加回复按钮,但是不需要添加评论数,因为所有超过二级的评论重置为二级.
