Kasatou-sources
===============

 Kasatou is a yet another imageboard engine written in Python and Django, completly free to use, change and do whatever you want.

 By default Kasatou engine is closed for strangers and users can get access over invitation system, but you can change it simply rewrite middleware file.

Features
===============

 * Thread hiding(by "SAGE!" button).
 * Post search.
 * Customizable styles.
 * Ability for user to delete his posts.
 * Whatever you write - source code is not complicated.


Requirements
===============

 Kasatou engine require Django 1.6 or higher and Python3(maybe will work with Python2 after some fixes). You can use and change all code as much as you need, pull requests is greets.
 
 
Installation
===============

 Download sources in your development directory.
 Do [code]python3 manage.py syncdb[/code], [code]python3 manage.py runserver[/code] to start.
 And that is all! Also it will work with OpenShift RedHat service(look at commented strings in settings.py).

Other
===============

 I'm greatly thanks to Ktan32 for his Kataba engine - it will help me to get on with web-development.
