import os
import base64
import json
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from PIL import Image, ImageDraw, ImageFont
import io
import time
import re
from urllib.parse import urlparse
import logging

# Add OpenAI import
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessibilityTester:
    def __init__(self):
        self.driver = None
        self.issues = []
        self.screenshot_data = None
        
    def setup_driver(self):
        """Setup Chrome driver with accessibility testing capabilities"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return False
    
    def test_color_contrast(self):
        """Test color contrast ratios"""
        try:
            # Get all text elements
            text_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
            
            for element in text_elements:
                try:
                    # Get computed styles
                    color = self.driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).color", element
                    )
                    background_color = self.driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).backgroundColor", element
                    )
                    font_size = self.driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).fontSize", element
                    )
                    
                    # Simple contrast check (you can implement more sophisticated contrast calculation)
                    if self.is_low_contrast(color, background_color):
                        location = element.location
                        size = element.size
                        
                        self.issues.append({
                            "type": "Low Color Contrast",
                            "severity": "High",
                            "description": f"Text color {color} on background {background_color} may not meet contrast requirements",
                            "element": element.tag_name,
                            "location": location,
                            "size": size,
                            "recommendation": "Ensure text has sufficient contrast ratio (4.5:1 for normal text, 3:1 for large text)"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in color contrast test: {e}")
    
    def test_missing_alt_text(self):
        """Test for missing alt text in images"""
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in images:
                try:
                    alt_text = img.get_attribute("alt")
                    src = img.get_attribute("src")
                    
                    if alt_text is None or alt_text.strip() == "":
                        location = img.location
                        size = img.size
                        
                        self.issues.append({
                            "type": "Missing Alt Text",
                            "severity": "High",
                            "description": f"Image missing alt text: {src}",
                            "element": "img",
                            "location": location,
                            "size": size,
                            "recommendation": "Add descriptive alt text to convey the purpose and content of the image"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in alt text test: {e}")
    
    def test_missing_labels(self):
        """Test for missing form labels"""
        try:
            inputs = self.driver.find_elements(By.XPATH, "//input[@type!='hidden' and @type!='submit' and @type!='button']")
            
            for input_elem in inputs:
                try:
                    # Check for associated label
                    input_id = input_elem.get_attribute("id")
                    aria_label = input_elem.get_attribute("aria-label")
                    aria_labelledby = input_elem.get_attribute("aria-labelledby")
                    
                    has_label = False
                    
                    if input_id:
                        labels = self.driver.find_elements(By.XPATH, f"//label[@for='{input_id}']")
                        has_label = len(labels) > 0
                    
                    if not has_label and not aria_label and not aria_labelledby:
                        location = input_elem.location
                        size = input_elem.size
                        
                        self.issues.append({
                            "type": "Missing Form Label",
                            "severity": "High",
                            "description": f"Form input missing accessible label",
                            "element": "input",
                            "location": location,
                            "size": size,
                            "recommendation": "Add a label element or aria-label attribute to describe the input field"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in form label test: {e}")
    
    def test_heading_structure(self):
        """Test heading structure (H1-H6)"""
        try:
            headings = self.driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
            
            previous_level = 0
            
            for heading in headings:
                try:
                    tag_name = heading.tag_name.lower()
                    current_level = int(tag_name[1])
                    
                    # Check for skipped heading levels
                    if current_level > previous_level + 1:
                        location = heading.location
                        size = heading.size
                        
                        self.issues.append({
                            "type": "Heading Structure Issue",
                            "severity": "Medium",
                            "description": f"Heading level {current_level} follows heading level {previous_level}, skipping levels",
                            "element": tag_name,
                            "location": location,
                            "size": size,
                            "recommendation": "Use heading levels in sequential order (don't skip levels)"
                        })
                    
                    previous_level = current_level
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in heading structure test: {e}")
    
    def test_aria_attributes(self):
        """Test ARIA attributes"""
        try:
            # Test for elements with ARIA roles
            elements_with_aria = self.driver.find_elements(By.XPATH, "//*[@role or @aria-label or @aria-labelledby or @aria-describedby]")
            
            for element in elements_with_aria:
                try:
                    role = element.get_attribute("role")
                    aria_label = element.get_attribute("aria-label")
                    aria_labelledby = element.get_attribute("aria-labelledby")
                    
                    # Check for invalid ARIA usage (basic check)
                    if role and role not in ["button", "link", "heading", "textbox", "checkbox", "radio", "menuitem", "tab", "tabpanel", "dialog", "banner", "main", "navigation", "complementary", "contentinfo"]:
                        location = element.location
                        size = element.size
                        
                        self.issues.append({
                            "type": "Invalid ARIA Role",
                            "severity": "Medium",
                            "description": f"Element has potentially invalid ARIA role: {role}",
                            "element": element.tag_name,
                            "location": location,
                            "size": size,
                            "recommendation": "Verify ARIA role is appropriate and correctly implemented"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in ARIA test: {e}")
    
    def test_form_accessibility(self):
        """Test form accessibility"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            for form in forms:
                try:
                    # Check for form submission without proper labels
                    submit_buttons = form.find_elements(By.XPATH, ".//input[@type='submit'] | .//button[@type='submit'] | .//button[not(@type)]")
                    
                    for button in submit_buttons:
                        value = button.get_attribute("value")
                        text = button.text
                        
                        if not value and not text:
                            location = button.location
                            size = button.size
                            
                            self.issues.append({
                                "type": "Form Button Missing Text",
                                "severity": "Medium",
                                "description": "Submit button missing accessible text",
                                "element": "button/input",
                                "location": location,
                                "size": size,
                                "recommendation": "Add descriptive text or value attribute to form buttons"
                            })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in form accessibility test: {e}")
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation"""
        try:
            # Check for elements that should be focusable
            interactive_elements = self.driver.find_elements(By.XPATH, "//a | //button | //input | //select | //textarea")
            
            for element in interactive_elements:
                try:
                    tabindex = element.get_attribute("tabindex")
                    
                    # Check for positive tabindex (anti-pattern)
                    if tabindex and tabindex.isdigit() and int(tabindex) > 0:
                        location = element.location
                        size = element.size
                        
                        self.issues.append({
                            "type": "Positive Tabindex",
                            "severity": "Medium",
                            "description": f"Element has positive tabindex ({tabindex}), which can disrupt natural tab order",
                            "element": element.tag_name,
                            "location": location,
                            "size": size,
                            "recommendation": "Use tabindex='0' or remove tabindex to maintain natural tab order"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in keyboard navigation test: {e}")
    
    def test_focus_management(self):
        """Test focus management"""
        try:
            # Check for missing focus indicators
            focusable_elements = self.driver.find_elements(By.XPATH, "//a | //button | //input | //select | //textarea")
            
            for element in focusable_elements:
                try:
                    # Check if element is visible and potentially missing focus styles
                    if element.is_displayed():
                        outline_style = self.driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).outline", element
                        )
                        
                        # This is a simplified check - in real implementation you'd need more sophisticated detection
                        if "none" in outline_style:
                            location = element.location
                            size = element.size
                            
                            self.issues.append({
                                "type": "Missing Focus Indicator",
                                "severity": "Low",
                                "description": "Interactive element may be missing visible focus indicator",
                                "element": element.tag_name,
                                "location": location,
                                "size": size,
                                "recommendation": "Ensure all interactive elements have visible focus indicators"
                            })
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in focus management test: {e}")
    
    def is_low_contrast(self, color, background_color):
        """Simple contrast check (implement proper contrast calculation)"""
        # This is a simplified check - you should implement proper contrast ratio calculation
        # using the WCAG contrast formula
        return "rgba(0, 0, 0, 0)" in background_color or color == background_color
    
    def get_wave_issues(self):
        """Return a deduplicated, filtered list of real accessibility issues for WAVE-style display, matching WAVE logic more closely."""
        seen = set()
        wave_issues = []
        main_types = {
            'Missing Alt Text',
            'Low Color Contrast',
            'Missing Form Label',
            'Heading Structure Issue',
            'Invalid ARIA Role',
            'Form Button Missing Text',
            'Positive Tabindex',
            'Missing Focus Indicator',
        }
        for idx, issue in enumerate(self.issues):
            if issue['type'] not in main_types:
                continue
            # Use element identifier for deduplication (id, src, or tag+location)
            elem_id = issue.get('element', '')
            if issue.get('element', '') == 'img' and issue.get('description', '').startswith('Image missing alt text:'):
                elem_id = issue.get('description', '')  # Use src if available
            # Round location to nearest 10px for deduplication
            x = int(round(issue['location']['x'] / 10.0) * 10) if 'location' in issue else 0
            y = int(round(issue['location']['y'] / 10.0) * 10) if 'location' in issue else 0
            key = (issue['type'], elem_id, x, y)
            if key in seen:
                continue
            seen.add(key)
            wave_issues.append({
                'wave_id': f"wave_{idx}",
                'type': issue['type'],
                'severity': issue['severity'],
                'x': issue['location']['x'] if 'location' in issue else 0,
                'y': issue['location']['y'] if 'location' in issue else 0,
                'description': issue.get('description', ''),
                'recommendation': issue.get('recommendation', '')
            })
        return wave_issues

    def capture_and_highlight_fullpage_screenshots(self, draw_rectangles=True):
        """Capture multiple screenshots to cover the full page. Optionally highlight issues with rectangles (default True)."""
        screenshots = []
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            scroll_step = viewport_height
            num_screens = (total_height + viewport_height - 1) // viewport_height

            for i in range(num_screens):
                scroll_y = i * scroll_step
                self.driver.execute_script(f"window.scrollTo(0, {scroll_y})")
                time.sleep(0.5)

                screenshot = self.driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(screenshot)).convert("RGBA")
                if draw_rectangles:
                    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
                    draw = ImageDraw.Draw(overlay)
                    for issue in self.issues:
                        if 'location' in issue and 'size' in issue:
                            location = issue['location']
                            size = issue['size']
                            x1 = location['x']
                            y1 = location['y']
                            x2 = x1 + size['width']
                            y2 = y1 + size['height']
                            if y2 >= scroll_y and y1 < scroll_y + viewport_height:
                                adj_y1 = y1 - scroll_y
                                adj_y2 = y2 - scroll_y
                                color = self.get_severity_color(issue['severity'], alpha=80)
                                draw.rectangle([x1, adj_y1, x2, adj_y2], outline=color, width=3)
                                draw.rectangle([x1, adj_y1, x2, adj_y2], fill=color)
                    combined = Image.alpha_composite(image, overlay)
                    buffer = io.BytesIO()
                    combined.convert("RGB").save(buffer, format='PNG')
                else:
                    buffer = io.BytesIO()
                    image.convert("RGB").save(buffer, format='PNG')
                buffer.seek(0)
                screenshots.append(base64.b64encode(buffer.getvalue()).decode('utf-8'))
            return screenshots
        except Exception as e:
            logger.error(f"Error capturing full page screenshots: {e}")
            return []

    def group_main_issues(self):
        """Group issues by type and severity, and count them for summary display."""
        grouped = {}
        for issue in self.issues:
            key = (issue['type'], issue['severity'])
            if key not in grouped:
                grouped[key] = {
                    'type': issue['type'],
                    'severity': issue['severity'],
                    'count': 0,
                    'examples': [],
                    'recommendation': issue.get('recommendation', '')
                }
            grouped[key]['count'] += 1
            if len(grouped[key]['examples']) < 3:
                grouped[key]['examples'].append({
                    'description': issue.get('description', ''),
                    'element': issue.get('element', ''),
                    'location': issue.get('location', {})
                })
        # Sort by severity (High > Medium > Low) and count desc
        severity_order = {'High': 0, 'Medium': 1, 'Low': 2}
        grouped_list = sorted(grouped.values(), key=lambda x: (severity_order.get(x['severity'], 3), -x['count']))
        return grouped_list

    def test_url(self, url):
        """Main method to test URL for accessibility issues"""
        if not self.setup_driver():
            return {"error": "Failed to setup browser driver"}
        try:
            self.driver.get(url)
            time.sleep(3)
            self.test_color_contrast()
            self.test_missing_alt_text()
            self.test_missing_labels()
            self.test_heading_structure()
            self.test_aria_attributes()
            self.test_form_accessibility()
            self.test_keyboard_navigation()
            self.test_focus_management()
            # Do not draw rectangles on screenshots anymore
            screenshots = self.capture_and_highlight_fullpage_screenshots(draw_rectangles=False)
            summary = self.generate_summary()
            main_issues = self.group_main_issues()
            wave_issues = self.get_wave_issues()
            return {
                "url": url,
                "total_issues": len(self.issues),
                "issues": self.issues,
                "screenshots": screenshots,
                "summary": summary,
                "main_issues": main_issues,
                "wave_issues": wave_issues
            }
        except Exception as e:
            logger.error(f"Error testing URL {url}: {e}")
            return {"error": f"Failed to test URL: {str(e)}"}
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_severity_color(self, severity, alpha=255):
        """Get RGBA color for severity level, with optional alpha."""
        colors = {
            'High': (231, 76, 60, alpha),      # Red
            'Medium': (243, 156, 18, alpha),   # Orange
            'Low': (241, 196, 15, alpha)       # Yellow
        }
        return colors.get(severity, (231, 76, 60, alpha))
    
    def generate_summary(self):
        """Generate test summary"""
        severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        
        for issue in self.issues:
            severity = issue.get('severity', 'Low')
            severity_counts[severity] += 1
        
        return {
            'total_issues': len(self.issues),
            'high_severity': severity_counts['High'],
            'medium_severity': severity_counts['Medium'],
            'low_severity': severity_counts['Low'],
            'tests_performed': [
                'Color Contrast',
                'Missing Alt Text',
                'Form Labels',
                'Heading Structure',
                'ARIA Attributes',
                'Keyboard Navigation',
                'Focus Management'
            ]
        }

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def test_accessibility():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'https://' + url
        
        # Create tester instance and run test
        tester = AccessibilityTester()
        results = tester.test_url(url)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in test route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/summary', methods=['POST'])
def generate_openai_summary():
    try:
        data = request.get_json()
        main_issues = data.get('main_issues', [])
        if not main_issues:
            return jsonify({'error': 'No issues provided'}), 400
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not set in environment'}), 500
        # Prepare prompt for OpenAI
        prompt = """
You are an expert web accessibility consultant. Given the following grouped accessibility issues found on a website, generate a clear, concise, and beautiful summary for a non-technical website owner. For each main issue type, explain what it means, why it matters, and how to fix it (in simple steps). End with a short encouragement to improve accessibility.

Accessibility Issues:
"""
        for issue in main_issues:
            prompt += f"\n- {issue['type']} (Severity: {issue['severity']}, Count: {issue['count']})"
            if issue['examples']:
                prompt += f"\n  Example: {issue['examples'][0]['description']}"
        prompt += "\n\nSummary and Recommendations:"
        # Call OpenAI API
        openai.api_key = openai_api_key

               
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an accessibility expert providing detailed analysis and recommendations for web accessibility issues."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        summary_text = response.choices[0].message.content
        # summary_text = response['choices'][0]['message']['content']
        return jsonify({'summary': summary_text})
    except Exception as e:
        logger.error(f"Error generating OpenAI summary: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)