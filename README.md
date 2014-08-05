#Flourish!

This will soon be the new Flourish website for 2014 and on. It is still a work in progress.

## Static Site Generator

There's a static site generator included. It'll output the generated site in a new `_site` directory. To run the generator you need to have [Jinja2](http://jinja.pocoo.org/docs/) and [markdown2](https://github.com/trentm/python-markdown2) installed.

To install those, you can (and probably should) use pip:

``` shell
# pip install Jinja2 markdow2
``` 

At present the posts feature doesn't work (it was deactivated because they aren't being used. It would be really easy to reactivate).

### Using the generator

The generator uses paver to execute tasks. This is mostly due to it being based on an earlier static site generator which actually had more tasks involving post generation and site publishing, but those aren't currently being used.

There's really only one command that can be used right now, and that's `generate`. Calling `python makeme.py generate` will turn all of the pages into real pages, and copy all of the static assets. 

If you want to view the generated site, you can run a python server by using `python -m http.server` (python3) or `python -m SimpleHTTPServer` (python2) while in the `_site` directory.
