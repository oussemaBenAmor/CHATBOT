# URL Web Scraping Functionality

## Overview
The chatbot now includes advanced web scraping capabilities that allow users to ask questions about transaction types and include URLs. The system will automatically extract relevant information from the websites and provide comprehensive answers.

## Features

### 🔗 **Automatic URL Detection**
- Automatically detects URLs in user questions
- Supports both `http://` and `https://` protocols
- Handles URLs without protocols (adds `https://` automatically)

### 🌐 **Intelligent Web Scraping**
- **Content Extraction**: Focuses on main content areas (main, article, .content, etc.)
- **Transaction Filtering**: Automatically filters content for transaction-related information
- **Smart Cleaning**: Removes navigation, headers, footers, and irrelevant content
- **Relevance Scoring**: Prioritizes sentences containing transaction keywords

### 📊 **Transaction Type Integration**
- **Refunds**: Searches for refund, return, credit, money back, reimbursement
- **Payments**: Looks for payment, pay, card, bank, cash, fee
- **Transfers**: Finds transfer, move, send, wire, bank transfer
- **Exchanges**: Identifies exchange, swap, trade, replace, convert

### 🎯 **Focused Information Extraction**
- Extracts sentences with monetary amounts ($, £, €, ¥)
- Filters content by relevance to the specific transaction type
- Limits output to prevent information overload
- Provides source attribution for each piece of information

## Usage Examples

### Example 1: Refund Information from Website
**User Question**: "What are the refund policies at example.com/refunds?"

**System Response**:
- Detects URL: `example.com/refunds`
- Scrapes the website
- Extracts refund-related information
- Combines with existing knowledge
- Provides comprehensive answer with source attribution

### Example 2: Payment Methods from Multiple Sources
**User Question**: "What payment methods do they accept at payment.example.com and bank.example.com?"

**System Response**:
- Processes both URLs
- Extracts payment-related information from each
- Combines information from multiple sources
- Provides unified answer with clear source separation

### Example 3: Transfer Information with File Upload
**User Question**: "How do I transfer money? Also check transfer.example.com and upload this document"

**System Response**:
- Processes the URL for transfer information
- Extracts content from uploaded document
- Combines both sources
- Provides comprehensive transfer guidance

## Technical Implementation

### Dependencies Added
```bash
beautifulsoup4==4.12.2  # HTML parsing and content extraction
lxml==4.9.3             # Fast XML/HTML processing
urllib3==2.0.7          # HTTP client library
```

### Key Components

#### 1. WebScraper Class (`app/web_scraper.py`)
- **URL Extraction**: Regex-based URL detection
- **Content Scraping**: HTTP requests with proper headers
- **HTML Parsing**: BeautifulSoup for content extraction
- **Content Filtering**: Transaction-relevant information extraction

#### 2. Integration with Chat System
- **Automatic Detection**: URLs detected in real-time
- **Parallel Processing**: Handles multiple URLs efficiently
- **Error Handling**: Graceful fallback for failed scraping
- **Rate Limiting**: Respectful delays between requests

#### 3. Enhanced Answer Generation
- **Multi-Source Answers**: Combines URL data with existing knowledge
- **Source Attribution**: Clear indication of information sources
- **Relevance Ranking**: Prioritizes most relevant information
- **Structured Output**: Organized presentation of findings

## Configuration

### Scraping Settings
```python
# Timeout for web requests
timeout = 10 seconds

# Delay between requests (respectful scraping)
delay = 1 second

# Maximum content length
max_content_length = 1000 characters

# Maximum sentences per URL
max_sentences_per_url = 20
```

### User Agent
```python
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## Error Handling

### Network Issues
- Connection timeouts
- HTTP error responses
- Invalid URLs
- Rate limiting responses

### Content Issues
- Empty or invalid HTML
- JavaScript-heavy pages
- Access restrictions
- Malformed content

## Security Considerations

### Safe Scraping Practices
- **Rate Limiting**: 1-second delays between requests
- **User Agent**: Proper browser identification
- **Timeout Limits**: Prevents hanging requests
- **Error Logging**: Comprehensive error tracking

### Content Validation
- **HTML Sanitization**: Removes potentially harmful content
- **Content Length Limits**: Prevents memory issues
- **Safe Parsing**: Uses established libraries (BeautifulSoup, lxml)

## Performance Optimization

### Efficient Processing
- **Parallel URL Processing**: Handles multiple URLs efficiently
- **Content Caching**: Avoids re-scraping same URLs
- **Smart Filtering**: Only extracts relevant content
- **Memory Management**: Limits content storage

### Scalability
- **Session Reuse**: Maintains HTTP connections
- **Connection Pooling**: Efficient resource usage
- **Async Processing**: Non-blocking operations

## User Experience

### Visual Indicators
- **URL Processing Status**: Shows when websites are being analyzed
- **Source Attribution**: Clear indication of information sources
- **Confidence Scores**: Indicates reliability of extracted information
- **Error Notifications**: Informs users of any scraping issues

### Response Format
```
Transaction Type: Refunds
Confidence: 85%
Found 5 relevant information pieces
Processed 2 website(s)

Based on the website information and available data about refunds:

1. [Database/File information]
2. [Database/File information]

📎 **From Refund Policy Page (https://example.com/refunds):**
   1. Refunds are processed within 5-7 business days
   2. Original receipt required for all refunds
   3. Return shipping costs are customer responsibility
```

## Future Enhancements

### Planned Features
1. **Content Caching**: Store scraped content for future use
2. **Advanced Filtering**: Machine learning-based relevance scoring
3. **Multi-language Support**: Handle websites in different languages
4. **Image Analysis**: Extract information from images and charts
5. **Real-time Updates**: Monitor websites for policy changes

### Performance Improvements
1. **Async Scraping**: Non-blocking URL processing
2. **Content Compression**: Efficient storage of extracted data
3. **Smart Caching**: Intelligent content refresh strategies
4. **Load Balancing**: Distribute scraping across multiple instances

## Troubleshooting

### Common Issues

#### 1. URLs Not Being Processed
- Check if URL format is correct
- Verify website accessibility
- Check for rate limiting

#### 2. Limited Content Extraction
- Website may use JavaScript rendering
- Content might be in non-standard HTML elements
- Access restrictions may apply

#### 3. Slow Response Times
- Multiple URLs being processed
- Network connectivity issues
- Large content extraction

### Debug Information
The system provides detailed logging for troubleshooting:
- URL processing status
- Content extraction results
- Error messages and stack traces
- Performance metrics

## Best Practices

### For Users
1. **Provide Clear URLs**: Use complete, accessible website addresses
2. **Combine Sources**: Use both URLs and file uploads for comprehensive answers
3. **Be Specific**: Ask about specific transaction types for better results

### For Developers
1. **Monitor Logs**: Track scraping success rates and errors
2. **Update User Agents**: Keep browser identification current
3. **Respect Robots.txt**: Check website scraping policies
4. **Handle Errors Gracefully**: Provide fallback responses

## Conclusion

The URL web scraping functionality significantly enhances the chatbot's capabilities by allowing it to access real-time information from websites. This feature provides users with up-to-date, comprehensive answers that combine existing knowledge with current web content, making the system more valuable and informative for transaction-related queries.


