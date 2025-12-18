import re
import os

file_path = '/mnt/c/Users/ADM/Colrose/backend/templates/blog/post_list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace src="../assets/ and href="../assets/ with {% static 'assets/ 
content = re.sub(r'src="\.\./assets/(?P<path>.*?)"', r'src="{% static \'assets/\g<path>\' %}"', content)
content = re.sub(r'href="\.\./assets/(?P<path>.*?)"', r'href="{% static \'assets/\g<path>\' %}"', content)

# Replace href="../" with /
content = content.replace('href="../"', 'href="/"')

# Replace href="../#section" with /#section
content = re.sub(r'href="\.\./#(?P<section>.*?)"', r'href="/#\g<section>"', content)

# Replace href="blog.html" with {% url 'post_list' %}
content = content.replace('href="blog.html"', 'href="{% url \'post_list\' %}"')

# Replace href="key-ecommerce-kpi.html" with {% url 'post_detail' 'key-ecommerce-kpi' %}
# This is a bit more complex, need to extract slug
def replace_article_links(match):
    filename = match.group(1)
    slug = os.path.splitext(filename)[0]
    return f"href=\"{{% url 'post_detail' '{slug}' %}}\""

content = re.sub(r'href="(?P<filename>[^"]+\.html)"', replace_article_links, content)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Static paths and hrefs updated successfully.")
