# 微信公众号文章爬虫
<img width="300" alt="截屏2024-12-21 14 45 49" src="https://github.com/user-attachments/assets/3506502c-e162-42a0-933a-0b27f3844cc6" />

一个用于获取微信公众号文章信息的爬虫工具。可以搜索公众号、获取文章列表并导出为 CSV 文件，方便后续数据分析和管理。

## 功能特点

- 登录微信公众平台（使用扫码登录）
- 搜索并筛选公众号
- 获取公众号文章列表
- 支持分页加载更多文章
- 导出文章信息到 CSV 文件

## 文件结构

```
wechat_spider/
├── wechat_spider.py   # 主程序
├── login.py           # 登录模块
└── agent.py           # User-Agent 管理模块
```

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python wechat_spider.py
```

3. 操作流程：
   - 首次运行需要扫码登录微信公众平台
   - 输入要搜索的公众号名称
   - 从搜索结果中选择目标公众号
   - 查看文章列表，可以：
     - 加载更多文章
     - 导出文章信息到 CSV 文件

## CSV 导出字段说明

导出的 CSV 文件包含以下字段：
- 标题：文章标题
- 作者：文章作者
- 摘要：文章摘要内容
- 链接：文章访问链接
- 发布时间：文章发布的具体时间
- 封面图：文章封面图片链接

## 注意事项

1. 登录相关：
   - 首次使用需要扫码登录
   - 登录信息会保存在 `gzhcookies.cookie` 文件中
   - 如果登录失效需要重新扫码

2. 数据导出：
   - CSV 文件默认保存在 `exports` 目录下
   - 文件名格式：`公众号名称_时间戳.csv`
   - 使用 UTF-8 编码，支持中文内容

3. 使用限制：
   - 需要遵守微信公众平台的使用规范
   - 建议合理控制爬取频率
   - 仅用于学习研究，请勿用于商业用途

## 环境要求

- Python 3.6+
- 依赖库：
  - requests
  - pillow (用于显示登录二维码)
  - urllib3

## License

MIT License

有想学习 AI公众号文章 写作的朋友可以加入小报童

<img width="300" alt="小报童" src="https://github.com/user-attachments/assets/4cfc78d7-e99d-447e-9cc6-24ac09315236" />



