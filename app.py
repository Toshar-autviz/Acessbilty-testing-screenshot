# # import requests
# # from bs4 import BeautifulSoup
# # from selenium import webdriver
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # import time
# # import base64
# # from urllib.parse import urljoin, urlparse, parse_qs
# # import os
# # from collections import Counter
# # import json
# # import xml.etree.ElementTree as ET
# # from urllib.robotparser import RobotFileParser
# # import re
# # from webdriver_manager.chrome import ChromeDriverManager
# # from selenium.webdriver.chrome.service import Service
# # import tempfile, os, uuid

# # class WebsiteAnalyzer:
# #     def __init__(self):
# #         self.driver = None
# #         self.setup_driver()
# #         self.discovered_pages = []
# #         self.base_domain = None
    
# #     def setup_driver(self):
# #         """Setup Chrome WebDriver with options"""
# #         chrome_options = Options()
# #         chrome_options.add_argument("--headless")  # Run in background
# #         chrome_options.add_argument("--no-sandbox")
# #         chrome_options.add_argument("--disable-dev-shm-usage")
# #         chrome_options.add_argument("--window-size=1920,1080")
# #         # Use a unique, writable user data dir
# #         user_data_dir = f"/tmp/chrome_user_data_{uuid.uuid4()}"
# #         os.makedirs(user_data_dir, exist_ok=True)
# #         chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
# #         try:
# #             self.driver = webdriver.Chrome(options=chrome_options)
# #         except Exception as e:
# #             print(f"Error setting up Chrome driver: {e}")
# #             print("Make sure ChromeDriver is installed and in your PATH")
    
# #     def discover_pages(self, base_url, max_pages=50):
# #         """Discover all available pages on the website"""
# #         print(f"Discovering pages for: {base_url}")
        
# #         # Ensure URL has protocol
# #         if not base_url.startswith(('http://', 'https://')):
# #             base_url = 'https://' + base_url
        
# #         self.base_domain = urlparse(base_url).netloc
# #         discovered_urls = set()
        
# #         # Method 1: Check sitemap.xml
# #         sitemap_urls = self._get_sitemap_urls(base_url)
# #         discovered_urls.update(sitemap_urls)
        
# #         # Method 2: Crawl main page for internal links
# #         internal_links = self._crawl_internal_links(base_url, max_depth=2)
# #         discovered_urls.update(internal_links)
        
# #         # Method 3: Common page patterns
# #         common_pages = self._check_common_pages(base_url)
# #         discovered_urls.update(common_pages)
        
# #         # Limit results and clean URLs
# #         discovered_urls = list(discovered_urls)[:max_pages]
        
# #         # Get page info for each discovered URL
# #         self.discovered_pages = []
# #         for url in discovered_urls:
# #             try:
# #                 page_info = self._get_page_info(url)
# #                 self.discovered_pages.append(page_info)
# #             except Exception as e:
# #                 print(f"Error getting info for {url}: {e}")
        
# #         print(f"Discovered {len(self.discovered_pages)} pages")
# #         return self.discovered_pages
    
# #     def _get_sitemap_urls(self, base_url):
# #         """Extract URLs from sitemap.xml"""
# #         urls = set()
# #         sitemap_urls = [
# #             urljoin(base_url, '/sitemap.xml'),
# #             urljoin(base_url, '/sitemap_index.xml'),
# #             urljoin(base_url, '/robots.txt')  # Check robots.txt for sitemap location
# #         ]
        
# #         for sitemap_url in sitemap_urls:
# #             try:
# #                 response = requests.get(sitemap_url, timeout=10)
# #                 if response.status_code == 200:
# #                     if 'sitemap' in sitemap_url.lower():
# #                         urls.update(self._parse_sitemap(response.text))
# #                     elif 'robots.txt' in sitemap_url:
# #                         sitemap_from_robots = self._get_sitemap_from_robots(response.text)
# #                         for sm_url in sitemap_from_robots:
# #                             sm_response = requests.get(sm_url, timeout=10)
# #                             if sm_response.status_code == 200:
# #                                 urls.update(self._parse_sitemap(sm_response.text))
# #             except Exception as e:
# #                 print(f"Error fetching sitemap from {sitemap_url}: {e}")
        
# #         return urls
    
# #     def _parse_sitemap(self, sitemap_content):
# #         """Parse sitemap XML and extract URLs"""
# #         urls = set()
# #         try:
# #             root = ET.fromstring(sitemap_content)
            
# #             # Handle sitemap index
# #             for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
# #                 loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
# #                 if loc is not None:
# #                     # Fetch individual sitemap
# #                     try:
# #                         response = requests.get(loc.text, timeout=10)
# #                         if response.status_code == 200:
# #                             urls.update(self._parse_sitemap(response.text))
# #                     except:
# #                         pass
            
# #             # Handle individual URLs
# #             for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
# #                 loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
# #                 if loc is not None and self._is_same_domain(loc.text):
# #                     urls.add(loc.text)
                    
# #         except ET.ParseError:
# #             # If not valid XML, try to extract URLs with regex
# #             url_pattern = re.compile(r'https?://[^\s<>"]+')
# #             found_urls = url_pattern.findall(sitemap_content)
# #             for url in found_urls:
# #                 if self._is_same_domain(url):
# #                     urls.add(url)
        
