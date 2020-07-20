## 增加ISSUE上传图片功能

**1. 新建Image模型**

第一步：
打开issuesystem下的models.py,添加图片类
使用外键将图片和ISSUE关联
```python
# upload_to指定文件上传路径
class Image(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="issue")
    image = models.ImageField(upload_to="%Y-%m-%d")  # upload_to内置了strftime函数
```
第二步：进行数据库迁移
```shell
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

**2. 修改新建ISSUE的模板，增加图片上传**

进入templates下的issuesystem文件夹，打开newissue.html
```html
<div class="form-group">
<label>图片:</label>
<input type="file" name='image' accept="image/*" class="form-control">
</div>
```

**3. 修改视图文件**

打开issuesystem下的views.py
```python
content = request.POST.get("content").strip()
image = request.FILES.get("image", None)  # 增加此行
# 并做如下修改
if title and description:
    # models.Issue.objects.create(title=title,
    #                             publisher=publisher,
    #                             description=description,
    #                             content=content)
    issue = models.Issue(title=title,
                         publisher=publisher,
                         description=description,
                         content=content)
    issue.save()
    if image:
        models.Image.objects.create(issue=issue, image=image)
    return redirect('/issuesystem/myissue/')
```
到这里已经实现了图片上传，上传图片时系统会将图片保存到项目配置目录下，并将路径存到数据库中，实际上数据库表中存储的是文件路径，并非文件本身，可以直接访问数据库查看内容．

**4. 修改图片保存路径**

修改settings.py
添加MEDIA路径
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(STATICFILES_DIRS[0], 'media')
```
再次上传文件发现根目录的static目录下多了一个media文件夹，在media文件夹下是我们上传的图片．同样，数据库表里保存的路径依然是media下的相对路径．在这里我将MEDIA_ROOT路径设置在static路径之下，是因为我搭建的是局域网项目，必须访问static路径下的资源！

**5. 查看图片**

第一步：修改views.py
在views.py中获取图片资源
打开issuesystem下的views.py，找到showissue视图函数
```python
def showissue(request, issueid):
    # issue = models.Issue.objects.get(id=issueid)
    issue = get_object_or_404(models.Issue, id=issueid)
    images = issue.issue.all()  # 增加此行
    publishtime = issue.publishtime
    return render(request, apptemplates('showissue.html'), 
                  {"issue":issue, "publishtime":publishtime, "images":images})
```
通过images = issue.issue.all()，直接利用issue对象反查关联图片，并在render时将images传送到前台．

第二步：打开showissue.html
增加图片显示
```shell
{% for image in images %}
<img class="thumbnail" src="/static/media/{{image.image}}">
{% endfor %}
```
图片设置的是缩略图样式，在issuesystem.css中设置thumbnail的样式．
查看issue时已经能够看到图片了

**6. 使用MEDIA_URL查看图片**

MEDIA_URL的设置是为了在模板html中使用{{MEDIA_URL}}，这样我们在修改图片存储的media根目录路径时，只需要修改MEDIA_ROOT的值即可，不需要担心MEDIA_ROOT修改后还要修改所有的模板文件．
第一步：修改配置文件settings.py
在settings.py的TEMPLATES中加入media
```python
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # 添加

```
第二步：django后台没有实现MEDIA_URL的自动跳转，我们设置的MEDIA_URL='/media/'，所以必须设置一个跳转让Django可以识别到此路由．
打开项目配置目录aisystem下的urls.py，找到urlpatterns,添加
```python
    url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
```
这样在html中使用MEDIA_URL时可以正确访问到图片
第三步：修改模板文件
打开showissue.html
增加图片显示
```shell
{% for image in images %}
<img class="thumbnail" src="{{MEDIA_URL}}{{image.image}}">
{% endfor %}
```

**7. 资源配置检测**

当settings.py中的MEDIA_ROOT路径更改时，系统会后续的资源放到新的路径下，但对于以前的资源却并不能做出调整，所以，我们需要在setting.py中执行移动操作！
```python
import shutil
...
MEDIA_ROOT_OLD = os.path.join(STATICFILES_DIRS[0], 'issuesystem/media')
MEDIA_ROOT = os.path.join(STATICFILES_DIRS[0], 'media')

if MEDIA_ROOT_OLD and os.path.exists(MEDIA_ROOT_OLD):
    shutil.move(MEDIA_ROOT_OLD, MEDIA_ROOT)
```

