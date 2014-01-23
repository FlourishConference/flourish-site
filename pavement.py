from paver.easy import *
import logging
import re

import misaka as m

from datetime import datetime
from jinja2 import Environment, FileSystemLoader, nodes
from jinja2.ext import Extension
from os import makedirs, mkdir, walk
from os.path import basename, exists, getmtime, splitext
from shutil import copy2
from subprocess import call
from yaml import load as yaml_load


options(
    setup=dict(
        name='flourish-gen',
        version='0.1',
        description='Simple static site generator for the Flourish! website. Written in Python.',
        author='Don Kuntz',
    )
)

# set base logging level. Info by default, debug if debug is true in config file
logging.basicConfig(level=logging.INFO)
l = logging.getLogger('FlourishGen')
l.setLevel(logging.INFO)

#debug ?
if True:
  l.setLevel(logging.DEBUG)


# TASKS
@task
def generate():
  if not exists('./_site/'):
    l.info('Creating ./_site/ directory')
    mkdir('./_site/')

  generate_site()


@task
@consume_args
def publish(args):
  l.error("Not implemented yet")


@task
@consume_args
def draft(args):
  title = ' '.join(args)
  filename = 'posts/' + re.sub(r'\W+', '-', title.lower())
  filename = re.sub(r'[-]{2,}', '-', filename)
  if filename[-1] == '-':
    filename = filename[:-1]

  filename += '.md'

  filecont =  "---\ntitle: \"" + title + "\""
  filecont += "\nlayout: post.html"
  filecont += "\ndate: " + datetime.now().strftime('%Y-%m-%d') + "\n"
  filecont += "\ndraft: true\n---\n\n"

  writer = open(filename, "w")
  writer.write(filecont)



####################
#  SITE GENERATION
####################
def generate_site():
  l.debug("Generating site.")

  env = Environment(loader=FileSystemLoader('./templates'))
  site = {}
  parse_pages(site)
  parse_posts(site)  
  make_site(site, env)


# parse out a file
def parse_file(filename):
  l.debug('Parsing file: ' + filename)
  parsed = {}

  f = open(filename)
  contents = ""
  for line in f:
    contents += line
  f.close()

  frontmatter, bodymatter = re.search(r'\A---\s+^(.+?)$\s+---\s*(.*)\Z', contents, re.M | re.S).groups()
  parsed['content'] = genHTML(bodymatter)
  parsed['config'] = yaml_load(frontmatter)
  parsed['filename'] = basename(filename)
  parsed['changed'] = getmtime(filename)

  return parsed


def genHTML(markdown):
  return m.html(markdown,
                extensions=m.EXT_FENCED_CODE | m.EXT_AUTOLINK | m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT,
                render_flags=m.HTML_SMARTYPANTS
               )

def walk_dir(container, directory, parse_fn) :
  for root, dirs, files in walk(directory):
    for f in files:
      container.append(parse_fn(root + '/' + f))
    for d in dirs:
      walk_dir(container, d, parse_fn)


####################
#    POST THINGS
####################

# Parse all posts in a site...
def parse_posts(site):
  posts = []
  post_directory = './posts'
  walk_dir(posts, post_directory, parse_post)

  posts = sorted(posts, key=lambda p: p['timestamp'], reverse=True)
  site['drafts'] = [x for x in posts if 'draft' in x['config'] and x['config']['draft']]
  site['posts'] = [x for x in posts if x not in site['drafts']]


# parse an individual post
def parse_post(filename):
  post = parse_file(filename)
  post['timestamp'] = datetime.strptime(str(post['config']['date']), '%Y-%m-%d')
  post['date'] = post['timestamp'].strftime('%d %B %Y')

  post['title'] = post['config']['title']

  url = re.sub(r'\W+', '-', post['title'].lower())
  url = re.sub(r'[-]{2,}', '-', url)
  if url[-1] == '-':
      url = url[:-1]
  post['url'] = '/blog/' + url + '/'

  # layout?
  if 'layout' not in post:
    post['layout'] = 'post.html'

  return post


#################
#  PAGE THINGS
#################

# Parse all pages in a site...
def parse_pages(site):
  pages = []
  page_directory = './pages'
  walk_dir(pages, page_directory, parse_page)

  site['pages'] = pages


# parse an indicidual page
def parse_page(filename):
  page = parse_file(filename)
  if 'slug' in page['config']:
    page['slug'] = page['config']['slug']
  else:
    page['slug'] = splitext(page['filename'])[0]

  if 'layout' not in page['config']:
    page['layout'] = 'page.html'
  else:
    page['layout'] = page['config']['layout']

  return page

###############
#  THE MAGIC
###############

# start to put things together
def make_site(site, env):
  expand_pages(site, env)
  #expand_posts(site, env)
  #expand_drafts(site, env)
  copy_assets(site)


# expand pages
def expand_pages(site, env):
  for page in site['pages']:
    out_path = './_site' + page['slug']

    l.debug(str(exists(out_path)) + "\t: " + out_path)
    if not exists(out_path):
      makedirs(out_path)

    writer = open(out_path + 'index.html', 'w')
    template = env.get_template(page['layout'])

    writer.write(template.render(site=site, page=page))
    writer.close()


# expand posts, creating posts and archives
def expand_posts(site, env):
  for post in site['posts']:
    oPath = './_site' + post['url']
    
    # do we need to remake the file?
    l.debug(str(exists(oPath)) + "\t: " + oPath)
    if not exists(oPath):
      makedirs(oPath)

    writer = open(oPath + 'index.html', 'w')
    template = env.get_template(post['layout'])

    writer.write(template.render(site=site, page=post))
    writer.close()

  oFile = './_site/blog/index.html'
  writer = open(oFile, 'w')
  template = env.get_template('index.html')
  writer.write(template.render(page={}, site=site, posts=site['posts']))
  writer.close()


# expand posts, creating posts and archives
def expand_drafts(site, env):
  for post in site['drafts']:
    oPath = './_site/drafts' + post['url']
    post['url'] = oPath[len('./_site'):]
    
    # do we need to remake the file?
    l.debug(str(exists(oPath)) + "\t: " + oPath)
    if not exists(oPath):
      makedirs(oPath)

    writer = open(oPath + 'index.html', 'w')
    template = env.get_template(post['layout'])

    writer.write(template.render(site=site, page=post))
    writer.close()
  
  oFile = './_site/drafts/index.html'
  writer = open(oFile, 'w')
  template = env.get_template('index.html')
  writer.write(template.render(page={}, site=site, posts=site['drafts']))
  writer.close()


def copy_assets(site):
  if not exists('./assets'):
    l.debug('no assets')
    return

  newPath = './_site/'

  for root, dirs, files in walk('./assets'):
    for d in dirs:
      ndir = root + '/' + d
      ndir = ndir.replace('./', newPath)

      if not exists(ndir):
        makedirs(ndir)

    for f in files:
      fPath = root + '/' + f
      nfPath = fPath.replace('./', newPath)

      if exists(nfPath):
        if getmtime(nfPath) > getmtime(fPath):
          continue

      copy2(fPath, nfPath)

