Kasatou-sources
===============

 Kasatou is a yet another imageboard engine written in Python and Django, completly free to use, change and do whatever you want.

 By default Kasatou engine is closed for strangers and users can get access over invitation system, but you can change it by simply rewriting middleware file.

Features
===============

 * Thread hiding(by "SAGE!" button).
 * Post search.
 * Customizable styles.
 * Ability for user to edit and delete his posts.
 * Whatever you write - source code is not complicated.

Requirements
===============

 Kasatou engine requires Django from 1.6 to 1.8 and Python3(maybe will work with Python2 after some fixes). You can use and change all code as much as you need, pull requests is welcome.
 
 
Installation
===============

 Download sources in your development directory.
 Do 
 ```
 python3 manage.py syncdb
 python3 manage.py runserver
 ```
 to start.
 And that is all! Also it will work with OpenShift RedHat service(look at commented strings in settings.py).

Other
===============

 I'm greatly thank to Ktan32 for his Kataba engine - it was help me to get on with web-development.