

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urlunparse
from typing import Dict, List, Optional
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.timeout = 15
        
        # Enhanced transaction condition keywords
        self.condition_keywords = {
            'refunds': [
                'refund', 'return', 'credit', 'money back', 'reimbursement', 'policy', 'terms',
                'conditions', 'requirements', 'deadline', 'time limit', 'receipt', 'packaging',
                'restocking fee', 'shipping cost', 'return shipping', 'original condition',
                'unused', 'unopened', 'defective', 'damaged', 'wrong item', 'size exchange'
            ],
            'payments': [
                'payment', 'pay', 'card', 'bank', 'cash', 'fee', 'charge', 'method', 'accepted',
                'credit card', 'debit card', 'bank transfer', 'wire transfer', 'check', 'money order',
                'processing fee', 'transaction fee', 'convenience fee', 'late fee', 'penalty',
                'minimum payment', 'due date', 'grace period', 'interest rate', 'apr'
            ],
            'transfers': [
                'transfer', 'move', 'send', 'wire', 'bank transfer', 'money transfer', 'electronic transfer',
                'ach transfer', 'domestic transfer', 'international transfer', 'transfer fee', 'processing time',
                'transfer limit', 'daily limit', 'monthly limit', 'recipient', 'account number', 'routing number',
                'swift code', 'iban', 'transfer amount', 'minimum transfer', 'maximum transfer'
            ],
            'exchanges': [
                'exchange', 'swap', 'trade', 'replace', 'substitution', 'conversion', 'policy', 'terms',
                'conditions', 'requirements', 'time limit', 'deadline', 'original packaging', 'receipt',
                'same value', 'price difference', 'restocking fee', 'shipping cost', 'size exchange',
                'color exchange', 'model exchange', 'brand exchange', 'exchange fee', 'processing time'
            ]
        }
        
        # Policy and condition indicators
        self.policy_indicators = [
            'policy', 'policies', 'terms', 'conditions', 'requirements', 'rules', 'guidelines',
            'procedures', 'process', 'steps', 'instructions', 'information', 'details', 'note',
            'important', 'please note', 'attention', 'warning', 'caution', 'restrictions'
        ]
        
        # Monetary and time patterns
        self.monetary_patterns = [
            r'[\$£€¥]\s*\d+(?:\.\d{2})?',  # $100, $100.50
            r'\d+(?:\.\d{2})?\s*[\$£€¥]',  # 100$, 100.50$
            r'\d+\s*(?:dollars?|euros?|pounds?|yen)',  # 100 dollars, 50 euros
            r'\d+\s*percent',  # 15 percent
            r'\d+%',  # 15%
        ]
        
        self.time_patterns = [
            r'\d+\s*(?:days?|weeks?|months?|years?)',  # 30 days, 2 weeks
            r'\d+\s*(?:business\s+days?|working\s+days?)',  # 5 business days
            r'\d+\s*(?:hours?|minutes?)',  # 24 hours, 30 minutes
            r'(?:same\s+day|next\s+day|overnight)',  # same day, next day
        ]
        
    def extract_urls_from_text(self, text: str) -> List[str]:
        # Enhanced URL pattern for full URLs
        url_pattern = r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[a-zA-Z0-9-_./?=&%#]*)?'
        urls = re.findall(url_pattern, text)
        
        no_protocol_pattern = r'(?:www\.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[a-zA-Z0-9-_./?=&%#]*)?'
        no_protocol_urls = re.findall(no_protocol_pattern, text)
        
        # Filter and combine URLs
        all_urls = urls + ['https://' + url for url in no_protocol_urls if url not in urls]
        
        # Clean and normalize URLs
        cleaned_urls = []
        seen_normalized = set()
        for url in all_urls:
            cleaned_url = self.clean_and_reconstruct_url(url)
            if cleaned_url and self.is_valid_url(cleaned_url):
                parsed = urlparse(cleaned_url)
                netloc = parsed.netloc.lower().replace('www.', '')
                normalized_parts = (
                    parsed.scheme.lower(),
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                )
                normalized_url = urlunparse(normalized_parts)
                if normalized_url not in seen_normalized:
                    seen_normalized.add(normalized_url)
                    cleaned_urls.append(cleaned_url)
        
        return cleaned_urls
    
    def clean_and_reconstruct_url(self, url: str) -> str:
        """Clean and reconstruct URLs with missing characters"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        tld_mappings = {
            'com': 'com', 'org': 'org', 'net': 'net', 'gov': 'gov', 'edu': 'edu',
            'co': 'co', 'io': 'io', 'ai': 'ai', 'uk': 'uk', 'ca': 'ca',
            'au': 'au', 'de': 'de', 'fr': 'fr', 'it': 'it', 'es': 'es',
            'nl': 'nl', 'se': 'se', 'no': 'no', 'dk': 'dk', 'fi': 'fi'
        }
        for tld, replacement in tld_mappings.items():
            pattern = rf'([a-zA-Z0-9]){tld}'
            if re.search(pattern, url) and not re.search(rf'\.{tld}', url):
                url = re.sub(pattern, rf'\1.{replacement}', url)
        for tld in tld_mappings.keys():
            if f'.{tld}' in url:
                tld_pattern = rf'\.{tld}([a-zA-Z0-9])'
                if re.search(tld_pattern, url):
                    url = re.sub(tld_pattern, rf'.{tld}/\1', url)
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and len(parsed.netloc) > 3 and re.match(r'^[a-zA-Z0-9-.]+\.[a-zA-Z]{2,}$', parsed.netloc)
        except:
            return False
    
    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """Enhanced scraping with better error handling and content extraction"""
        try:
            logger.info(f"Scraping URL: {url}")
            url = self.clean_and_reconstruct_url(url)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
            ]
            response = None
            for user_agent in user_agents:
                try:
                    self.session.headers.update({'User-Agent': user_agent})
                    time.sleep(0.5)
                    response = self.session.get(url, timeout=self.timeout)
                    if response.status_code == 403 and 'cloudflare' in response.text.lower():
                        logger.warning(f"Cloudflare protection detected for {url}")
                        continue
                    response.raise_for_status()
                    break
                except Exception as e:
                    logger.warning(f"Failed with user agent {user_agent}: {e}")
                    continue
            if not response:
                raise requests.exceptions.RequestException("Failed to fetch with all user agents")
            try:
                if response.encoding:
                    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
                else:
                    soup = BeautifulSoup(response.content, 'html.parser')
            except:
                soup = BeautifulSoup(response.content, 'html.parser')
            if 'cloudflare' in soup.get_text().lower() or 'challenge' in soup.get_text().lower():
                logger.warning(f"Cloudflare challenge page detected for {url}")
                return {'url': url, 'status': 'error', 'error': 'Website protected by Cloudflare - cannot access content'}
            content = self.extract_relevant_content(soup)
            if not content.strip() or len(content.strip()) < 100:
                content = self.extract_content_aggressive(soup)
            return {
                'url': url,
                'title': self.extract_title(soup),
                'content': content,
                'status': 'success'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return {'url': url, 'status': 'error', 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return {'url': url, 'status': 'error', 'error': str(e)}
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title with fallbacks"""
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            return title_tag.get_text().strip()
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')[:100]
        return "No title found"
    
    def extract_content_aggressive(self, soup: BeautifulSoup) -> str:
        """More aggressive content extraction when normal methods fail"""
        content = ""
        content_elements = soup.find_all(['p', 'div', 'span', 'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for element in content_elements:
            text = element.get_text().strip()
            if text and len(text) > 10:
                content += text + "\n"
        if not content.strip():
            body = soup.find('body')
            if body:
                content = body.get_text()
        if not content.strip():
            content = soup.get_text()
        return content
    
    def extract_relevant_content(self, soup: BeautifulSoup) -> str:
        """Universal content extraction that works on ANY website"""
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "menu", "form"]):
            element.decompose()
        universal_selectors = [
            'main', 'article', '.content', '.main-content', '#content', '#main',
            '.post-content', '.entry-content', '.policy-content', '.terms-content',
            '.conditions', '.requirements', '.rules', '.guidelines', '.procedures',
            '.info', '.details', '.text', '.body', '.main', '.container',
            'div[class*="content"]', 'div[class*="text"]', 'div[class*="info"]',
            'div[class*="main"]', 'div[class*="body"]', 'div[class*="container"]',
            'div[class*="wrapper"]', 'div[class*="section"]', 'div[class*="article"]',
            '.content', '.text', '.body', '.main', '.article', '.post', '.entry',
            '.policy', '.terms', '.conditions', '.requirements', '.rules'
        ]
        content = ""
        for selector in universal_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text().strip()
                        if text and len(text) > 20:
                            content += text + "\n"
                    if content.strip():
                        break
            except:
                continue
        if not content.strip():
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
            for element in text_elements:
                text = element.get_text().strip()
                if text and len(text) > 15:
                    content += text + "\n"
        if not content.strip():
            body = soup.find('body')
            if body:
                content = body.get_text()
        if not content.strip():
            content = self.extract_content_aggressive(soup)
        content = self.clean_content(content)
        return content
    
    def clean_content(self, content: str) -> str:
        """Universal content cleaning that works on any website"""
        content = re.sub(r'\s+', ' ', content)
        noise_patterns = [
            r'Cookie|Privacy|Terms|Contact|About|Home|Login|Sign up|Subscribe|Newsletter',
            r'Follow us|Share|Like|Comment|Tweet|Post',
            r'Advertisement|Ad|Sponsored|Promoted',
            r'Menu|Navigation|Search|Filter|Sort',
            r'Copyright|All rights reserved|Legal|Disclaimer',
            r'Accept|Reject|Close|Skip|Continue|Next|Previous',
            r'Loading|Please wait|Processing|Error|Success|Warning',
            r'Back to top|Scroll to top|Go to top',
            r'Read more|Learn more|Find out more|Discover more',
            r'Subscribe|Newsletter|Stay updated|Get notified'
        ]
        for pattern in noise_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        sentences = re.split(r'[.!?]+', content)
        relevant_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:
                sentence_lower = sentence.lower()
                if any(indicator in sentence_lower for indicator in [
                    'policy', 'terms', 'conditions', 'requirements', 'rules', 'guidelines',
                    'procedures', 'process', 'steps', 'instructions', 'information', 'details',
                    'important', 'note', 'attention', 'warning', 'caution', 'restrictions',
                    'fee', 'cost', 'charge', 'price', 'deadline', 'time', 'limit',
                    'eligible', 'not eligible', 'require', 'need', 'must', 'should',
                    'refund', 'reimbursement', 'return', 'exchange', 'payment', 'transfer',
                    'will', 'can', 'cannot', 'may', 'if', 'when', 'after', 'before'
                ]):
                    relevant_sentences.append(sentence)
                elif re.search(r'\d+', sentence):
                    relevant_sentences.append(sentence)
                elif any(term in sentence_lower for term in ['€', 'euro', 'dollar', '$', 'pound', '£', '¥', 'yen']):
                    relevant_sentences.append(sentence)
                elif len(sentence) > 30:
                    relevant_sentences.append(sentence)
        if not relevant_sentences:
            relevant_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:30]
        return '. '.join(relevant_sentences[:50])
    
    
    def extract_transaction_conditions(self, content: str, transaction_type: str) -> Dict[str, List[str]]:
        """
        Extract transaction conditions and requirements for any transaction type, organized by category.
        """
        categories = {
        'requirements': ['require', 'need', 'must', 'should', 'have to', 'eligible', 'condition', 'qualify', 'prerequisite'],
        'fees': ['fee', 'cost', 'charge', 'price', '$', 'percent', '%', '€', 'euro', 'dollar', 'pound', 'yen', 'amount', 'rate'],
        'timeframes': ['day', 'week', 'month', 'hour', 'time', 'deadline', 'period', 'duration', 'limit', 'expiry', 'valid', 'year'],
        'restrictions': ['cannot', 'not allowed', 'prohibited', 'restricted', 'limit', 'not eligible', 'exclusive', 'forbidden', 'banned', 'excluded'],
        'procedures': ['step', 'process', 'procedure', 'how to', 'follow', 'complete', 'submit', 'fill', 'form', 'application', 'request', 'file', 'check'],
        'general_info': ['policy', 'terms', 'conditions', 'rules', 'guidelines', 'information', 'details', 'note', 'important', 'attention']
        }
        conditions = {cat: [] for cat in categories}
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:
                continue
            sentence_lower = sentence.lower()
            found = False
            for cat, keywords in categories.items():
                if any(word in sentence_lower for word in keywords):
                    conditions[cat].append(sentence)
                    found = True
                    break
            if not found and len(sentence) > 20:
                conditions['general_info'].append(sentence)
        for category in conditions:
            conditions[category] = conditions[category][:8]
        return conditions
    
    def extract_transaction_info(self, content: str, transaction_type: str) -> List[str]:
        """Enhanced transaction information extraction with better categorization"""
        conditions = self.extract_transaction_conditions(content, transaction_type)
        all_info = []
        all_info.extend(conditions['requirements'])
        all_info.extend(conditions['timeframes'])
        all_info.extend(conditions['fees'])
        all_info.extend(conditions['procedures'])
        all_info.extend(conditions['restrictions'])
        if len(all_info) < 5:
            all_info.extend(conditions['general_info'])
        return all_info[:12]
    
    def process_urls_in_question(self, question: str, transaction_type: str) -> List[Dict]:
        """Process URLs with enhanced condition extraction"""
        urls = self.extract_urls_from_text(question)
        results = []
        for url in urls:
            if self.is_valid_url(url):
                time.sleep(1)
                scraped_data = self.scrape_url(url)
                if scraped_data and scraped_data['status'] == 'success':
                    transaction_conditions = self.extract_transaction_conditions(
                        scraped_data['content'], transaction_type
                    )
                    transaction_info = self.extract_transaction_info(
                        scraped_data['content'], transaction_type
                    )
                    results.append({
                        'url': url,
                        'title': scraped_data['title'],
                        'transaction_info': transaction_info,
                        'transaction_conditions': transaction_conditions,
                        'raw_content': scraped_data['content'][:1500],
                        'status': 'success'
                    })
                else:
                    results.append(scraped_data)
        return results

def create_web_scraper():
    """Factory function to create enhanced web scraper instance"""
    return WebScraper()