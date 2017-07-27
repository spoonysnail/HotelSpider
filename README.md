# HotelSpider
爬取去哪儿酒店数据

Command Lines:
1. python ProxySpider.py
   # 通过ProxySpider获取有效代理ip，并存入本地文档
2. python MainPost.py cityname output_filename dataperpage startpage
   # 爬取某城市所有酒店数据
      --cityname:城市名
      --output_filename:输出文件
      --dataperpage:每次请求返回的酒店个数
      --startpage：请求起始页
   e.g. python MainPost.py 上海 shangehai.csv 100 1
