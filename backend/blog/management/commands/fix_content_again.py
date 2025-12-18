
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from blog.models import Post

class Command(BaseCommand):
    help = 'Fixes nested <article> tags in post content.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting nested content fix...'))
        posts = Post.objects.all()
        
        for post in posts:
            soup = BeautifulSoup(post.content, 'lxml')
            
            # The content is currently a full <article> tag.
            # We need to extract the content *inside* this tag.
            article_tag = soup.find('article')
            
            if article_tag:
                # Get the inner HTML of the article tag
                inner_content = article_tag.decode_contents()
                
                if inner_content != post.content:
                    post.content = inner_content
                    post.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully unwrapped content for: "{post.title}"'))
                else:
                    self.stdout.write(self.style.WARNING(f'No changes needed for post: "{post.title}"'))
            else:
                self.stdout.write(self.style.WARNING(f'No <article> tag found in post: "{post.title}", skipping.'))

        self.stdout.write(self.style.SUCCESS('Nested content fix complete.'))
