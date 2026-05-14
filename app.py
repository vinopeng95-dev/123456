from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# HTML 模板 - 首頁（美化版）
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>P級電影推薦系統 | 保護級電影查詢</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft JhengHei', 'PingFang TC', 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        /* 動態漸層背景 */
        .gradient-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* 粒子效果 */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100vh) rotate(360deg);
                opacity: 0;
            }
        }

        /* 星星效果 */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }

        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }

        @keyframes twinkle {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }

        /* 玻璃效果卡片 */
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            box-shadow: 0 25px 45px rgba(0,0,0,0.2), 0 0 0 1px rgba(255,255,255,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 35px 55px rgba(0,0,0,0.3);
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            animation: slideDown 0.8s ease;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            font-size: 3.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .subtitle {
            font-size: 1.2em;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 0.9em;
        }

        .search-card {
            padding: 40px;
            margin-bottom: 30px;
            animation: fadeIn 0.8s ease 0.2s both;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: scale(0.95);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        .search-form {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .rating-select {
            padding: 15px 25px;
            font-size: 18px;
            border: 2px solid #e0e0e0;
            border-radius: 50px;
            width: 250px;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
        }

        .rating-select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .search-btn {
            padding: 15px 40px;
            font-size: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }

        .search-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .search-btn:hover::before {
            width: 300px;
            height: 300px;
        }

        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .quick-buttons {
            margin-top: 25px;
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .quick-btn {
            padding: 10px 24px;
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            color: #667eea;
        }

        .quick-btn:hover {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-2px);
        }

        .results-card {
            padding: 30px;
            animation: fadeIn 0.8s ease 0.4s both;
        }

        .results-header {
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }

        .results-header h2 {
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .results-count {
            color: #764ba2;
            font-weight: bold;
            font-size: 1.2em;
        }

        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
        }

        .movie-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            animation: cardFadeIn 0.6s ease both;
        }

        @keyframes cardFadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .movie-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }

        .movie-poster {
            height: 240px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }

        .movie-poster img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s;
        }

        .movie-card:hover .movie-poster img {
            transform: scale(1.05);
        }

        .no-poster {
            color: #999;
            font-size: 14px;
            text-align: center;
        }

        .movie-info {
            padding: 20px;
        }

        .movie-title {
            font-size: 1.25em;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
            line-height: 1.4;
        }

        .movie-rating {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 12px;
        }

        .rating-P { background: #4CAF50; color: white; }
        .rating-G { background: #2196F3; color: white; }
        .rating-PG12 { background: #FF9800; color: white; }
        .rating-PG15 { background: #FF5722; color: white; }
        .rating-R { background: #F44336; color: white; }
        .rating-unknown { background: #9E9E9E; color: white; }

        .movie-date {
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .movie-link {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            margin-top: 10px;
            transition: gap 0.3s;
        }

        .movie-link:hover {
            gap: 10px;
            text-decoration: underline;
        }

        .no-results {
            text-align: center;
            padding: 60px;
            color: #999;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: rgba(255,255,255,0.9);
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            h1 {
                font-size: 2em;
            }
            .header {
                padding: 25px;
            }
            .search-card {
                padding: 25px;
            }
            .movie-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="gradient-bg"></div>
    <div class="particles" id="particles"></div>
    <div class="stars" id="stars"></div>

    <div class="container">
        <div class="header">
            <h1>🎬 P級電影推薦系統</h1>
            <div class="subtitle">
                <span>查詢本週上映的保護級電影</span>
                <span class="badge">適合6歲以上觀賞</span>
            </div>
        </div>

        <div class="search-card glass-card">
            <form method="get" action="/recommend" class="search-form">
                <select name="rating" class="rating-select">
                    <option value="P">🔞 P級 (保護級)</option>
                    <option value="G">👶 G級 (普遍級)</option>
                    <option value="PG12">🧒 PG12 (輔導12級)</option>
                    <option value="PG15">👦 PG15 (輔導15級)</option>
                    <option value="R">🔞 R級 (限制級)</option>
                    <option value="all">📽️ 顯示全部電影</option>
                </select>
                <button type="submit" class="search-btn">🔍 查詢推薦</button>
            </form>
            
            <div class="quick-buttons">
                <button class="quick-btn" onclick="location.href='/recommend?rating=P'">🎯 P級電影</button>
                <button class="quick-btn" onclick="location.href='/recommend?rating=all'">📅 本週全電影</button>
                <button class="quick-btn" onclick="location.href='/debug'">🔧 查看除錯</button>
                <button class="quick-btn" onclick="location.href='/'">🔄 重新整理</button>
            </div>
        </div>

        <div class="results-card glass-card">
            <div class="results-header">
                <h2>📽️ 電影推薦結果</h2>
            </div>
            <div id="results">
                <p style="text-align:center; color:#999;">✨ 請選擇電影分級進行查詢 ✨</p>
            </div>
        </div>

        <div class="footer">
            <p>🎬 資料來源：開眼電影網 | 分級依據：台灣電影分級制度 | 即時更新</p>
        </div>
    </div>

    <script>
        // 產生粒子效果
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                const size = Math.random() * 8 + 2;
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 20 + 's';
                particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
                particlesContainer.appendChild(particle);
            }
        }

        // 產生星星效果
        function createStars() {
            const starsContainer = document.getElementById('stars');
            for (let i = 0; i < 100; i++) {
                const star = document.createElement('div');
                star.classList.add('star');
                const size = Math.random() * 3 + 1;
                star.style.width = size + 'px';
                star.style.height = size + 'px';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.animationDelay = Math.random() * 3 + 's';
                star.style.animationDuration = (Math.random() * 2 + 1) + 's';
                starsContainer.appendChild(star);
            }
        }

        createParticles();
        createStars();
    </script>
</body>
</html>
'''

# HTML 模板 - 查詢結果（美化版）
RECOMMEND_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ rating_name }}電影推薦 | 查詢結果</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft JhengHei', 'PingFang TC', 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .gradient-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            box-shadow: 0 25px 45px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            animation: slideDown 0.8s ease;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }

        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            padding: 12px 28px;
            border-radius: 50px;
            margin-top: 20px;
            transition: all 0.3s;
        }

        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .results-card {
            padding: 30px;
            animation: fadeIn 0.8s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .results-header {
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }

        .results-header h2 {
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .rating-badge {
            display: inline-block;
            background: {{ rating_color }};
            color: white;
            padding: 5px 15px;
            border-radius: 30px;
            font-size: 14px;
        }

        .results-count {
            color: #764ba2;
            font-weight: bold;
            font-size: 1.1em;
        }

        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
        }

        .movie-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            animation: cardFadeIn 0.6s ease both;
        }

        @keyframes cardFadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .movie-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }

        .movie-poster {
            height: 240px;
            background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .movie-poster img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s;
        }

        .movie-card:hover .movie-poster img {
            transform: scale(1.05);
        }

        .no-poster {
            color: #999;
            font-size: 14px;
            text-align: center;
        }

        .movie-info {
            padding: 20px;
        }

        .movie-title {
            font-size: 1.25em;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
        }

        .movie-rating {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 12px;
            background: {{ rating_color }};
            color: white;
        }

        .movie-date {
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .movie-link {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            margin-top: 10px;
            transition: gap 0.3s;
        }

        .movie-link:hover {
            gap: 10px;
            text-decoration: underline;
        }

        .no-results {
            text-align: center;
            padding: 60px;
            color: #999;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: rgba(255,255,255,0.9);
        }

        .search-again {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
        }

        .search-again select, .search-again button {
            padding: 12px 20px;
            margin: 0 5px;
            border-radius: 50px;
            border: 1px solid #ddd;
            font-size: 14px;
        }

        .search-again button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }

        .search-again button:hover {
            transform: translateY(-2px);
        }

        .debug-info {
            background: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            font-size: 13px;
        }

        @media (max-width: 768px) {
            .container { padding: 20px; }
            h1 { font-size: 1.8em; }
            .header { padding: 25px; }
            .movie-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="gradient-bg"></div>
    <div class="particles" id="particles"></div>

    <div class="container">
        <div class="header">
            <h1>🎬 {{ rating_name }}電影推薦</h1>
            <p>{{ description }}</p>
            <a href="/" class="back-btn">← 返回首頁</a>
        </div>

        <div class="results-card glass-card">
            <div class="results-header">
                <h2>
                    📽️ 本週上映電影 
                    <span class="rating-badge">{{ rating_name }}</span>
                </h2>
                <p>✨ 共找到 <span class="results-count">{{ movies|length }}</span> 部符合條件的電影 ✨</p>
                {% if total_count %}
                <p style="font-size: 14px; color: #666;">📊 總共爬取 {{ total_count }} 部本週上映電影</p>
                {% endif %}
            </div>

            {% if movies %}
            <div class="movie-grid">
                {% for movie in movies %}
                <div class="movie-card" style="animation-delay: {{ loop.index * 0.05 }}s">
                    <div class="movie-poster">
                        {% if movie.poster %}
                            <img src="{{ movie.poster }}" alt="{{ movie.title }}" onerror="this.parentElement.innerHTML='<div class=\'no-poster\'>🎬 暫無海報</div>'">
                        {% else %}
                            <div class="no-poster">🎬 暫無海報</div>
                        {% endif %}
                    </div>
                    <div class="movie-info">
                        <div class="movie-title">{{ movie.title }}</div>
                        <div class="movie-rating">{{ movie.rating }}</div>
                        <div class="movie-date">📅 {{ movie.release_date }} 上映</div>
                        <a href="{{ movie.url }}" class="movie-link" target="_blank">🔗 詳細介紹 →</a>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="no-results">
                <p>😢 抱歉，本週沒有找到「{{ rating_name }}」電影</p>
                <p>💡 試試其他分級，或點擊下方按鈕查看全部電影</p>
            </div>
            {% endif %}

            <div class="search-again">
                <form method="get" action="/recommend" style="display: inline;">
                    <select name="rating">
                        <option value="P">P級 (保護級)</option>
                        <option value="G">G級 (普遍級)</option>
                        <option value="PG12">PG12 (輔導12級)</option>
                        <option value="PG15">PG15 (輔導15級)</option>
                        <option value="R">R級 (限制級)</option>
                        <option value="all">顯示全部電影</option>
                    </select>
                    <button type="submit">🔍 查詢其他分級</button>
                </form>
            </div>

            {% if debug_data %}
            <div class="debug-info">
                <strong>📊 分級統計</strong><br>
                {% for rating, count in debug_data.items() %}
                • {{ rating }}: {{ count }} 部<br>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p>🎬 資料來源：開眼電影網 | 更新時間：{{ update_time }}</p>
        </div>
    </div>

    <script>
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                const size = Math.random() * 8 + 2;
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 20 + 's';
                particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
                particlesContainer.appendChild(particle);
            }
        }
        createParticles();
    </script>
</body>
</html>
'''

# 除錯頁面（美化版）
DEBUG_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>除錯資訊 - 電影分級查詢</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft JhengHei', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        h2 { color: #764ba2; margin: 20px 0 15px 0; }
        .back-btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 50px;
            margin-bottom: 20px;
        }
        .stats {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            min-width: 100px;
        }
        .stat-card .count { font-size: 2em; font-weight: bold; color: #667eea; }
        .movie-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .movie-item:hover { transform: translateX(5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .rating-P { border-left: 5px solid #4CAF50; }
        .rating-G { border-left: 5px solid #2196F3; }
        .rating-PG12 { border-left: 5px solid #FF9800; }
        .rating-PG15 { border-left: 5px solid #FF5722; }
        .rating-R { border-left: 5px solid #F44336; }
        .movie-title { font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
        .movie-rating { font-size: 0.9em; color: #666; margin-bottom: 5px; }
        .movie-link { font-size: 0.8em; color: #667eea; word-break: break-all; }
        .movie-poster-img { max-width: 100px; margin-top: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-btn">← 返回首頁</a>
        <h1>🔧 電影分級除錯資訊</h1>
        <p>📊 總共爬取 <strong>{{ movies|length }}</strong> 部電影</p>
        
        <h2>📈 分級統計</h2>
        <div class="stats">
            {% for rating, count in stats.items() %}
            <div class="stat-card">
                <div class="count">{{ count }}</div>
                <div>{{ rating }}</div>
            </div>
            {% endfor %}
        </div>
        
        <h2>🎬 所有電影詳細資訊</h2>
        {% for movie in movies %}
        <div class="movie-item rating-{{ movie.rating_code }}">
            <div class="movie-title">{{ movie.title }}</div>
            <div class="movie-rating">🏷️ 分級: {{ movie.rating }}</div>
            <div class="movie-rating">📅 上映: {{ movie.release_date }}</div>
            <div class="movie-link">🔗 <a href="{{ movie.url }}" target="_blank">{{ movie.url[:80] }}...</a></div>
            {% if movie.poster %}
            <img src="{{ movie.poster }}" class="movie-poster-img" onerror="this.style.display='none'">
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

def get_movies_from_atmovies():
    """從開眼電影網爬取本週上映電影"""
    url = "http://www.atmovies.com.tw/movie/next/"
    Data =
