
import os
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from blog.models import Post
from datetime import datetime
import re

class Command(BaseCommand):
    help = 'Import posts from HTML files'

    def handle(self, *args, **options):
        blog_dir = '/app/blog_html'
        for filename in os.listdir(blog_dir):
            if filename.endswith('.html') and filename != 'index.html':
                filepath = os.path.join(blog_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, 'lxml')
                article_soup = soup.find('article')

                title = ''
                pub_date = None
                image_path = None
                content = ''

                if article_soup:
                    # Extract title and then remove it
                    title_tag = article_soup.find('h1')
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        title_tag.decompose()
                    else:
                        title = os.path.splitext(filename)[0].replace('-', ' ').capitalize()

                    # Extract pub_date and then remove the meta container
                    meta_wrap_tag = article_soup.find('div', class_='cs_post_meta_wrap')
                    if meta_wrap_tag:
                        date_p_tag = meta_wrap_tag.find('p', string=re.compile(r'\d{2}\.\d{2}\.\d{4}'))
                        if date_p_tag:
                            date_str = date_p_tag.get_text(strip=True)
                            try:
                                pub_date = datetime.strptime(date_str, '%d.%m.%Y').replace(tzinfo=timezone.utc)
                            except ValueError:
                                self.stdout.write(self.style.WARNING(f'Could not parse date "{date_str}" for {filename}.'))
                        meta_wrap_tag.decompose()

                    # Extract image and then remove it
                    img_tag = article_soup.find('img')
                    if img_tag and img_tag.has_attr('src'):
                        image_path = img_tag['src'].lstrip('./').lstrip('../')
                        img_tag.decompose()

                    # The remaining soup is the content
                    content = str(article_soup)
                
                else:
                    # Fallback for unexpected structure
                    content = str(soup)
                    title = os.path.splitext(filename)[0].replace('-', ' ').capitalize()

                slug = slugify(os.path.splitext(filename)[0])
                
                defaults = {
                    'title': title,
                    'content': content,
                    'image_path': image_path,
                }
                
                try:
                    post = Post.objects.get(slug=slug)
                    for key, value in defaults.items():
                        setattr(post, key, value)
                    if pub_date: # Only update pub_date if found in HTML for existing post
                        post.pub_date = pub_date
                    post.save()
                    created = False
                except Post.DoesNotExist:
                    if pub_date:
                        defaults['pub_date'] = pub_date
                    else:
                        defaults['pub_date'] = timezone.now() # Fallback for new posts
                    post = Post.objects.create(slug=slug, **defaults)
                    created = True

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported new post: {title}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated existing post: {title}'))

