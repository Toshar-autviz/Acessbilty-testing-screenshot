import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from urllib.parse import urljoin, urlparse, parse_qs
import os
from collections import Counter
import json
import xml.etree.ElementTree as ET
from urllib.robotparser import RobotFileParser
import re

class WebsiteAnalyzer:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.discovered_pages = []
        self.base_domain = None
    
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
    
    def discover_pages(self, base_url, max_pages=50):
        """Discover all available pages on the website"""
        print(f"Discovering pages for: {base_url}")
        
        # Ensure URL has protocol
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        self.base_domain = urlparse(base_url).netloc
        discovered_urls = set()
        
        # Method 1: Check sitemap.xml
        sitemap_urls = self._get_sitemap_urls(base_url)
        discovered_urls.update(sitemap_urls)
        
        # Method 2: Crawl main page for internal links
        internal_links = self._crawl_internal_links(base_url, max_depth=2)
        discovered_urls.update(internal_links)
        
        # Method 3: Common page patterns
        common_pages = self._check_common_pages(base_url)
        discovered_urls.update(common_pages)
        
        # Limit results and clean URLs
        discovered_urls = list(discovered_urls)[:max_pages]
        
        # Get page info for each discovered URL
        self.discovered_pages = []
        for url in discovered_urls:
            try:
                page_info = self._get_page_info(url)
                self.discovered_pages.append(page_info)
            except Exception as e:
                print(f"Error getting info for {url}: {e}")
        
        print(f"Discovered {len(self.discovered_pages)} pages")
        return self.discovered_pages
    
    def _get_sitemap_urls(self, base_url):
        """Extract URLs from sitemap.xml"""
        urls = set()
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/robots.txt')  # Check robots.txt for sitemap location
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    if 'sitemap' in sitemap_url.lower():
                        urls.update(self._parse_sitemap(response.text))
                    elif 'robots.txt' in sitemap_url:
                        sitemap_from_robots = self._get_sitemap_from_robots(response.text)
                        for sm_url in sitemap_from_robots:
                            sm_response = requests.get(sm_url, timeout=10)
                            if sm_response.status_code == 200:
                                urls.update(self._parse_sitemap(sm_response.text))
            except Exception as e:
                print(f"Error fetching sitemap from {sitemap_url}: {e}")
        
        return urls
    
    def _parse_sitemap(self, sitemap_content):
        """Parse sitemap XML and extract URLs"""
        urls = set()
        try:
            root = ET.fromstring(sitemap_content)
            
            # Handle sitemap index
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    # Fetch individual sitemap
                    try:
                        response = requests.get(loc.text, timeout=10)
                        if response.status_code == 200:
                            urls.update(self._parse_sitemap(response.text))
                    except:
                        pass
            
            # Handle individual URLs
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None and self._is_same_domain(loc.text):
                    urls.add(loc.text)
                    
        except ET.ParseError:
            # If not valid XML, try to extract URLs with regex
            url_pattern = re.compile(r'https?://[^\s<>"]+')
            found_urls = url_pattern.findall(sitemap_content)
            for url in found_urls:
                if self._is_same_domain(url):
                    urls.add(url)
        
        return urls
    
    def _get_sitemap_from_robots(self, robots_content):
        """Extract sitemap URLs from robots.txt"""
        sitemaps = []
        for line in robots_content.split('\n'):
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                sitemaps.append(sitemap_url)
        return sitemaps
    
    def _crawl_internal_links(self, base_url, max_depth=2):
        """Crawl website for internal links"""
        urls = set()
        visited = set()
        to_visit = [(base_url, 0)]
        
        while to_visit and len(urls) < 30:  # Limit crawling
            current_url, depth = to_visit.pop(0)
            
            if current_url in visited or depth > max_depth:
                continue
                
            visited.add(current_url)
            
            try:
                if self.driver:
                    self.driver.get(current_url)
                    time.sleep(1)
                    html_content = self.driver.page_source
                else:
                    response = requests.get(current_url, timeout=10)
                    html_content = response.text
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    if self._is_valid_page_url(full_url):
                        urls.add(full_url)
                        if depth < max_depth:
                            to_visit.append((full_url, depth + 1))
                            
            except Exception as e:
                print(f"Error crawling {current_url}: {e}")
        
        return urls
    
    def _check_common_pages(self, base_url):
        """Check for common page patterns"""
        common_paths = [
            '', '/', '/home', '/about', '/about-us', '/contact', '/contact-us',
            '/services', '/products', '/blog', '/news', '/faq', '/help',
            '/privacy', '/terms', '/careers', '/team', '/portfolio',
            '/gallery', '/testimonials', '/pricing', '/login', '/register'
        ]
        
        urls = set()
        for path in common_paths:
            test_url = urljoin(base_url, path)
            try:
                response = requests.head(test_url, timeout=5)
                if response.status_code == 200:
                    urls.add(test_url)
            except:
                pass
        
        return urls
    
    def _is_same_domain(self, url):
        """Check if URL belongs to the same domain"""
        if not self.base_domain:
            return True
        return urlparse(url).netloc == self.base_domain
    
    def _is_valid_page_url(self, url):
        """Check if URL is a valid page to analyze"""
        parsed = urlparse(url)
        
        # Must be same domain
        if not self._is_same_domain(url):
            return False
        
        # Skip certain file types
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip']
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip fragments and certain query parameters
        if parsed.fragment:
            return False
        
        return True
    
    def _get_page_info(self, url):
        """Get basic information about a page"""
        try:
            if self.driver:
                self.driver.get(url)
                time.sleep(1)
                title = self.driver.title
                html_content = self.driver.page_source
            else:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else 'Untitled'
                html_content = response.text
            
            # Get page description
            soup = BeautifulSoup(html_content, 'html.parser')
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Count basic elements for preview
            element_count = len(soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'img', 'a']))
            
            return {
                'url': url,
                'title': title.strip() if title else 'Untitled',
                'description': description[:150] + '...' if len(description) > 150 else description,
                'element_count': element_count,
                'path': urlparse(url).path or '/'
            }
        except Exception as e:
            return {
                'url': url,
                'title': 'Error loading page',
                'description': str(e),
                'element_count': 0,
                'path': urlparse(url).path or '/'
            }
    
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

