.. _namespace_plugin_migration:

Migrating plugins to new organization
#####################################

So you want to help migrate a plugin? Great!

If the plugin you want to migrate is located in the `legacy monolithic Pelican Plugins repository`_:

Create an issue at the `legacy monolithic Pelican Plugins repository`_ and ask a maintainer to create a corresponding new repository under the new `Pelican Plugins organization`_ and invite you to join it.

If, on the other hand, you are migrating a plugin from a personal repository:

Create an issue at the `legacy monolithic Pelican Plugins repository`_, include a link to the personal repository, and ask a maintainer for assistance with the next steps.

Initial Setup (By Maintainer)
=============================

Create new repository via: `https://github.com/organizations/pelican-plugins/repositories/new`_

* repository name should not contain the word “pelican”
* add description (example: “Pelican plugin that adds a table of contents to articles”)
* set to **Public**
* do not check the box marked: “Initialize this repository with a README”
* do not add a `README`, `.gitignore`, or license file

Once the repository has been created:

* Settings > Environments > New environment > Name: **Deployment** > *Press "Configure Environment" button* > Add Secret (add `GH_TOKEN` & `PYPI_PASSWORD`)
* Invite collaborators: Settings > Manage Access > Invite teams or people (button)

The following is performed on the maintainer's workstation. Replace `related-posts` below with the name of the to-be-migrated plugin.

Clone the legacy monolithic repository::

    cd ~/projects/pelican-plugins/
    git clone https://github.com/getpelican/pelican-plugins related-posts-legacy
    cd related-posts-legacy

Filter existing commits related to the plugin via `git-filter-repo` (which on macOS can be installed via `brew install git-filter-repo`, or if you have Pipx installed, via `pipx install git-filter-repo`)::

    git filter-repo --path related_posts/ --path-rename related_posts/:
    git log --reverse  # copy full day+date+timestamp of first commit

Create a new (empty) repository with an initial empty commit, using the above date::

    mkdir ../related-posts && cd ../related-posts
    git init --initial-branch=main
    git commit --allow-empty -m "Initial commit" --date="Wed Apr 10 19:12:31 2013 -0400"

Add the new repository as the `origin` remote and push the initial commit::

    git remote add origin git@github.com:pelican-plugins/related-posts.git
    git push origin main

Add legacy plugin clone as a remote and pull contents into new branch::

    git remote add legacy ../related-posts-legacy
    git fetch legacy master
    git checkout -b migrate --track legacy/master

Rebase legacy plugin commits on top of new initial commit and push::

    git rebase --committer-date-is-author-date main
    git push origin migrate

Updating the Plugin
===================

Once a maintainer has created the new (empty) repository and pushed existing commits into a new `migrate` branch, clone the new repository to your workstation and switch to that branch::

    git clone git@github.com:pelican-plugins/related-posts.git ~/projects/pelican-plugins/related-posts
    cd ~/projects/pelican-plugins/related-posts
    git switch migrate

Create the new directory structure and move the plugin code contents to it::

    mkdir -p pelican/plugins/related_posts
    git mv *.py pelican/plugins/related_posts/
    git commit --no-verify -m "Convert to namespace plugin filesystem layout"

Review the `Pelican Plugin CookieCutter Template docs`_ and use the template to generate a fresh project. Here we'll use the Pipx-based method to ephemerally invoke CookieCutter::

    cd ~
    pipx run cookiecutter https://github.com/getpelican/cookiecutter-pelican-plugin

Guidance follows for answering the Cookiecutter questions you will be asked. Except for `plugin_name`, `description`, `authors`, `keywords`, `license`, and `dev_status`, you should be able to just hit the `Return` key to accept the provided default value.

