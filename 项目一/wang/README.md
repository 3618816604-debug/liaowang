# 智能瞭望系统

智能瞭望系统是一个基于Flask的Web应用，用于实现信息搜索、数据管理和分析功能。

## 项目功能

- **用户认证**：支持用户登录和注销功能
- **数据搜索**：
  - 模拟百度搜索
  - 雅安市政府网站实时爬虫搜索
- **数据管理**：
  - 保存搜索结果到数据仓库
  - 查看和管理保存的数据
- **报告生成**：支持生成数据分析报告

## 技术栈

- **后端框架**：Flask
- **数据库**：SQLite
- **ORM**：SQLAlchemy
- **用户认证**：Flask-Login
- **爬虫**：Requests + BeautifulSoup4

## 项目结构

```
.
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化文件
│   ├── models.py           # 数据库模型
│   ├── routes.py           # 路由定义
│   ├── static/             # 静态资源
│   └── templates/          # HTML模板
├── instance/               # 实例配置目录
├── run.py                  # 应用入口文件
├── yaan_search.py          # 雅安搜索爬虫
└── requirements.txt        # 项目依赖
```

## 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/3618816604-debug/liaowang.git
   cd liaowang
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **运行应用**
   ```bash
   python run.py
   ```

6. **访问应用**
   打开浏览器访问：http://127.0.0.1:5000

## 使用说明

### 登录
- 使用默认账号登录：
  - 用户名：admin
  - 密码：password

### 搜索功能
1. 在仪表板页面输入关键词
2. 点击搜索按钮
3. 查看搜索结果（包含百度模拟结果和雅安市政府网站实际结果）

### 数据管理
1. 搜索结果页面可以选择保存感兴趣的数据
2. 在数据仓库页面查看和管理保存的数据
3. 支持根据关键词过滤数据

### 报告生成
- 点击报告生成按钮可以生成数据分析报告

## 爬虫说明

项目包含一个专门用于爬取雅安市政府网站的爬虫模块 `yaan_search.py`，具有以下特点：

- 支持关键词搜索
- 自动处理重定向
- 提取标题、内容、URL和发布日期
- 支持结果保存到文件

## 开发说明

### 添加新功能
1. 在 `app/routes.py` 中添加新的路由
2. 在 `app/templates/` 中创建相应的模板
3. 如果需要数据库操作，在 `app/models.py` 中定义模型

### 数据库迁移
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

## 注意事项

1. 本项目使用SQLite数据库，适合开发和测试环境
2. 生产环境建议使用PostgreSQL或MySQL
3. 爬虫功能仅用于学习和研究，请勿用于商业用途
4. 请遵守相关网站的robots.txt协议

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 作者

3618816604-debug
