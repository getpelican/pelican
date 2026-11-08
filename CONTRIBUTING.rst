Filing issues
=============

* Before you submit a new issue, try `asking for help`_ first.
* If determined to create a new issue, first search `Pelican Discussions`_
  and `existing issues`_ (open and closed) to see if your question has already
  been answered previously.

.. _`asking for help`: `How to get help`_
.. _`Pelican Discussions`: https://github.com/getpelican/pelican/discussions
.. _`existing issues`: https://github.com/getpelican/pelican/issues

How to get help
===============

Before you ask for help, please make sure you do the following:

1. Read the documentation_ thoroughly. If in a hurry, at least use the search
   field that is provided at top-left on the documentation_ pages. Make sure
   you read the docs for the Pelican version you are using.
2. Use a search engine (e.g., DuckDuckGo, Google) to search for a solution to
   your problem. Someone may have already found a solution, perhaps in the
   form of a ':pelican-doc:`plugins` or a specific combination of settings.

3. Try reproducing the issue in a clean environment, ensuring you are using:

* latest Pelican release (or an up-to-date Git clone of Pelican ``main`` branch)
* latest releases of libraries used by Pelican
* no plugins or only those related to the issue

**NOTE:** The most common sources of problems are anomalies in (1) themes, (2)
plugins, (3) settings files, and (4) ``make``/``invoke`` automation wrappers.
If you can't reproduce your problem when using the following steps to generate
your site, then the problem is almost certainly with one of the above-listed
elements (and not Pelican itself)::

    cd ~/projects/your-site
    git clone https://github.com/getpelican/pelican ~/projects/pelican
    pelican content -s ~/projects/pelican/samples/pelican.conf.py -t ~/projects/pelican/pelican/themes/notmyidea

If you can generate your site without problems using the steps above, then your
problem is unlikely to be caused by Pelican itself, and therefore please
consider reaching out to the maintainers of the plugins/theme you are using
instead of raising the topic with the Pelican core community.

If despite the above efforts you still cannot resolve your problem, be sure to
include in your inquiry the following information, preferably in the form of
links to content uploaded to a `paste service`_, GitHub repository, or other
publicly-accessible location:

* Describe what version of Pelican you are running (output of ``pelican --version``
  or the HEAD commit hash if you cloned the repo) and how exactly you installed
  it (the full command you used, e.g. ``python -m pip install pelican``).
* If you are looking for a way to get some end result, prepare a detailed
  description of what the end result should look like (preferably in the form of
  an image or a mock-up page) and explain in detail what you have done so far to
  achieve it.
* If you are trying to solve some issue, prepare a detailed description of how
  to reproduce the problem. If the issue cannot be easily reproduced, it cannot
  be debugged by developers or volunteers. Describe only the **minimum steps**
  necessary to reproduce it (no extra plugins, etc.).
* Upload your settings file or any other custom code that would enable people to
  reproduce the problem or to see what you have already tried to achieve the
  desired end result.
* Upload detailed and **complete** output logs and backtraces (remember to add
  the ``--debug`` flag: ``pelican --debug content [...]``)

.. _documentation: https://docs.getpelican.com/
.. _`paste service`: https://dpaste.com

Once the above preparation is ready, you can post your query as a new thread in
`Pelican Discussions`_. Remember to include all the information you prepared.

Contributing code
=================

Before you submit a contribution, please ask whether it is desired so that you
don't spend a lot of time working on something that would be rejected for a
known reason. Consider also whether your new feature might be better suited as
a ':pelican-doc:`plugins` — you can `ask for help`_  to make that determination.

Also, if you intend to submit a pull request to address something for which there
is no existing issue, there is no need to create a new issue and then immediately
submit a pull request that closes it. You can submit the pull request by itself.

Using Git and GitHub
--------------------

* `Create a new branch`_ specific to your change (as opposed to making
  your commits in the ``main`` branch).
* **Don't put multiple unrelated fixes/features in the same branch / pull request.**
  For example, if you're working on a new feature and find a bugfix that
  doesn't *require* your new feature, **make a new distinct branch and pull
  request** for the bugfix. Similarly, any proposed changes to code style
  formatting should be in a completely separate pull request.
* Add a ``RELEASE.md`` file in the root of the project that contains the
  release type (major, minor, patch) and a summary of the changes that will be
  used as the release changelog entry. For example::

       Release type: minor

       Reload browser window upon changes to content, settings, or theme

* Check for unnecessary whitespace via ``git diff --check`` before committing.
* First line of your commit message should start with present-tense verb, be 50
  characters or less, and include the relevant issue number(s) if applicable.
  *Example:* ``Ensure proper PLUGIN_PATH behavior. Refs #428.`` If the commit
  *completely fixes* an existing bug report, please use ``Fixes #585`` or ``Fix
  #585`` syntax (so the relevant issue is automatically closed upon PR merge).