# #         return urls
    
# #     def _get_sitemap_from_robots(self, robots_content):
# #         """Extract sitemap URLs from robots.txt"""
# #         sitemaps = []
# #         for line in robots_content.split('\n'):
# #             if line.lower().startswith('sitemap:'):
# #                 sitemap_url = line.split(':', 1)[1].strip()
# #                 sitemaps.append(sitemap_url)
# #         return sitemaps
    
#     # def _crawl_internal_links(self, base_url, max_depth=2):
#     #     """Crawl website for internal links"""
#     #     urls = set()
#     #     visited = set()
#     #     to_visit = [(base_url, 0)]
        
#     #     while to_visit and len(urls) < 30:  # Limit crawling
#     #         current_url, depth = to_visit.pop(0)
            
#     #         if current_url in visited or depth > max_depth:
#     #             continue
                
#     #         visited.add(current_url)
            
#     #         try:
#     #             if self.driver:
#     #                 self.driver.get(current_url)
#     #                 time.sleep(1)
#     #                 html_content = self.driver.page_source
#     #             else:
#     #                 response = requests.get(current_url, timeout=10)
#     #                 html_content = response.text
                
#     #             soup = BeautifulSoup(html_content, 'html.parser')
                
#     #             # Find all links
#     #             for link in soup.find_all('a', href=True):
#     #                 href = link['href']
#     #                 full_url = urljoin(current_url, href)
                    
#     #                 if self._is_valid_page_url(full_url):
#     #                     urls.add(full_url)
#     #                     if depth < max_depth:
#     #                         to_visit.append((full_url, depth + 1))
                            
#     #         except Exception as e:
#     #             print(f"Error crawling {current_url}: {e}")
        
#     #     return urls
    
# #     def _check_common_pages(self, base_url):
# #         """Check for common page patterns"""
# #         common_paths = [
# #             '', '/', '/home', '/about', '/about-us', '/contact', '/contact-us',
# #             '/services', '/products', '/blog', '/news', '/faq', '/help',
# #             '/privacy', '/terms', '/careers', '/team', '/portfolio',
# #             '/gallery', '/testimonials', '/pricing', '/login', '/register'
# #         ]
        
# #         urls = set()
# #         for path in common_paths:
# #             test_url = urljoin(base_url, path)
# #             try:
# #                 response = requests.head(test_url, timeout=5)
# #                 if response.status_code == 200:
# #                     urls.add(test_url)
# #             except:
# #                 pass
        
# #         return urls
    
# #     def _is_same_domain(self, url):
# #         """Check if URL belongs to the same domain"""
# #         if not self.base_domain:
# #             return True
# #         return urlparse(url).netloc == self.base_domain
    
# #     def _is_valid_page_url(self, url):
# #         """Check if URL is a valid page to analyze"""
# #         parsed = urlparse(url)
        
# #         # Must be same domain
# #         if not self._is_same_domain(url):
# #             return False
        
# #         # Skip certain file types
# #         skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip']
# #         if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
# #             return False
        
# #         # Skip fragments and certain query parameters
# #         if parsed.fragment:
# #             return False
        
# #         return True
    
# #     def _get_page_info(self, url):
# #         """Get basic information about a page"""
# #         try:
# #             if self.driver:
# #                 self.driver.get(url)
# #                 time.sleep(1)
# #                 title = self.driver.title
# #                 html_content = self.driver.page_source
# #             else:
# #                 response = requests.get(url, timeout=10)
# #                 soup = BeautifulSoup(response.text, 'html.parser')
# #                 title = soup.title.string if soup.title else 'Untitled'
# #                 html_content = response.text
            
# #             # Get page description
# #             soup = BeautifulSoup(html_content, 'html.parser')
# #             description = ''
# #             meta_desc = soup.find('meta', attrs={'name': 'description'})
# #             if meta_desc:
# #                 description = meta_desc.get('content', '')
            
# #             # Count basic elements for preview
# #             element_count = len(soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'img', 'a']))
            
# #             return {
# #                 'url': url,
# #                 'title': title.strip() if title else 'Untitled',
# #                 'description': description[:150] + '...' if len(description) > 150 else description,
# #                 'element_count': element_count,
# #                 'path': urlparse(url).path or '/'
# #             }
# #         except Exception as e:
# #             return {
# #                 'url': url,
# #                 'title': 'Error loading page',
# #                 'description': str(e),
# #                 'element_count': 0,
# #                 'path': urlparse(url).path or '/'
# #             }
    
# #     def take_screenshot(self, url):
# #         """Take screenshot of the webpage"""
# #         if not self.driver:
# #             return None
            
# #         try:
# #             self.driver.get(url)
# #             time.sleep(3)  # Wait for page to load
            
# #             # Take screenshot
# #             screenshot = self.driver.get_screenshot_as_png()
            
# #             # Convert to base64 for web display
# #             screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
# #             return screenshot_b64
            
# #         except Exception as e:
# #             print(f"Error taking screenshot: {e}")
# #             return None
    
# #     def extract_components(self, url):
# #         """Extract and analyze HTML components"""
# #         try:
# #             # Get page source
# #             if self.driver:
# #                 self.driver.get(url)
# #                 time.sleep(2)
# #                 html_content = self.driver.page_source
# #             else:
# #                 response = requests.get(url, timeout=10)
# #                 html_content = response.text
            