**8. 过期资源删除**

当我们删除图片数据库表资源时，media文件夹下存在的图片资源并不会清除，所以我们同样可以在初始化时完成清除操作．
打开issuesystem下的views.py，添加以下代码
```python
from django.conf import settings
media_path = settings.MEDIA_ROOT
def iter_files(rootdir):
    images = []
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            file_name = os.path.join(root, file)
            images.append(file_name)
    return images
images = iter_files(media_path)
dbimages = models.Image.objects.all()
for dbimage in dbimages:
    images.remove(os.path.join(media_path,str(dbimage.image)))
if len(images):
    for image in images:
        os.remove(image)
```
每次重启服务时都会进行数据库资源和media资源校验

**9. 实时删除图片资源**

当我们删除图片数据库表资源时，同时删除对应的系统资源
打开issuesystem下的views.py，找到deleteissue函数，
```python
# 原代码
    models.Issue.objects.filter(id=issueid).delete()
# 修改为
    # models.Issue.objects.filter(id=issueid).delete()
    delete_issue =  models.Issue.objects.get(id=issueid)
    delete_images = delete_issue.issue.all()
    for delete_image in delete_images:
        os.remove(os.path.join(media_path,str(delete_image.image)))
    delete_issue.delete()
```

**10. 上传多张图片**

第一步：修改模板文件newissue.html,支持多文件上传
找到图片输入的控件，增加multiple属性．修改字段
```html
<input type="file" name='upload-images' multiple="multiple" accept="image/*" class="form-control">
```
这是在前端，已经可以一次上传多个图片．
第二步: 修改视图函数
打开issuesystem下的views.py，找到newissue函数
```python
# 修改前：
        image = request.FILES.get("image", None)
        ...
             if image:
                 models.Image.objects.create(issue=issue, image=image)
# 修改后：
        images = request.FILES.getlist("upload-images", None)
        ...
             if len(images):
                 for image in images:
                     models.Image.objects.create(issue=issue, image=image)

```

**11. 上传前预览**

第一步：修改模板文件newissue.html
找到图片输入的控件，增加onchange属性，add-image类名，以及图片显示框
```html
<input type="file" name='image' multiple="multiple" accept="image/*" class="form-control add-image" onchange="addImage()">
<div id="list-image"></div>
```
第二步: 添加js操作预览图片
```javascript
function addImage() {
  var files = $('.add-image').prop("files");
  var listimage = document.getElementById("list-image");
  function readAndPreview(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function () {
      var image = document.createElement("img");
      image.height = 100;
      image.title = file.name;
      image.src = this.result;
      listimage.appendChild(image);
    }, false);
    reader.readAsDataURL(file);
  }
  if (files) {
    [].forEach.call(files, readAndPreview);
  }
};
```
到这里已经可以预览每次上传的图片．

**12. 上传前添加图片**

第11点我们上传图片前可以预览，但是如果我们重新选取照片时，前端预览界面虽然显示了所有选中的照片，但实际上传的图片只有最后一次选中的图片．这种数据不对应自然不是我们希望看到的．
第一步：修改11点中的js代码
```javascript
var uploadimages = [];  # 增加
function addImage() {
  var files = $('.add-image').prop("files");
  var listimage = document.getElementById("list-image");
  function readAndPreview(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function () {
      var image = document.createElement("img");
      image.height = 100;
      image.title = file.name;
      image.src = this.result;
      listimage.appendChild(image);
    }, false);
    reader.readAsDataURL(file);
    uploadimages.push(file);  # 增加
  }
  if (files) {
    [].forEach.call(files, readAndPreview);
  }
};
```
我们使用一个uploadimages变量存储我们选中的所有图片

那如何将数据传回后台呢
由于Form表单的Filelist只读，我们无法将我们获取的图片对象回传表单，所以我们要换一种处理方式．

