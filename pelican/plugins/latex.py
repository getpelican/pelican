# -*- coding: utf-8 -*-
"""
Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.

Installation
------------

To enable, ensure that `latex.py` is put somewhere that is accessible.
Then use as follows by adding the following to your settings.py:

    PLUGINS = ["latex"]

Be careful: Not loading the plugin is easy to do, and difficult to detect. To
make life easier, find where pelican is installed, and then copy the plugin
there. An easy way to find where pelican is installed is to verbose list the
available themes by typing `pelican-themes -l -v`. 

Once the pelican folder is found, copy `latex.py` to the `plugins` folder. Then 
add to settings.py like this:

    PLUGINS = ["pelican.plugins.latex"]

Now all that is left to do is to embed the following to your template file 
between the `<head>` parameters (for the NotMyIdea template, this file is base.html)

    {% if article and article.latex %}
        {{ article.latex }}
    {% endif %}

Usage
-----
Latex will be embedded in every article. If however you want latex only for
selected articles, then in settings.py, add

    LATEX = 'article'

And in each article, add the metadata key `latex:`. For example, with the above
settings, creating an article that I want to render latex math, I would just 
include 'Latex' as part of the metadata without any value:

    Date: 1 sep 2012
    Status: draft
    Latex:

Latex Examples
--------------
###Inline
Latex between `$`..`$`, for example, `$`x^2`$`, will be rendered inline 
with respect to the current html block.

###Displayed Math
Latex between `$$`..`$$`, for example, `$$`x^2`$$`, will be rendered centered in a 
new paragraph.

###Equations
Latex between `\begin` and `\end`, for example, `begin{equation}` x^2 `\end{equation}`, 
will be rendered centered in a new paragraph with a right justified equation number 
at the top of the paragraph. This equation number can be referenced in the document. 
To do this, use a `label` inside of the equation format and then refer to that label 
using `ref`. For example: `begin{equation}` `\label{eq}` X^2 `\end{equation}`. Now 
refer to that equation number by `$`\ref{eq}`$`.
   
Template And Article Examples
-----------------------------
To see an example of this plugin in action, look at 
[this article](http://doctrina.org/How-RSA-Works-With-Examples.html). To see how 
this plugin works with a template, look at 
[this template](https://github.com/barrysteyn/pelican_theme-personal_blog).
"""

from pelican import signals

latexScript = '\n\
    <script src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type= "text/javascript">\n\
       MathJax.Hub.Config({\n\
           config: ["MMLorHTML.js"],\n\
           jax: ["input/TeX","input/MathML","output/HTML-CSS","output/NativeMML"],\n\
           TeX: { extensions: ["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"], equationNumbers: { autoNumber: "AMS" } },\n\
           extensions: ["tex2jax.js","mml2jax.js","MathMenu.js","MathZoom.js"],\n\
           tex2jax: { \n\
               inlineMath: [ [\'$\',\'$\'] ],\n\
               displayMath: [ [\'$$\',\'$$\'] ],\n\
               processEscapes: true },\n\
           "HTML-CSS": {\n\
               styles: { ".MathJax .mo, .MathJax .mi": {color: "black ! important"}}\n\
           }\n\
       });\n\
    </script>\n\
'

def addLatex(gen, metadata):
    """
        The registered handler for the latex plugin. It will add 
        the latex script to the article metadata
    """
    if 'LATEX' in gen.settings.keys() and gen.settings['LATEX'] == 'article':
        if 'latex' in metadata.keys():
            metadata['latex'] = latexScript
    else:
        metadata['latex'] = latexScript

def register():
    """
        Plugin registration
    """
    signals.article_generate_context.connect(addLatex)