# #             soup = BeautifulSoup(html_content, 'html.parser')
            
# #             # Count different types of components
# #             components = {}
            
# #             # Basic HTML elements
# #             basic_elements = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
# #                             'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']
            
# #             for element in basic_elements:
# #                 count = len(soup.find_all(element))
# #                 if count > 0:
# #                     components[element] = count
            
# #             # Form elements
# #             form_elements = ['form', 'input', 'textarea', 'select', 'button']
# #             for element in form_elements:
# #                 count = len(soup.find_all(element))
# #                 if count > 0:
# #                     components[element] = count
            
# #             # Media elements
# #             media_elements = ['video', 'audio', 'iframe', 'canvas', 'svg']
# #             for element in media_elements:
# #                 count = len(soup.find_all(element))
# #                 if count > 0:
# #                     components[element] = count
            
# #             # Semantic HTML5 elements
# #             semantic_elements = ['header', 'nav', 'main', 'section', 'article', 
# #                                'aside', 'footer', 'figure', 'figcaption']
# #             for element in semantic_elements:
# #                 count = len(soup.find_all(element))
# #                 if count > 0:
# #                     components[element] = count
            
# #             # Special components detection
# #             components.update(self._detect_special_components(soup))
            
# #             return components
            
# #         except Exception as e:
# #             print(f"Error extracting components: {e}")
# #             return {}
    
# #     def _detect_special_components(self, soup):
# #         """Detect special components like modals, dropdowns, etc."""
# #         special_components = {}
        
# #         # Common class/id patterns for special components
# #         patterns = {
# #             'modals': ['modal', 'popup', 'dialog', 'overlay'],
# #             'dropdowns': ['dropdown', 'select', 'menu'],
# #             'carousels': ['carousel', 'slider', 'swiper'],
# #             'tabs': ['tab', 'accordion'],
# #             'cards': ['card', 'tile'],
# #             'notifications': ['alert', 'notification', 'toast'],
# #             'loaders': ['loader', 'spinner', 'loading'],
# #             'tooltips': ['tooltip', 'popover']
# #         }
        
# #         for component_type, keywords in patterns.items():
# #             count = 0
# #             for keyword in keywords:
# #                 # Check for class names containing keywords
# #                 elements_by_class = soup.find_all(class_=lambda x: x and keyword in ' '.join(x).lower())
# #                 elements_by_id = soup.find_all(id=lambda x: x and keyword in x.lower())
# #                 count += len(elements_by_class) + len(elements_by_id)
            
# #             if count > 0:
# #                 special_components[component_type] = count
        
# #         return special_components
    
# #     def calculate_complexity(self, components):
# #         """Calculate page complexity based on component count"""
# #         # Weight different components based on complexity
# #         complexity_weights = {
# #             # Basic elements (low weight)
# #             'div': 1, 'span': 1, 'p': 1, 'a': 1, 'li': 1,
            
# #             # Headers and structure (medium weight)
# #             'h1': 2, 'h2': 2, 'h3': 2, 'h4': 2, 'h5': 2, 'h6': 2,
# #             'header': 3, 'nav': 3, 'main': 3, 'section': 2, 'footer': 3,
            
# #             # Interactive elements (high weight)
# #             'form': 5, 'input': 3, 'button': 3, 'select': 4, 'textarea': 4,
            
# #             # Media and complex elements (high weight)
# #             'img': 2, 'video': 6, 'audio': 5, 'iframe': 6, 'canvas': 7, 'svg': 4,
            
# #             # Tables (medium weight)
# #             'table': 4, 'tr': 1, 'td': 1, 'th': 2,
            
# #             # Special components (very high weight)
# #             'modals': 8, 'carousels': 10, 'dropdowns': 6, 'tabs': 7,
# #             'cards': 3, 'notifications': 5, 'loaders': 4, 'tooltips': 3
# #         }
        
# #         total_complexity = 0
# #         total_elements = 0
        
# #         for component, count in components.items():
# #             weight = complexity_weights.get(component, 2)  # Default weight
# #             total_complexity += count * weight
# #             total_elements += count
        
# #         return {
# #             'total_elements': total_elements,
# #             'complexity_score': total_complexity,
# #             'complexity_level': self._get_complexity_level(total_complexity)
# #         }
    
# #     def _get_complexity_level(self, score):
# #         """Categorize complexity level"""
# #         if score < 50:
# #             return "Simple"
# #         elif score < 150:
# #             return "Moderate"
# #         elif score < 300:
# #             return "Complex"
# #         else:
# #             return "Very Complex"
    
# #     def analyze_website(self, url):
# #         """Main method to analyze a website"""
# #         print(f"Analyzing website: {url}")
        
# #         # Ensure URL has protocol
# #         if not url.startswith(('http://', 'https://')):
# #             url = 'https://' + url
        
# #         result = {
# #             'url': url,
# #             'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
# #             'screenshot': None,
# #             'components': {},
# #             'complexity': {},
# #             'errors': []
# #         }
        
# #         try:
# #             # Take screenshot
# #             print("Taking screenshot...")
# #             result['screenshot'] = self.take_screenshot(url)
            
# #             # Extract components
# #             print("Extracting components...")
# #             result['components'] = self.extract_components(url)
            