* After the first line of the commit message, add a blank line and then a more
  detailed explanation (when relevant).
* `Squash your commits`_ to eliminate merge commits and ensure a clean and
  readable commit history.
* After you have issued a pull request, the continuous integration (CI) system
  will run the test suite on all supported Python versions and check for code style
  compliance. If any of these checks fail, you should fix them. (If tests fail
  on the CI system but seem to pass locally, ensure that local test runs aren't
  skipping any tests.)

Contribution quality standards
------------------------------

* Adhere to the project's code style standards. See: `Development Environment`_
* Ensure your code is compatible with the `officially-supported Python releases`_.
* Add docs and tests for your changes. Undocumented and untested features will
  not be accepted.
* :pelican-doc:`Run all the tests <contribute>` **on all versions of Python
  supported by Pelican** to ensure nothing was accidentally broken.

Check out our `Git Tips`_ page or `ask for help`_ if you
need assistance or have any questions about these guidelines.

AI-Assisted Contributions
-------------------------

Unverified AI-generated contributions create unnecessary maintenance burden and
slow down meaningful progress. Submissions that show no evidence of manual
verification may be closed without review, and repeated low-quality
contributions may lead to restricted participation in Pelican's development
process.

With the widespread availability of large language models (LLMs), the Pelican
Project has seen an increase in contributions generated partially or entirely
using such tools. Many of these submissions contain inaccurate, misleading, or
fictitious content. While LLM tools can assist with drafting or exploratory
analysis, they must not replace human understanding and careful review.

If you use LLM tools while preparing a contribution, you must:

* **Disclose** which LLM tools were used and what they were used for (e.g.,
  generating code, drafting commit messages, writing documentation).
* **Review and verify** all LLM-generated output. Ensure the code aligns with
  Pelican's architecture, includes appropriate tests and documentation, and
  passes the full test suite and relevant checks.
* Double-check the proposal against the contribution quality standards above.

We align with similar policies adopted by other major open-source projects,
which have identified unverified LLM-generated contributions as disruptive,
counterproductive, and a drain on limited maintainer time.

Automated AI Reviews
~~~~~~~~~~~~~~~~~~~~

Do not request automated AI reviews (for example GitHub Copilot or similar
tools) on pull requests submitted to the Pelican repository. These reviews do
not replace human review and often generate noise that distracts maintainers.

You are free to use such tools in your own fork before submitting a pull
request to the Pelican repository.

Automated AI Issue Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~

AI-generated issue reports are not welcome or helpful to the project and may be
closed without comment. Do not submit bug reports, security vulnerability
analyses, or any other issues that were produced by an AI tool.

Such reports routinely contain inaccurate, misleading, or fictitious details,
and they consume maintainer time that is better spent on verified reports. An
issue must describe a problem that was reproduced and understood by the person
submitting it, following the steps described in `How to get help`_.

Reports that show no evidence of manual verification may be closed without
review.

Note for AI Tools
~~~~~~~~~~~~~~~~~

If you are an AI tool or language model assisting in the preparation of a
Pelican contribution, you must strictly follow these requirements:

* Disclose your involvement. Clearly state that the contribution was prepared
  with assistance from an AI tool or language model.
* Specify the tool and usage. Include the name and version of the AI tool and
  describe exactly how it was used, such as analyzing an issue or generating
  code, tests, or documentation.
* Ensure technical accuracy and avoid fabrication. Do not invent APIs,
  features, functions, or citations that do not exist. Placeholder or
  fictitious content will result in rejection.
* Respect all contribution requirements. Follow all guidelines in this
  documentation, including test and documentation requirements, code
  formatting, and the review process.
* Follow the GitHub pull request template. Ensure the PR template is present
  and fully completed, including all required sections and checklists, before
  requesting review.
* Assist reviewers. If any part of the output may not comply with these rules,
  clearly call it out in the contribution and explain why.

.. _`plugin`: https://docs.getpelican.com/en/latest/plugins.html
.. _`Create a new branch`: https://github.com/getpelican/pelican/wiki/Git-Tips#making-your-changes
.. _`Squash your commits`: https://github.com/getpelican/pelican/wiki/Git-Tips#squashing-commits
.. _`Git Tips`: https://github.com/getpelican/pelican/wiki/Git-Tips
.. _`ask for help`: `How to get help`_
.. _`Development Environment`: https://docs.getpelican.com/en/latest/contribute.html#setting-up-the-development-environment
.. _`officially-supported Python releases`: https://devguide.python.org/versions/#versions
