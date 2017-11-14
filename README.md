Running the script
- Assumes the vagrant VM is set up (not distributed here)
- Assumes the database is set up (not distributed here)
- Clone the repo to the vagrant installation in a shared folder called 'log'
- vagrant ssh
- cd /vagrant/log
- ```python logs_backend.py```

The program was designed using a single class, LogDatabase, to handle everything. The idea behind this class was to create something handling all the internal stuff (connection and queries to the database), so an external user could easy take this and use it without any knowledge of databases.