# #             # Calculate complexity
# #             print("Calculating complexity...")
# #             result['complexity'] = self.calculate_complexity(result['components'])
            
# #             print("Analysis complete!")
            
# #         except Exception as e:
# #             error_msg = f"Error analyzing website: {e}"
# #             print(error_msg)
# #             result['errors'].append(error_msg)
        
# #         return result
    
# #     def close(self):
# #         """Close the webdriver"""
# #         if self.driver:
# #             self.driver.quit()

# # # Flask web application
# # from flask import Flask, render_template, request, jsonify

# # app = Flask(__name__)

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/discover', methods=['POST'])
# # def discover():
# #     url = request.json.get('url', '').strip()
# #     max_pages = request.json.get('max_pages', 20)
    
# #     if not url:
# #         return jsonify({'error': 'URL is required'}), 400
    
# #     analyzer = WebsiteAnalyzer()
# #     try:
# #         pages = analyzer.discover_pages(url, max_pages)
# #         return jsonify({'pages': pages})
# #     finally:
# #         analyzer.close()

# # @app.route('/analyze', methods=['POST'])
# # def analyze():
# #     url = request.json.get('url', '').strip()
    
# #     if not url:
# #         return jsonify({'error': 'URL is required'}), 400
    
# #     analyzer = WebsiteAnalyzer()
# #     try:
# #         result = analyzer.analyze_website(url)
# #         return jsonify(result)
# #     finally:
# #         analyzer.close()

# # if __name__ == '__main__':
# #     # Create templates directory if it doesn't exist
# #     if not os.path.exists('templates'):
# #         os.makedirs('templates')
        
# #     print("Enhanced Website Component Analyzer")
# #     print("=" * 40)
# #     print("NEW FEATURES:")
# #     print("✅ Automatic page discovery via sitemap.xml")
# #     print("✅ Web crawling for internal links")
# #     print("✅ Common page pattern detection")
# #     print("✅ Page selection interface")
# #     print("✅ Individual page analysis")
# #     print("\nStarting Flask application...")
# #     print("Open http://localhost:5000 in your browser")
# #     print("\nMake sure you have the following dependencies installed:")
# #     print("pip install flask selenium beautifulsoup4 requests lxml")
# #     print("\nAlso install ChromeDriver for screenshots")
    
# #     app.run(debug=True, port=5000,host='0.0.0.0')

# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import base64
# from urllib.parse import urljoin, urlparse, parse_qs
# import os
# from collections import Counter
# import json
# import xml.etree.ElementTree as ET
# from urllib.robotparser import RobotFileParser
# import re
# from selenium.webdriver.chrome.service import Service
# import tempfile
# import uuid
# import shutil
# import atexit

# class WebsiteAnalyzer:
#     def __init__(self):
#         self.driver = None
#         self.user_data_dir = None
#         self.setup_driver()
#         self.discovered_pages = []
#         self.base_domain = None


#     def setup_driver(self):
#         """Setup Chrome driver with accessibility-focused options"""
#         options = Options()
#         options.add_argument('--headless')
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-gpu')
#         options.add_argument('--window-size=1920,1080')
#         options.add_argument('--force-device-scale-factor=1')
        
#         # self.driver = webdriver.Chrome(options=options)
#         # self.driver.implicitly_wait(10)
#         service = Service(executable_path=os.getenv("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))
#         self.driver = webdriver.Chrome(service=service, options=options)
#         print("done")

    
    
#     # def setup_driver(self):
#     #     """Setup Chrome WebDriver with options for Ubuntu"""
#     #     chrome_options = Options()
#     #     chrome_options.binary_location = "/usr/bin/google-chrome"  # 👈 Add this line

        
#     #     # Essential options for headless mode in Ubuntu
#     #     chrome_options.add_argument("--headless")
#     #     chrome_options.add_argument("--no-sandbox")
#     #     chrome_options.add_argument("--disable-dev-shm-usage")
#     #     chrome_options.add_argument("--disable-gpu")
#     #     chrome_options.add_argument("--disable-extensions")
#     #     chrome_options.add_argument("--disable-plugins")
#     #     chrome_options.add_argument("--disable-images")  # Speed up loading
#     #     chrome_options.add_argument("--window-size=1920,1080")
#     #     chrome_options.add_argument("--remote-debugging-port=9222")
        
#     #     # Create a unique temporary directory for user data
#     #     self.user_data_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
#     #     chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
#     #     # Additional stability options for Ubuntu
#     #     chrome_options.add_argument("--disable-background-timer-throttling")
#     #     chrome_options.add_argument("--disable-backgrounding-occluded-windows")
#     #     chrome_options.add_argument("--disable-renderer-backgrounding")
#     #     chrome_options.add_argument("--disable-features=TranslateUI")
#     #     chrome_options.add_argument("--disable-ipc-flooding-protection")
#     #     chrome_options.add_argument("--single-process")  # Sometimes helps with permission issues
        
#     #     # Set up cleanup on exit
#     #     atexit.register(self.cleanup_temp_dirs)
        
