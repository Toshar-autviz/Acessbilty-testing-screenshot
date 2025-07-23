import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from urllib.parse import urljoin, urlparse
import os
from collections import Counter
import json

class WebsiteAnalyzer:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Make sure ChromeDriver is installed and in your PATH")
    
    def take_screenshot(self, url):
        """Take screenshot of the webpage"""
        if not self.driver:
            return None
            
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            # Convert to base64 for web display
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            return screenshot_b64
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def extract_components(self, url):
        """Extract and analyze HTML components"""
        try:
            # Get page source
            if self.driver:
                self.driver.get(url)
                time.sleep(2)
                html_content = self.driver.page_source
            else:
                response = requests.get(url, timeout=10)
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Count different types of components
            components = {}
            
            # Basic HTML elements
            basic_elements = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                            'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']
            
            for element in basic_elements:
                count = len(soup.find_all(element))
                if count > 0:
                    components[element] = count
            
            # Form elements
            form_elements = ['form', 'input', 'textarea', 'select', 'button']
            for element in form_elements:
                count = len(soup.find_all(element))
                if count > 0:
                    components[element] = count
            
            # Media elements
            media_elements = ['video', 'audio', 'iframe', 'canvas', 'svg']
            for element in media_elements:
                count = len(soup.find_all(element))
                if count > 0:
                    components[element] = count
            
            # Semantic HTML5 elements
            semantic_elements = ['header', 'nav', 'main', 'section', 'article', 
                               'aside', 'footer', 'figure', 'figcaption']
            for element in semantic_elements:
                count = len(soup.find_all(element))
                if count > 0:
                    components[element] = count
            
            # Special components detection
            components.update(self._detect_special_components(soup))
            
            return components
            
        except Exception as e:
            print(f"Error extracting components: {e}")
            return {}
    
    def _detect_special_components(self, soup):
        """Detect special components like modals, dropdowns, etc."""
        special_components = {}
        
        # Common class/id patterns for special components
        patterns = {
            'modals': ['modal', 'popup', 'dialog', 'overlay'],
            'dropdowns': ['dropdown', 'select', 'menu'],
            'carousels': ['carousel', 'slider', 'swiper'],
            'tabs': ['tab', 'accordion'],
            'cards': ['card', 'tile'],
            'notifications': ['alert', 'notification', 'toast'],
            'loaders': ['loader', 'spinner', 'loading'],
            'tooltips': ['tooltip', 'popover']
        }
        
        for component_type, keywords in patterns.items():
            count = 0
            for keyword in keywords:
                # Check for class names containing keywords
                elements_by_class = soup.find_all(class_=lambda x: x and keyword in ' '.join(x).lower())
                elements_by_id = soup.find_all(id=lambda x: x and keyword in x.lower())
                count += len(elements_by_class) + len(elements_by_id)
            
            if count > 0:
                special_components[component_type] = count
        
        return special_components
    
    def calculate_complexity(self, components):
        """Calculate page complexity based on component count"""
        # Weight different components based on complexity
        complexity_weights = {
            # Basic elements (low weight)
            'div': 1, 'span': 1, 'p': 1, 'a': 1, 'li': 1,
            
            # Headers and structure (medium weight)
            'h1': 2, 'h2': 2, 'h3': 2, 'h4': 2, 'h5': 2, 'h6': 2,
            'header': 3, 'nav': 3, 'main': 3, 'section': 2, 'footer': 3,
            
            # Interactive elements (high weight)
            'form': 5, 'input': 3, 'button': 3, 'select': 4, 'textarea': 4,
            
            # Media and complex elements (high weight)
            'img': 2, 'video': 6, 'audio': 5, 'iframe': 6, 'canvas': 7, 'svg': 4,
            
            # Tables (medium weight)
            'table': 4, 'tr': 1, 'td': 1, 'th': 2,
            
            # Special components (very high weight)
            'modals': 8, 'carousels': 10, 'dropdowns': 6, 'tabs': 7,
            'cards': 3, 'notifications': 5, 'loaders': 4, 'tooltips': 3
        }
        
        total_complexity = 0
        total_elements = 0
        
        for component, count in components.items():
            weight = complexity_weights.get(component, 2)  # Default weight
            total_complexity += count * weight
            total_elements += count
        
        return {
            'total_elements': total_elements,
            'complexity_score': total_complexity,
            'complexity_level': self._get_complexity_level(total_complexity)
        }
    
    def _get_complexity_level(self, score):
        """Categorize complexity level"""
        if score < 50:
            return "Simple"
        elif score < 150:
            return "Moderate"
        elif score < 300:
            return "Complex"
        else:
            return "Very Complex"
    
    def analyze_website(self, url):
        """Main method to analyze a website"""
        print(f"Analyzing website: {url}")
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = {
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'screenshot': None,
            'components': {},
            'complexity': {},
            'errors': []
        }
        
        try:
            # Take screenshot
            print("Taking screenshot...")
            result['screenshot'] = self.take_screenshot(url)
            
            # Extract components
            print("Extracting components...")
            result['components'] = self.extract_components(url)
            
            # Calculate complexity
            print("Calculating complexity...")
            result['complexity'] = self.calculate_complexity(result['components'])
            
            print("Analysis complete!")
            
        except Exception as e:
            error_msg = f"Error analyzing website: {e}"
            print(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def close(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

# Flask web application
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    analyzer = WebsiteAnalyzer()
    try:
        result = analyzer.analyze_website(url)
        return jsonify(result)
    finally:
        analyzer.close()

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Component Analyzer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="url"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
        }
        .screenshot {
            text-align: center;
            margin-bottom: 20px;
        }
        .screenshot img {
            max-width: 100%;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .components, .complexity {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .components h3, .complexity h3 {
            margin-top: 0;
            color: #333;
        }
        .component-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .component-item {
            background: white;
            padding: 10px;
            border-radius: 3px;
            border-left: 3px solid #007bff;
        }
        .complexity-score {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .loading {
            text-align: center;
            color: #666;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Website Component Analyzer</h1>
        
        <div class="input-group">
            <label for="url">Website URL:</label>
            <input type="url" id="url" placeholder="https://example.com" required>
            <button onclick="analyzeWebsite()" id="analyzeBtn">Analyze Website</button>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <div class="screenshot" id="screenshot"></div>
            
            <div class="complexity" id="complexity"></div>
            
            <div class="components" id="components">
                <h3>Page Components</h3>
                <div class="component-list" id="componentList"></div>
            </div>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <p>🔄 Analyzing website... This may take a few moments.</p>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        async function analyzeWebsite() {
            const url = document.getElementById('url').value.trim();
            const analyzeBtn = document.getElementById('analyzeBtn');
            const results = document.getElementById('results');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Show loading, hide results and errors
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    throw new Error(data.error || 'Analysis failed');
                }
                
            } catch (err) {
                error.textContent = err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Website';
            }
        }
        
        function displayResults(data) {
            const results = document.getElementById('results');
            const screenshot = document.getElementById('screenshot');
            const complexity = document.getElementById('complexity');
            const componentList = document.getElementById('componentList');
            
            // Display screenshot
            if (data.screenshot) {
                screenshot.innerHTML = `
                    <h3>Website Screenshot</h3>
                    <img src="data:image/png;base64,${data.screenshot}" alt="Website Screenshot">
                `;
            }
            
            // Display complexity
            complexity.innerHTML = `
                <h3>Page Complexity Analysis</h3>
                <div class="complexity-score">
                    Score: ${data.complexity.complexity_score} (${data.complexity.complexity_level})
                </div>
                <p>Total Elements: ${data.complexity.total_elements}</p>
            `;
            
            // Display components
            componentList.innerHTML = '';
            Object.entries(data.components).forEach(([component, count]) => {
                const item = document.createElement('div');
                item.className = 'component-item';
                item.innerHTML = `
                    <strong>${component}</strong><br>
                    Count: ${count}
                `;
                componentList.appendChild(item);
            });
            
            results.style.display = 'block';
        }
        
        // Allow Enter key to trigger analysis
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeWebsite();
            }
        });
    </script>
</body>
</html>'''
    
    # Write the HTML template file
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Website Component Analyzer")
    print("=" * 30)
    print("Starting Flask application...")
    print("Open http://localhost:5000 in your browser")
    print("\nMake sure you have the following dependencies installed:")
    print("pip install flask selenium beautifulsoup4 requests")
    print("\nAlso install ChromeDriver for screenshots")
    
    app.run(debug=True, port=5000)