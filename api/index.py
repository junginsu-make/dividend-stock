"""
Vercel Serverless Flask App
Optimized for Vercel's Python Runtime
"""
from flask import Flask, render_template_string, jsonify, request
import os
import sys
import json

# ============================================
# 경로 설정
# ============================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# ============================================
# Flask 앱 생성
# ============================================
app = Flask(__name__)

# ============================================
# 템플릿 로더 함수
# ============================================
def load_template(name):
    """Load HTML template from file"""
    template_path = os.path.join(PROJECT_ROOT, 'templates', name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Template Error</h1><p>{str(e)}</p><p>Path: {template_path}</p>"


# ============================================
# 페이지 라우트
# ============================================

@app.route('/')
def index():
    return render_template_string(load_template('index.html'))

@app.route('/app')
def dashboard():
    return render_template_string(load_template('dashboard.html'))

@app.route('/dividend')
def dividend_page():
    return render_template_string(load_template('dividend.html'))


# ============================================
# 배당 API 라우트
# ============================================

@app.route('/api/dividend/themes')
def get_dividend_themes():
    try:
        from us_market.dividend.engine import DividendEngine
        
        engine = DividendEngine()
        themes = engine.get_themes()
        
        meta = {'last_updated': 'N/A', 'total_tickers': 0}
        universe_path = os.path.join(PROJECT_ROOT, 'us_market/dividend/data/dividend_universe.json')
        if os.path.exists(universe_path):
            with open(universe_path, 'r', encoding='utf-8') as f:
                universe = json.load(f)
                if '_meta' in universe:
                    meta = universe['_meta']
        
        return jsonify({'themes': themes, 'meta': meta})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/dividend/all-tiers', methods=['POST'])
def get_all_tier_portfolios():
    try:
        data = request.json or {}
        theme_id = data.get('theme_id', 'max_monthly_income')
        target_monthly_krw = float(data.get('target_monthly_krw', 1000000))
        fx_rate = float(data.get('fx_rate', 1420))
        tax_rate = float(data.get('tax_rate', 15.4)) / 100.0
        optimize_mode = data.get('optimize_mode', 'greedy')
        
        from us_market.dividend.engine import DividendEngine
        engine = DividendEngine()
        
        results = {}
        for tier in ['defensive', 'balanced', 'aggressive']:
            result = engine.generate_portfolio(
                theme_id=theme_id,
                tier_id=tier,
                target_monthly_krw=target_monthly_krw,
                fx_rate=fx_rate,
                tax_rate=tax_rate,
                optimize_mode=optimize_mode
            )
            results[tier] = result
        return jsonify(results)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/dividend/risk-metrics/<ticker>')
def get_dividend_risk_metrics(ticker):
    try:
        from us_market.dividend.risk_analytics import RiskAnalytics
        period = request.args.get('period', '1y')
        ra = RiskAnalytics()
        metrics = ra.get_all_risk_metrics(ticker, period)
        
        vol = metrics.get('volatility_annual')
        dd = metrics.get('max_drawdown')
        if vol is not None and dd is not None:
            if vol < 0.15 and abs(dd) < 0.20:
                metrics['risk_grade'] = 'A'
            elif vol < 0.25 and abs(dd) < 0.35:
                metrics['risk_grade'] = 'B'
            else:
                metrics['risk_grade'] = 'C'
        else:
            metrics['risk_grade'] = 'N/A'
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/sustainability/<ticker>')
def get_dividend_sustainability(ticker):
    try:
        from us_market.dividend.dividend_analyzer import DividendAnalyzer
        da = DividendAnalyzer()
        metrics = da.get_all_metrics(ticker)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/optimize-advanced', methods=['POST'])
def optimize_dividend_advanced():
    try:
        data = request.json or {}
        theme_id = data.get('theme_id', 'max_monthly_income')
        tier_id = data.get('tier_id', 'balanced')
        target_monthly_krw = float(data.get('target_monthly_krw', 1000000))
        fx_rate = float(data.get('fx_rate', 1420))
        tax_rate = float(data.get('tax_rate', 15.4)) / 100.0
        optimize_mode = data.get('optimize_mode', 'risk_parity')
        
        from us_market.dividend.engine import DividendEngine
        engine = DividendEngine()
        
        result = engine.generate_portfolio(
            theme_id=theme_id,
            tier_id=tier_id,
            target_monthly_krw=target_monthly_krw,
            fx_rate=fx_rate,
            tax_rate=tax_rate,
            optimize_mode=optimize_mode
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/dividend/backtest', methods=['POST'])
def run_dividend_backtest():
    try:
        from us_market.dividend.backtest import BacktestEngine
        
        data = request.json or {}
        portfolio = data.get('portfolio', [])
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date')
        initial_capital = float(data.get('initial_capital', 100000))
        
        if not portfolio:
            return jsonify({'error': 'Portfolio is required'}), 400
        
        portfolio_tuples = [(p['ticker'], p['weight']) for p in portfolio]
        
        engine = BacktestEngine()
        result = engine.run_backtest(
            portfolio=portfolio_tuples,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# ============================================
# 디버그 엔드포인트
# ============================================

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check paths"""
    return jsonify({
        'current_dir': CURRENT_DIR,
        'project_root': PROJECT_ROOT,
        'templates_exist': os.path.exists(os.path.join(PROJECT_ROOT, 'templates')),
        'us_market_exist': os.path.exists(os.path.join(PROJECT_ROOT, 'us_market')),
        'sys_path': sys.path[:5]
    })


# For local development
if __name__ == '__main__':
    app.run(port=5001, debug=True)
