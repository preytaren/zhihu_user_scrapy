# zhihu_user_scrapy
基于Scrapy的知乎用户数据爬虫，对用户基础数据和用户头像进行了爬取。

# 获取源代码
```
git clone https://github.com/preytaren/zhihu_user_scrapy.git
```
# requirements
需要提前安装 Redis，并在默认端口运行 Redis
```
apt-get install redis
redis-server
```
然后安装 Python 包依赖
```
cd zhihu_user_scrapy/
pip install -r requirements.txt
```
运行 Celery
```
cd zhihu_user_scrapy/
celery -A tasks worker --loglevel=info
```

运行爬虫
```
scrapy crawl zhihu   
```

# todo
- 进行性能优化提升爬虫性能
- 通过 scrapy-redis 完成分布式爬虫
- 使用 docker 作为基础平台
