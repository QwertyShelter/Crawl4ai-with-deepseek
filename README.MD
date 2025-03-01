# 基于 crawl4ai 和 playwright 的动态页面爬取分析
运行 cookie.py，接下来手动登录网站，之后程序便可以返回网页的 cookies，以便后续搜索

将得到的 cookies 复制到 config.py 中，再运行 main.py，即可自动检索出相关页面的 url，再交给 LLM 进行处理 