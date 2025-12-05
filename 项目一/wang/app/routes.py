from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User, Data
import requests
from datetime import datetime
import sys
import os
# 导入雅安搜索爬虫
from yaan_search import YaanGovSearch

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        keyword = request.form['keyword']
        
        # 1. 获取百度爬虫数据（模拟）
        mock_baidu_data = [
            {
                'title': f'关于{keyword}的搜索结果1',
                'content': f'这是关于{keyword}的详细内容1...',
                'url': f'https://www.baidu.com/s?wd={keyword}1',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果2',
                'content': f'这是关于{keyword}的详细内容2...',
                'url': f'https://www.baidu.com/s?wd={keyword}2',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果3',
                'content': f'这是关于{keyword}的详细内容3...',
                'url': f'https://www.baidu.com/s?wd={keyword}3',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果4',
                'content': f'这是关于{keyword}的详细内容4...',
                'url': f'https://www.baidu.com/s?wd={keyword}4',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果5',
                'content': f'这是关于{keyword}的详细内容5...',
                'url': f'https://www.baidu.com/s?wd={keyword}5',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果6',
                'content': f'这是关于{keyword}的详细内容6...',
                'url': f'https://www.baidu.com/s?wd={keyword}6',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果7',
                'content': f'这是关于{keyword}的详细内容7...',
                'url': f'https://www.baidu.com/s?wd={keyword}7',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果8',
                'content': f'这是关于{keyword}的详细内容8...',
                'url': f'https://www.baidu.com/s?wd={keyword}8',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果9',
                'content': f'这是关于{keyword}的详细内容9...',
                'url': f'https://www.baidu.com/s?wd={keyword}9',
                'source': '百度'
            },
            {
                'title': f'关于{keyword}的搜索结果10',
                'content': f'这是关于{keyword}的详细内容10...',
                'url': f'https://www.baidu.com/s?wd={keyword}10',
                'source': '百度'
            }
        ]
        
        # 2. 获取雅安市政府网站搜索数据
        yaan_data = []
        try:
            searcher = YaanGovSearch()
            yaan_results = searcher.search(keyword)
            # 转换数据格式，使其与百度数据格式一致
            for result in yaan_results:
                yaan_data.append({
                    'title': result['title'],
                    'content': result['content'] if result['content'] else '无摘要',
                    'url': result['url'],
                    'source': result['source'] if result['source'] else '雅安市政府网站',
                    'publish_date': result['publish_date'] if result['publish_date'] else ''
                })
        except Exception as e:
            print(f"雅安搜索爬虫出错: {str(e)}")
        
        # 2.5. 为模拟百度数据添加publish_date字段
        for result in mock_baidu_data:
            result['publish_date'] = ''  # 模拟数据没有发布日期
        
        # 3. 合并百度数据和雅安数据
        all_results = mock_baidu_data + yaan_data
        
        return render_template('dashboard.html', results=all_results, keyword=keyword)
    return render_template('dashboard.html')

@app.route('/save_data', methods=['POST'])
@login_required
def save_data():
    if request.method == 'POST':
        keyword = request.form['keyword']
        titles = request.form.getlist('titles[]')
        contents = request.form.getlist('contents[]')
        urls = request.form.getlist('urls[]')
        sources = request.form.getlist('sources[]')
        publish_dates = request.form.getlist('publish_dates[]')
        
        for title, content, url, source, publish_date in zip(titles, contents, urls, sources, publish_dates):
            data = Data(
                keyword=keyword,
                title=title,
                content=content,
                url=url,
                source=source,
                publish_date=publish_date
            )
            db.session.add(data)
        db.session.commit()
        flash('数据保存成功')
        return redirect(url_for('dashboard'))

@app.route('/delete_data/<int:data_id>', methods=['POST'])
@login_required
def delete_data(data_id):
    """删除单条数据"""
    try:
        data = Data.query.get(data_id)
        if data:
            db.session.delete(data)
            db.session.commit()
            flash('数据删除成功')
    except Exception as e:
        db.session.rollback()
        flash(f'数据删除失败: {str(e)}')
    return redirect(url_for('data_warehouse'))

@app.route('/data_warehouse', methods=['GET', 'POST'])
@login_required
def data_warehouse():
    query = Data.query
    
    # 处理批量删除
    if request.method == 'POST' and 'delete_selected' in request.form:
        selected_ids = request.form.getlist('selected_ids')
        if selected_ids:
            try:
                # 转换为整数列表
                selected_ids = [int(id) for id in selected_ids]
                # 删除选中的数据
                Data.query.filter(Data.id.in_(selected_ids)).delete(synchronize_session=False)
                db.session.commit()
                flash('批量删除成功')
            except Exception as e:
                db.session.rollback()
                flash(f'批量删除失败: {str(e)}')
            return redirect(url_for('data_warehouse'))
    
    # 按关键词搜索
    if request.method == 'POST' and 'search_keyword' in request.form:
        search_keyword = request.form.get('search_keyword')
        if search_keyword:
            query = query.filter(Data.keyword.like(f'%{search_keyword}%') | Data.title.like(f'%{search_keyword}%'))
    
    # 按日期分组
    data_list = query.order_by(Data.create_time.desc()).all()
    
    # 按日期分组
    grouped_data = {}
    for data in data_list:
        date_key = data.create_time.strftime('%Y-%m-%d')
        if date_key not in grouped_data:
            grouped_data[date_key] = []
        grouped_data[date_key].append(data)
    
    return render_template('data_warehouse.html', grouped_data=grouped_data)

@app.route('/generate_report')
@login_required
def generate_report():
    # 这里将实现AI报告生成功能，暂时返回模拟数据
    return render_template('report.html', report_content='这是AI生成的报告内容...')

# 初始化数据库函数
def init_db():
    db.create_all()
    # 创建默认管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password='admin888')
        db.session.add(admin)
        db.session.commit()