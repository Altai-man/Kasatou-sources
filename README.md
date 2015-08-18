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

 Kasatou engine requires Django 1.7.9(or higher), Postgresql and Python3(maybe engine will works with Python2 after some fixes). You can use and change all code as much as you need, pull requests are welcome.


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

 I'm greatly thankful to @Ktan32 for his Kataba engine - it was help me to get on with web-development. Also I really appreciate @Ordy's help - his default design for Kasatou engine is simple yet really pleasurable.