#     #     try:
#     #         # Try to use system chrome first
#     #         self.driver = webdriver.Chrome(options=chrome_options)
#     #         print("Chrome WebDriver initialized successfully")
#     #     except Exception as e:
#     #         print(f"Error setting up Chrome driver: {e}")
#     #         print("\nTroubleshooting steps for Ubuntu:")
#     #         print("1. Install Chrome: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
#     #         print("2. Add repository: echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
#     #         print("3. Update and install: sudo apt update && sudo apt install google-chrome-stable")
#     #         print("4. Install ChromeDriver: sudo apt install chromium-chromedriver")
#     #         print("5. Check Chrome version: google-chrome --version")
#     #         print("6. Check ChromeDriver version: chromedriver --version")
            
#     #         # Cleanup temp directory if driver creation failed
#     #         self.cleanup_temp_dirs()
    
#     def cleanup_temp_dirs(self):
#         """Clean up temporary directories"""
#         if self.user_data_dir and os.path.exists(self.user_data_dir):
#             try:
#                 shutil.rmtree(self.user_data_dir)
#                 print(f"Cleaned up temp directory: {self.user_data_dir}")
#             except Exception as e:
#                 print(f"Error cleaning up temp directory: {e}")
    
#     def discover_pages(self, base_url, max_pages=50):
#         """Discover all available pages on the website"""
#         print(f"Discovering pages for: {base_url}")
        
#         # Ensure URL has protocol
#         if not base_url.startswith(('http://', 'https://')):
#             base_url = 'https://' + base_url
        
#         self.base_domain = urlparse(base_url).netloc
#         discovered_urls = set()
        
#         # Method 1: Check sitemap.xml
#         sitemap_urls = self._get_sitemap_urls(base_url)
#         discovered_urls.update(sitemap_urls)
        
#         # Method 2: Crawl main page for internal links
#         internal_links = self._crawl_internal_links(base_url, max_depth=2)
#         discovered_urls.update(internal_links)
        
#         # Method 3: Common page patterns
#         common_pages = self._check_common_pages(base_url)
#         discovered_urls.update(common_pages)
        
#         # Limit results and clean URLs
#         discovered_urls = list(discovered_urls)[:max_pages]
        
#         # Get page info for each discovered URL
#         self.discovered_pages = []
#         for url in discovered_urls:
#             try:
#                 page_info = self._get_page_info(url)
#                 self.discovered_pages.append(page_info)
#             except Exception as e:
#                 print(f"Error getting info for {url}: {e}")
        
#         print(f"Discovered {len(self.discovered_pages)} pages")
#         return self.discovered_pages
    
#     def _get_sitemap_urls(self, base_url):
#         """Extract URLs from sitemap.xml"""
#         urls = set()
#         sitemap_urls = [
#             urljoin(base_url, '/sitemap.xml'),
#             urljoin(base_url, '/sitemap_index.xml'),
#             urljoin(base_url, '/robots.txt')  # Check robots.txt for sitemap location
#         ]
        
#         for sitemap_url in sitemap_urls:
#             try:
#                 response = requests.get(sitemap_url, timeout=10)
#                 if response.status_code == 200:
#                     if 'sitemap' in sitemap_url.lower():
#                         urls.update(self._parse_sitemap(response.text))
#                     elif 'robots.txt' in sitemap_url:
#                         sitemap_from_robots = self._get_sitemap_from_robots(response.text)
#                         for sm_url in sitemap_from_robots:
#                             sm_response = requests.get(sm_url, timeout=10)
#                             if sm_response.status_code == 200:
#                                 urls.update(self._parse_sitemap(sm_response.text))
#             except Exception as e:
#                 print(f"Error fetching sitemap from {sitemap_url}: {e}")
        
#         return urls
    
#     def _parse_sitemap(self, sitemap_content):
#         """Parse sitemap XML and extract URLs"""
#         urls = set()
#         try:
#             root = ET.fromstring(sitemap_content)
            
#             # Handle sitemap index
#             for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
#                 loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
#                 if loc is not None:
#                     # Fetch individual sitemap
#                     try:
#                         response = requests.get(loc.text, timeout=10)
#                         if response.status_code == 200:
#                             urls.update(self._parse_sitemap(response.text))
#                     except:
#                         pass
            
#             # Handle individual URLs
#             for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
#                 loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
#                 if loc is not None and self._is_same_domain(loc.text):
#                     urls.add(loc.text)
                    
#         except ET.ParseError:
#             # If not valid XML, try to extract URLs with regex
#             url_pattern = re.compile(r'https?://[^\s<>"]+')
#             found_urls = url_pattern.findall(sitemap_content)
#             for url in found_urls:
#                 if self._is_same_domain(url):
#                     urls.add(url)
        
#         return urls
    
#     def _get_sitemap_from_robots(self, robots_content):
#         """Extract sitemap URLs from robots.txt"""
#         sitemaps = []
#         for line in robots_content.split('\n'):
#             if line.lower().startswith('sitemap:'):
#                 sitemap_url = line.split(':', 1)[1].strip()
#                 sitemaps.append(sitemap_url)
#         return sitemaps
    
#     # def _crawl_internal_links(self, base_url, max_depth=2):
#     #     """Crawl website for internal links"""
#     #     urls = set()
#     #     visited = set()
#     #     to_visit = [(base_url, 0)]
        
#     #     while to_visit and len(urls) < 30:  # Limit crawling
#     #         current_url, depth = to_visit.pop(0)
            
#     #         if current_url in visited or depth > max_depth:
#     #             continue
                
#     #         visited.add(current_url)
            
