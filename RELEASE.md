Release type: minor

Add setting to allow for empty `alt` attributes in images; it defaults to `False`, which is the current behavior. Empty `alt` text can be indicative of an accessibility oversight, but can be intentional and desired, e.g. https://webaim.org/techniques/alttext/, https://www.w3.org/WAI/tutorials/images/decorative/.