* `plugin_name`: For multiple-word names, put a space in between words and use title case. Should not contain the word “pelican”. Ex: `Related Posts`
* `repo_name`:  For multiple-word names, use a hyphen — not an underscore. Ex: `related-posts`
* `package_name`: Hyphens should be converted to underscores here. Ex: `related_posts`
* `distribution_name`: Prefixed with `pelican-`. Ex: `pelican-related-posts`
* `version`: Leave as `0.0.0` default value, which will be incremented automatically via AutoPub upon initial distribution release.
* `description`: Copy & paste description from repository's **About** section
* `authors`: Review source code and commit history to determine primary author, if any. Ask a maintainer if not clear. Ex: `"Jane Smith <jane@example.com>", "Jack Jones <jack@example.com>"`
* `keywords`: Add relevant keywords, including `"pelican"` and `"plugin"`. Ex: `"pelican", "plugin", "table", "contents"`
* `readme`: Name of the README file. Ex: `README.md`
* `contributing`: Name of the README file. Ex: `CONTRIBUTING.md`
* `license`: Choose the same license as the original plugin.
* `repo_url`: URL to the repository. Ex: `https://github.com/pelican-plugins/related-posts`
* `dev_status`: Development status. Best to choose `5 - Production/Stable` unless there's a good reason not to. Ex: `5`
* `python_version`: Minimum Python version. Best to choose 3.7+. Ex: `^3.7`
* `pelican_version`: Minimum Pelican version. Best to choose 4.5+. Ex: `^4.5`

Copy over the new files generated by the plugin template, none of which presumably exist in the existing repository::

    cd ~/projects/pelican-plugins/
    mv ~/related-posts ~/projects/pelican-plugins/related-posts-new
    cp -R related-posts-new/{.editorconfig,.gitignore,.github,.pre-commit-config.yaml,CONTRIBUTING.md,pyproject.toml,tasks.py,tox.ini} related-posts/

Add any plugin dependencies to the `pyproject.toml` file via `poetry add […]` and adjust them in `pyproject.toml` to ensure they are in alphabetical order.

Compare the old and new README files, merging them such that the relevant parts of the template-generated README are present — particularly the build/PyPI status badges and the **Installation** and **Contributing** sections.

Are there any tests? If not, now might be a good time to copy over the generated test file and then add some::

    cp related-posts-new/pelican/plugins/related_posts/test_related_posts.py related-posts/pelican/plugins/related_posts/test_related_posts.py

Create a virtual environment and set up the project::

    cd ~/projects/pelican-plugins/related-posts
    python -m venv ~/virtualenvs/related-posts
    source ~/virtualenvs/related-posts/bin/activate
    python -m pip install -U pip invoke
    invoke setup

Confirm that the plugin is detected and registered::

    pelican-plugins

Run the test suite and ensure there are no failures or errors::

    pytest

Test that the plugin actually works by building it and installing the packaged distribution::

    poetry build
    pip install dist/pelican-related-posts-0.0.0.tar.gz

Fix functional issues, if any, and then commit Python code fixes with appropriate commit message(s)::

    git add [...]
    git commit --no-verify

Ensure code has been modernized for Python 3.7+, review the changed files, modify as necessary, and commit::

    pipx run pyupgrade --py37-plus pelican/plugins/related_posts/*.py
    git add [...]
    git commit --no-verify -m "Modernize code for Python 3.7+"

Make sure the GitHub Actions CI/CD workflow refers to the repository's actual primary branch name (e.g., `main`)::

    grep github\.ref .github/workflows/main.yml

Add and commit the new files related to code style::

    git add .editorconfig .pre-commit-config.yaml tasks.py tox.ini .github
    git commit --no-verify -m "Add code style and CI/CD configuration"

Apply Black and `isort` formatting, ensure linting passes, and commit any code style changes::

    inv black
    inv isort
    inv lint
    git add [...]
    git commit -m "Apply code style conventions to project"

Add and commit `pyproject.toml` and `.gitignore`::

    git add pyproject.toml .gitignore
    git commit -m "Add pyproject file to project"

Add and commit README changes and the CONTRIBUTING file::

    git add README.md CONTRIBUTING.md
    git commit -m "Update README and add CONTRIBUTING"

Assuming all new and changed files have been committed, push the branch and submit a pull request::

    git push origin migrate

Clean Up
--------

Remove legacy clone and generated template files::

    cd ~/projects/pelican-plugins/
    rm -rf related-posts-legacy related-posts-new

Remove section from `.git/config` that is no longer needed::

    cd related-posts
    git remote remove legacy

Add a note at the top of the legacy plugin README in the deprecated monolithic repository indicating that the plugin has migrated. 🎉

.. _legacy monolithic Pelican Plugins repository: https://github.com/getpelican/pelican-plugins
.. _Pelican Plugins organization: https://github.com/pelican-plugins
.. _https://github.com/organizations/pelican-plugins/repositories/new: https://github.com/organizations/pelican-plugins/repositories/new
.. _Pelican Plugin CookieCutter Template docs: https://github.com/getpelican/cookiecutter-pelican-plugin#pelican-plugin-cookiecutter-template