#     #         try:
#     #             if self.driver:
#     #                 self.driver.set_page_load_timeout(15)  # Set timeout
#     #                 self.driver.get(current_url)
#     #                 time.sleep(2)  # Increased wait time
#     #                 html_content = self.driver.page_source
#     #             else:
#     #                 response = requests.get(current_url, timeout=10, headers={
#     #                     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
#     #                 })
#     #                 html_content = response.text
                
#     #             soup = BeautifulSoup(html_content, 'html.parser')
                
#     #             # Find all links
#     #             for link in soup.find_all('a', href=True):
#     #                 href = link['href']
#     #                 full_url = urljoin(current_url, href)
                    
#     #                 if self._is_valid_page_url(full_url):
#     #                     urls.add(full_url)
#     #                     if depth < max_depth:
#     #                         to_visit.append((full_url, depth + 1))
                            
#     #         except Exception as e:
#     #             print(f"Error crawling {current_url}: {e}")
        
#     #     return urls

#     def _crawl_internal_links(self, base_url, max_depth=2):
#         """Crawl website for internal links"""
#         urls = set()
#         visited = set()
#         to_visit = [(base_url, 0)]
        
#         while to_visit and len(urls) < 30:  # Limit crawling
#             current_url, depth = to_visit.pop(0)
            
#             if current_url in visited or depth > max_depth:
#                 continue
                
#             visited.add(current_url)
            
#             try:
#                 if self.driver:
#                     self.driver.get(current_url)
#                     time.sleep(1)
#                     html_content = self.driver.page_source
#                 else:
#                     response = requests.get(current_url, timeout=10)
#                     html_content = response.text
                
#                 soup = BeautifulSoup(html_content, 'html.parser')
                
#                 # Find all links
#                 for link in soup.find_all('a', href=True):
#                     href = link['href']
#                     full_url = urljoin(current_url, href)
                    
#                     if self._is_valid_page_url(full_url):
#                         urls.add(full_url)
#                         if depth < max_depth:
#                             to_visit.append((full_url, depth + 1))
                            
#             except Exception as e:
#                 print(f"Error crawling {current_url}: {e}")
        
#         return urls

    
#     # def _check_common_pages(self, base_url):
#     #     """Check for common page patterns"""
#     #     common_paths = [
#     #         '', '/', '/home', '/about', '/about-us', '/contact', '/contact-us',
#     #         '/services', '/products', '/blog', '/news', '/faq', '/help',
#     #         '/privacy', '/terms', '/careers', '/team', '/portfolio',
#     #         '/gallery', '/testimonials', '/pricing', '/login', '/register'
#     #     ]
        
#     #     urls = set()
#     #     for path in common_paths:
#     #         test_url = urljoin(base_url, path)
#     #         try:
#     #             response = requests.head(test_url, timeout=5, headers={
#     #                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
#     #             })
#     #             if response.status_code == 200:
#     #                 urls.add(test_url)
#     #         except:
#     #             pass
        
#     #     return urls

    
#     def _check_common_pages(self, base_url):
#         """Check for common page patterns"""
#         common_paths = [
#             '', '/', '/home', '/about', '/about-us', '/contact', '/contact-us',
#             '/services', '/products', '/blog', '/news', '/faq', '/help',
#             '/privacy', '/terms', '/careers', '/team', '/portfolio',
#             '/gallery', '/testimonials', '/pricing', '/login', '/register'
#         ]
        
#         urls = set()
#         for path in common_paths:
#             test_url = urljoin(base_url, path)
#             try:
#                 response = requests.head(test_url, timeout=5)
#                 if response.status_code == 200:
#                     urls.add(test_url)
#             except:
#                 pass
        
#         return urls
    
#     def _is_same_domain(self, url):
#         """Check if URL belongs to the same domain"""
#         if not self.base_domain:
#             return True
#         return urlparse(url).netloc == self.base_domain
    
#     def _is_valid_page_url(self, url):
#         """Check if URL is a valid page to analyze"""
#         parsed = urlparse(url)
        
#         # Must be same domain
#         if not self._is_same_domain(url):
#             return False
        
#         # Skip certain file types
#         skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip']
#         if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
#             return False
        
#         # Skip fragments and certain query parameters
#         if parsed.fragment:
#             return False
        
#         return True
    
#     def _get_page_info(self, url):
#         """Get basic information about a page"""
#         try:
#             if self.driver:
#                 self.driver.set_page_load_timeout(15)
#                 self.driver.get(url)
#                 time.sleep(2)
#                 title = self.driver.title
#                 html_content = self.driver.page_source
#             else:
#                 response = requests.get(url, timeout=10)
#                 soup = BeautifulSoup(response.text, 'html.parser')
#                 title = soup.title.string if soup.title else 'Untitled'
#                 html_content = response.text
            
#             # Get page description
#             soup = BeautifulSoup(html_content, 'html.parser')
#             description = ''
#             meta_desc = soup.find('meta', attrs={'name': 'description'})
#             if meta_desc:
#                 description = meta_desc.get('content', '')
            
#             # Count basic elements for preview
#             element_count = len(soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'img', 'a']))
            
