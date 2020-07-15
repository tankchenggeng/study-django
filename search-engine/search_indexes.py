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