@app.route('/discover', methods=['POST'])
def discover():
    url = request.json.get('url', '').strip()
    max_pages = request.json.get('max_pages', 20)
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    analyzer = WebsiteAnalyzer()
    try:
        pages = analyzer.discover_pages(url, max_pages)
        return jsonify({'pages': pages})
    finally:
        analyzer.close()

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
    
    # Create the enhanced HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Component Analyzer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
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
        input[type="url"], input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="number"] {
            width: 200px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px 10px 5px 0;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        button.secondary {
            background-color: #6c757d;
        }
        button.secondary:hover {
            background-color: #5a6268;
        }
        .pages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .page-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .page-card:hover {
            border-color: #007bff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .page-card.selected {
            border-color: #007bff;
            background: #e7f3ff;
        }
        .page-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .page-url {
            color: #007bff;
            font-size: 14px;
            margin-bottom: 8px;
            word-break: break-all;
        }
        .page-description {
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .page-stats {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #888;
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
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        .analyze-selected {
            background-color: #28a745;
            margin-top: 20px;
        }
        .analyze-selected:hover {
            background-color: #218838;
        }
        .page-count {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Enhanced Website Component Analyzer</h1>
        
        <div class="section">
            <div class="input-group">
                <label for="url">Website URL:</label>
                <input type="url" id="url" placeholder="https://example.com" required>
            </div>
            <div class="input-group">
                <label for="maxPages">Maximum pages to discover:</label>
                <input type="number" id="maxPages" value="20" min="5" max="100">
            </div>
            <button onclick="discoverPages()" id="discoverBtn">🔍 Discover Pages</button>
        </div>
        
        <div id="pagesSection" class="section" style="display: none;">
            <div class="section-title">
                Available Pages
                <span id="pageCount" class="page-count"></span>
            </div>
            <div id="pagesGrid" class="pages-grid"></div>
            <button onclick="analyzeSelected()" id="analyzeSelectedBtn" class="analyze-selected" style="display: none;">
                📊 Analyze Selected Page
            </button>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <div class="section-title">Analysis Results</div>
            <div class="screenshot" id="screenshot"></div>
            
            <div class="complexity" id="complexity"></div>
            
            <div class="components" id="components">
                <h3>Page Components</h3>
                <div class="component-list" id="componentList"></div>
            </div>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <p>🔄 Processing... This may take a few moments.</p>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        let discoveredPages = [];
        let selectedPageUrl = null;
        
        async function discoverPages() {
            const url = document.getElementById('url').value.trim();
            const maxPages = parseInt(document.getElementById('maxPages').value) || 20;
            const discoverBtn = document.getElementById('discoverBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const pagesSection = document.getElementById('pagesSection');
            
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Show loading, hide other sections
            loading.style.display = 'block';
            loading.innerHTML = '<p>🔄 Discovering pages... This may take a few moments.</p>';
            pagesSection.style.display = 'none';
            document.getElementById('results').style.display = 'none';
            error.style.display = 'none';
            discoverBtn.disabled = true;
            discoverBtn.textContent = '🔍 Discovering...';
            
            try {
                const response = await fetch('/discover', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        url: url,
                        max_pages: maxPages
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    discoveredPages = data.pages;
                    displayPages(data.pages);
                    pagesSection.style.display = 'block';
                } else {
                    throw new Error(data.error || 'Discovery failed');
                }
                
            } catch (err) {
                error.textContent = err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                discoverBtn.disabled = false;
                discoverBtn.textContent = '🔍 Discover Pages';
            }
        }
        
        function displayPages(pages) {
            const pagesGrid = document.getElementById('pagesGrid');
            const pageCount = document.getElementById('pageCount');
            
            pageCount.textContent = `(${pages.length} pages found)`;
            pagesGrid.innerHTML = '';
            
            pages.forEach((page, index) => {
                const pageCard = document.createElement('div');
                pageCard.className = 'page-card';
                pageCard.onclick = () => selectPage(page.url, pageCard);
                
                pageCard.innerHTML = `
                    <div class="page-title">${page.title}</div>
                    <div class="page-url">${page.url}</div>
                    <div class="page-description">${page.description}</div>
                    <div class="page-stats">
                        <span>Path: ${page.path}</span>
                        <span>Elements: ${page.element_count}</span>
                    </div>
                `;
                
                pagesGrid.appendChild(pageCard);
            });
            
            // Auto-select first page
            if (pages.length > 0) {
                setTimeout(() => {
                    pagesGrid.firstChild.click();
                }, 100);
            }
        }
        
        function selectPage(url, cardElement) {
            // Remove previous selection
            document.querySelectorAll('.page-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Select current card
            cardElement.classList.add('selected');
            selectedPageUrl = url;
            
            // Show analyze button
            document.getElementById('analyzeSelectedBtn').style.display = 'block';
            
            // Hide previous results
            document.getElementById('results').style.display = 'none';
        }
        
        async function analyzeSelected() {
            if (!selectedPageUrl) {
                alert('Please select a page to analyze');
                return;
            }
            
            const analyzeBtn = document.getElementById('analyzeSelectedBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const results = document.getElementById('results');
            
            // Show loading
            loading.style.display = 'block';
            loading.innerHTML = '<p>🔄 Analyzing selected page... This may take a few moments.</p>';
            results.style.display = 'none';
            error.style.display = 'none';
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '📊 Analyzing...';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: selectedPageUrl })
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
                analyzeBtn.textContent = '📊 Analyze Selected Page';
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
                    <p><strong>URL:</strong> ${data.url}</p>
                    <img src="data:image/png;base64,${data.screenshot}" alt="Website Screenshot">
                `;
            } else {
                screenshot.innerHTML = `
                    <h3>Website Screenshot</h3>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p>Screenshot not available</p>
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
            const sortedComponents = Object.entries(data.components).sort((a, b) => b[1] - a[1]);
            
            sortedComponents.forEach(([component, count]) => {
                const item = document.createElement('div');
                item.className = 'component-item';
                item.innerHTML = `
                    <strong>${component}</strong><br>
                    Count: ${count}
                `;
                componentList.appendChild(item);
            });
            
            results.style.display = 'block';
            
            // Scroll to results
            results.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Allow Enter key to trigger discovery
        document.getElementById('url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                discoverPages();
            }
        });
        
        // Quick analyze function for backwards compatibility
        async function analyzeWebsite() {
            const url = document.getElementById('url').value.trim();
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            selectedPageUrl = url.startsWith('http') ? url : 'https://' + url;
            await analyzeSelected();
        }
    </script>
</body>
</html>'''
    
    # Write the HTML template file
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Enhanced Website Component Analyzer")
    print("=" * 40)
    print("NEW FEATURES:")
    print("✅ Automatic page discovery via sitemap.xml")
    print("✅ Web crawling for internal links")
    print("✅ Common page pattern detection")
    print("✅ Page selection interface")
    print("✅ Individual page analysis")
    print("\nStarting Flask application...")
    print("Open http://localhost:5000 in your browser")
    print("\nMake sure you have the following dependencies installed:")
    print("pip install flask selenium beautifulsoup4 requests lxml")
    print("\nAlso install ChromeDriver for screenshots")
    
    app.run(debug=True, port=5000,host='0.0.0.0')