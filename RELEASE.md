Release type: minor

Use HTTPS links in documentation, themes, and settings templates
for sites that support it and/or redirect to it. This also updates
the links to point to the destination URL that sites are now
redirecting to, which primarily affects all Jinja2 and PyPI links.

Modify `ignorable_git_crlf_errors()` in the unit tests to ignore the
possible git error "CRLF will be replaced by LF".

Modify `test_custom_generation_works()` in the unit tests to
explicitly use "en_US.UTF-8" because it was defaulting to character
set ISO8859-1 otherwise.
