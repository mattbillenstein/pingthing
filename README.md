# pingthing

A simple daemon to run http checks on your services and email you if they fail.

For best results, do not run this on the same server you're checking, run it on
a machine with uncorrelated failures - preferrably in a different cloud.

There are no dependencies other than access to an smtp server, this should run
on any recent version of python3.

See checks_example.py for an example check and config_example.py for smtp
server config.

See the init directory for init scripts.
