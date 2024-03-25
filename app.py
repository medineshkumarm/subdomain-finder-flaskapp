from flask import Flask, request, jsonify
from flask_cors import CORS 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import requests

app = Flask(__name__)
CORS(app)

def extract_urls(main_url, limit):
    all_urls = set()
    queue = deque([main_url])
    visited = set([main_url])
    count = 0
    
    while queue and count < limit:
        url = queue.popleft()
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                absolute_url = urljoin(url, href)
                
                if absolute_url not in all_urls and absolute_url not in visited:
                    all_urls.add(absolute_url)
                    visited.add(absolute_url)
                    
                    if absolute_url.startswith(main_url):
                        queue.append(absolute_url)
                        count += 1
                        if count >= limit:
                            break
    
    return list(all_urls)

@app.route('/extract_urls', methods=['GET'])
def extract_urls_api():
    main_url = request.args.get('main_url')
    limit = int(request.args.get('limit', 50))  # Default limit to 50 if not provided
    
    if not main_url:
        return jsonify({'error': 'Main URL is required'}), 400
    
    try:
        all_urls = extract_urls(main_url, limit)
        return jsonify({'urls': all_urls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
