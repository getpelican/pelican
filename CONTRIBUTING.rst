Contribution submission guidelines
==================================

* Consider whether your new feature might be better suited as a
  :doc:`plugin<plugins>`. Folks are usually available in the
  `#pelican IRC channel`_ to help make that determination.
* `Create a new git branch`_ specific to your change (as opposed to making
  your commits in the master branch).
* **Don't put multiple fixes/features in the same branch / pull request.**
  For example, if you're hacking on a new feature and find a bugfix that
  doesn't *require* your new feature, **make a new distinct branch and pull
  request** for the bugfix.
* Adhere to PEP8 coding standards whenever possible.
* Check for unnecessary whitespace via ``git diff --check`` before committing.
* **Add docs and tests for your changes**.
* **Run all the tests on both Python 2.7+ and 3.2+** to ensure nothing was
  accidentally broken.
* First line of your commit message should start with present-tense verb, be 50
  characters or less, and include the relevant issue number(s) if applicable.
  *Example:* ``Ensure proper PLUGIN_PATH behavior. Refs #428.`` If the commit
  *completely fixes* an existing bug report, please use ``Fixes #585`` or ``Fix
  #585`` syntax (so the relevant issue is automatically closed upon PR merge).
* After the first line of the commit message, add two returns and then a more
  detailed explanation (when relevant).
* **Use** ``hub pull-request`` when submitting code for a **pre-existing GitHub
  Issue**. This isn't an absolute requirement, but makes the maintainers' lives
  much easier! Specifically: `install hub
  <https://github.com/defunkt/hub/#installation>`_ and then run `hub
  pull-request <https://github.com/defunkt/hub/#git-pull-request>`_ to turn the
  issue into a pull request containing your code.

Check out our `Git Tips`_ page or ask on the `#pelican IRC channel`_ if you
need assistance or have any questions about these guidelines.

.. _`#pelican IRC channel`: http://webchat.freenode.net/?channels=pelican&uio=d4
.. _`Create a new git branch`: https://github.com/getpelican/pelican/wiki/Git-Tips#making-your-changes
.. _`Git Tips`: https://github.com/getpelican/pelican/wiki/Git-Tips
