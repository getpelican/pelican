Release type: patch

Fix autoreload behavior upon changes to the theme, content or settings. The default `IGNORE_FILES` value is updated to recursively ignore all hidden files and the [default filters](https://watchfiles.helpmanual.io/api/filters/#watchfiles.DefaultFilter.ignore_dirs) from `watchfiles.DefaultFilter` are also used.