#             return {
#                 'url': url,
#                 'title': title.strip() if title else 'Untitled',
#                 'description': description[:150] + '...' if len(description) > 150 else description,
#                 'element_count': element_count,
#                 'path': urlparse(url).path or '/'
#             }
#         except Exception as e:
#             return {
#                 'url': url,
#                 'title': 'Error loading page',
#                 'description': str(e),
#                 'element_count': 0,
#                 'path': urlparse(url).path or '/'
#             }
    
#     def take_screenshot(self, url):
#         """Take screenshot of the webpage"""
#         if not self.driver:
#             print("Driver not available, skipping screenshot")
#             return None
            
#         try:
#             self.driver.set_page_load_timeout(20)
#             self.driver.get(url)
#             time.sleep(5)  # Wait for page to load completely
            
#             # Scroll to ensure full page load
#             self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
#             self.driver.execute_script("window.scrollTo(0, 0);")
#             time.sleep(2)
            
#             # Take screenshot
#             screenshot = self.driver.get_screenshot_as_png()
            
#             # Convert to base64 for web display
#             screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
#             return screenshot_b64
            
#         except Exception as e:
#             print(f"Error taking screenshot: {e}")
#             return None
    
#     def extract_components(self, url):
#         """Extract and analyze HTML components"""
#         try:
#             # Get page source
#             if self.driver:
#                 self.driver.set_page_load_timeout(15)
#                 self.driver.get(url)
#                 time.sleep(3)
#                 html_content = self.driver.page_source
#             else:
#                 # response = requests.get(url, timeout=10, headers={
#                 #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
#                 # })
#                 response = requests.get(url, timeout=10)
#                 html_content = response.text
            
#             soup = BeautifulSoup(html_content, 'html.parser')
            
#             # Count different types of components
#             components = {}
            
#             # Basic HTML elements
#             basic_elements = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
#                             'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']
            
#             for element in basic_elements:
#                 count = len(soup.find_all(element))
#                 if count > 0:
#                     components[element] = count
            
#             # Form elements
#             form_elements = ['form', 'input', 'textarea', 'select', 'button']
#             for element in form_elements:
#                 count = len(soup.find_all(element))
#                 if count > 0:
#                     components[element] = count
            
#             # Media elements
#             media_elements = ['video', 'audio', 'iframe', 'canvas', 'svg']
#             for element in media_elements:
#                 count = len(soup.find_all(element))
#                 if count > 0:
#                     components[element] = count
            
#             # Semantic HTML5 elements
#             semantic_elements = ['header', 'nav', 'main', 'section', 'article', 
#                                'aside', 'footer', 'figure', 'figcaption']
#             for element in semantic_elements:
#                 count = len(soup.find_all(element))
#                 if count > 0:
#                     components[element] = count
            
#             # Special components detection
#             components.update(self._detect_special_components(soup))
            
#             return components
            
#         except Exception as e:
#             print(f"Error extracting components: {e}")
#             return {}
    
#     def _detect_special_components(self, soup):
#         """Detect special components like modals, dropdowns, etc."""
#         special_components = {}
        
#         # Common class/id patterns for special components
#         patterns = {
#             'modals': ['modal', 'popup', 'dialog', 'overlay'],
#             'dropdowns': ['dropdown', 'select', 'menu'],
#             'carousels': ['carousel', 'slider', 'swiper'],
#             'tabs': ['tab', 'accordion'],
#             'cards': ['card', 'tile'],
#             'notifications': ['alert', 'notification', 'toast'],
#             'loaders': ['loader', 'spinner', 'loading'],
#             'tooltips': ['tooltip', 'popover']
#         }
        
#         for component_type, keywords in patterns.items():
#             count = 0
#             for keyword in keywords:
#                 # Check for class names containing keywords
#                 elements_by_class = soup.find_all(class_=lambda x: x and keyword in ' '.join(x).lower())
#                 elements_by_id = soup.find_all(id=lambda x: x and keyword in x.lower())
#                 count += len(elements_by_class) + len(elements_by_id)
            
#             if count > 0:
#                 special_components[component_type] = count
        
#         return special_components
    
#     def calculate_complexity(self, components):
#         """Calculate page complexity based on component count"""
#         # Weight different components based on complexity
#         complexity_weights = {
#             # Basic elements (low weight)
#             'div': 1, 'span': 1, 'p': 1, 'a': 1, 'li': 1,
            
#             # Headers and structure (medium weight)
#             'h1': 2, 'h2': 2, 'h3': 2, 'h4': 2, 'h5': 2, 'h6': 2,
#             'header': 3, 'nav': 3, 'main': 3, 'section': 2, 'footer': 3,
            
#             # Interactive elements (high weight)
#             'form': 5, 'input': 3, 'button': 3, 'select': 4, 'textarea': 4,
            
#             # Media and complex elements (high weight)
#             'img': 2, 'video': 6, 'audio': 5, 'iframe': 6, 'canvas': 7, 'svg': 4,
            
#             # Tables (medium weight)
#             'table': 4, 'tr': 1, 'td': 1, 'th': 2,
            
#             # Special components (very high weight)
#             'modals': 8, 'carousels': 10, 'dropdowns': 6, 'tabs': 7,
#             'cards': 3, 'notifications': 5, 'loaders': 4, 'tooltips': 3
#         }
        
#         total_complexity = 0
#         total_elements = 0
        
#         for component, count in components.items():
#             weight = complexity_weights.get(component, 2)  # Default weight
#             total_complexity += count * weight
#             total_elements += count
        
