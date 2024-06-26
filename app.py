from flask import Flask, request, jsonify
from flask_cors import CORS 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import requests
import re

app = Flask(__name__)
CORS(app)

def extract_subdomains(main_url, limit):
    all_subdomains = set()
    queue = deque([main_url])
    visited = set([main_url])
    count = 0
    
    while queue and count < limit:
        url = queue.popleft()
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extracting links and checking for subdomains in href
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', href):  # Matching URLs
                    domain_match = re.search(r'(https?://)?(?:www\.)?([^/:]+)', href)
                    if domain_match:
                        subdomain = domain_match.group(2)
                        if subdomain != main_url and subdomain not in all_subdomains:
                            all_subdomains.add(subdomain)
                            count += 1
                            if count >= limit:
                                break
                            queue.append('http://' + subdomain)
    
    return list(all_subdomains)

@app.route('/extract_subdomains', methods=['GET'])
def extract_subdomains_api():
    main_url = request.args.get('main_url')
    limit = int(request.args.get('limit', 50))  # Default limit to 50 if not provided
    
    if not main_url:
        return jsonify({'error': 'Main URL is required'}), 400
    
    try:
        all_subdomains = extract_subdomains(main_url, limit)
        return jsonify({'subdomains': all_subdomains})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