第二步：修改模板文件newissue.html
找到表单输入的控件，添加id，使用button替代submit控件
```html
<form id="newissue" action="/issuesystem/newissue/" method="post" enctype="multipart/form-data">
          ...
          <input type="button" name="提交" value="发布" onclick="uploadImages()">
        </form>
```

第三步：编写uploadImages()
```javascript
function uploadImages() {
  var formData = new FormData($('#newissue')[0]);
  uploadimages.map(element => {
    formData.append("upload-images", element);
  });
  $.ajax({
      type:'POST',
      url:"http://10.205.56.193:8000/issuesystem/newissue/",
      data: formData,
      processData:false,
      contentType:false,
      success:function(){
        window.location.href = "http://10.205.56.193:8000/issuesystem/myissue/";
      },
      error:function(){alert('Fail 404');}
      });
```
在这里我们使用了formData．
解析
var formData = new FormData($('#newissue')[0]);
获取表单内容，初始化为FormData

uploadimages.map(element => {
formData.append("upload-images", element);
});
将图片列表中的每个对象放入upload-images字段

最后使用ajax传至后台

success:function(){
window.location.href = "http://10.205.56.193:8000/issuesystem/myissue/";
},

Ajax是局部刷新，提交请求后并不能像表单提交一样跳转，所以在传输成功后我们使用window.location.href强制跳转

**12. 上传前删除图片**

如果我们要删除图片，就需要为每张图片添加删除控件
修改添加图片的js代码
```javascript
// 第一步：给每张图片增加控件
var uploadimages = [];
function addImage() {
  var files = $('.add-image').prop("files");
  var listimage = document.getElementById("list-image");
　　// 增加imgdivhtml，使用imgdiv替代img，添加控件i
  var imgdivhtml = "\
      <img src=\"{0}\" style=\"height: 100px\">\
      <i class=\"zmdi zmdi-delete img-delete-button\"></i>"
  function readAndPreview(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function () {
      var imgdiv = document.createElement("div");
      imgdiv.className = "imgDiv";
      imgdiv.innerHTML = imgdivhtml.format(this.result);
      listimage.appendChild(imgdiv);
    }, false);
    reader.readAsDataURL(file);
    uploadimages.push(file);
  }
  if (files) {
    [].forEach.call(files, readAndPreview);
  }
};

// 第二步：删除功能
$('#list-image').click(function(e) {
  if (e.target.className == "zmdi zmdi-delete img-delete-button") {
    var listimage = document.getElementById("list-image");
    var index = $('#list-image .imgDiv').index(e.target.parentElement);
    uploadimages.splice(index, 1);  // index为图片索引，删除从index开始的一个对象
    listimage.removeChild(e.target.parentElement);
  }
});
```

**13. 点击图片查看大图**

第一步: 修改showissue.html
```html
<!-- 修改前 直接显示图片-->
<img class="thumbnail" src="{{MEDIA_URL}}{{image.image}}">
<!-- 修改后 改变图片大小，显示缩略图-->
<a href="/issuesystem/showimage/{{ image.id }}" target="_blank">
<img src="{{MEDIA_URL}}{{image.image}}" style="height: 100px">
</a>
```
target="_blank"可使网页跳转时新建网页

第二步：打开issuesystem下的urls.py,添加路由
```python
path('showimage/<int:imageid>/', views.showimage),
```

第三步：打开issuesystem下的views.py,添加视图
```python
@login_required
def showimage(request, imageid):
    image = get_object_or_404(models.Image, id=imageid)
    return render(request, apptemplates('showimage.html'), {"image":image})
```

第四步：进入templates下的issuesystem目录,添加模板showimage.html
```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8"/>
  <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>
  <meta name="description" content="FOXCONN AI"/>
  <meta name="author" content="Tank"/>
  <title>IMAGE</title>
  <!-- loader-->
  {% load staticfiles %}
  <!--favicon-->
  <link rel="icon" href="{% static 'assets/images/favicon.ico' %}" type="image/x-icon">
  <!-- Custom Style-->
  <link href="{% static 'assets/css/app-style.css' %}" rel="stylesheet"/>
</head>
<body class="bg-theme bg-theme2">
    <div style="text-align: center;">
    <img src="{{MEDIA_URL}}{{image.image}}" style="width: 720px">
    <div>
</body>
</html>
```