#         return {
#             'total_elements': total_elements,
#             'complexity_score': total_complexity,
#             'complexity_level': self._get_complexity_level(total_complexity)
#         }
    
#     def _get_complexity_level(self, score):
#         """Categorize complexity level"""
#         if score < 50:
#             return "Simple"
#         elif score < 150:
#             return "Moderate"
#         elif score < 300:
#             return "Complex"
#         else:
#             return "Very Complex"
    
#     def analyze_website(self, url):
#         """Main method to analyze a website"""
#         print(f"Analyzing website: {url}")
        
#         # Ensure URL has protocol
#         if not url.startswith(('http://', 'https://')):
#             url = 'https://' + url
        
#         result = {
#             'url': url,
#             'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
#             'screenshot': None,
#             'components': {},
#             'complexity': {},
#             'errors': []
#         }
        
#         try:
#             # Take screenshot (only if driver is available)
#             if self.driver:
#                 print("Taking screenshot...")
#                 result['screenshot'] = self.take_screenshot(url)
#             else:
#                 print("Skipping screenshot (no driver available)")
            
#             # Extract components
#             print("Extracting components...")
#             result['components'] = self.extract_components(url)
            
#             # Calculate complexity
#             print("Calculating complexity...")
#             result['complexity'] = self.calculate_complexity(result['components'])
            
#             print("Analysis complete!")
            
#         except Exception as e:
#             error_msg = f"Error analyzing website: {e}"
#             print(error_msg)
#             result['errors'].append(error_msg)
        
#         return result
    
#     def close(self):
#         """Close the webdriver and cleanup"""
#         if self.driver:
#             try:
#                 self.driver.quit()
#             except:
#                 pass
#         self.cleanup_temp_dirs()

# # Flask web application
# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/discover', methods=['POST'])
# def discover():
#     print("hello there")
#     url = request.json.get('url', '').strip()
#     max_pages = request.json.get('max_pages', 20)
    
#     if not url:
#         return jsonify({'error': 'URL is required'}), 400
    
#     analyzer = WebsiteAnalyzer()
#     try:
#         pages = analyzer.discover_pages(url, max_pages)

#         return jsonify({'pages': pages})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         print("herer")
#         analyzer.close()

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     url = request.json.get('url', '').strip()
    
#     if not url:
#         return jsonify({'error': 'URL is required'}), 400
    
#     analyzer = WebsiteAnalyzer()
#     try:
#         result = analyzer.analyze_website(url)
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         analyzer.close()

# if __name__ == '__main__':
#     # Create templates directory if it doesn't exist
#     if not os.path.exists('templates'):
#         os.makedirs('templates')
        
#     print("Enhanced Website Component Analyzer - Ubuntu Fixed Version")
#     print("=" * 50)
#     print("FIXES APPLIED:")
#     print("✅ Proper temp directory management")
#     print("✅ Chrome options optimized for Ubuntu")
#     print("✅ Better error handling and cleanup")
#     print("✅ Fallback to requests when driver fails")
#     print("✅ Increased timeouts for stability")
#     print("\nStarting Flask application...")
#     print("Open http://localhost:5000 in your browser")
#     print("\nUbuntu setup commands:")
#     print("sudo apt update")
#     print("sudo apt install -y google-chrome-stable chromium-chromedriver")
#     print("pip install flask selenium beautifulsoup4 requests lxml")
    
#     app.run(debug=True, port=5000, host='0.0.0.0')



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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc

class WebsiteAnalyzer:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.discovered_pages = []
        self.base_domain = None
    
    # def setup_driver(self):
    #     """Setup Chrome WebDriver with options"""
    #     chrome_options = Options()
    #     chrome_options.add_argument("--headless")  # Run in background
    #     chrome_options.add_argument("--no-sandbox")
    #     chrome_options.add_argument("--disable-dev-shm-usage")
    #     chrome_options.add_argument("--window-size=1920,1080")
        
    #     try:
    #         self.driver = webdriver.Chrome(options=chrome_options)
    #     except Exception as e:
    #         print(f"Error setting up Chrome driver: {e}")
    #         print("Make sure ChromeDriver is installed and in your PATH")

    # def setup_driver(self):
    #     """Setup Chrome driver with accessibility-focused options"""
    #     options = Options()
    #     options.add_argument('--headless')
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--disable-dev-shm-usage')
    #     # options.add_argument('--disable-gpu')
    #     options.add_argument('--window-size=1920,1080')
    #     # options.add_argument('--force-device-scale-factor=1')
        
    #     # self.driver = webdriver.Chrome(options=options)
    #     # self.driver.implicitly_wait(10)
    #     service = Service(executable_path=os.getenv("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))
    #     try:
    #         self.driver = webdriver.Chrome(service=service, options=options)
    #     except Exception as e:
    #         print(f"Error setting up Chrome driver: {e}")
    #         print("Make sure ChromeDriver is installed and in your PATH")

    def setup_driver(self):
        """Setup undetected Chrome driver with safe headless options"""
        options = uc.ChromeOptions()
        # options.add_argument('--headless=new')  # Use `new` headless mode (more stable)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        try:
            self.driver = uc.Chrome(options=options, headless=True)
            self.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Error setting up undetected Chrome driver: {e}")
            print("Check if UC dependencies are installed or permissions are correct")

    
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