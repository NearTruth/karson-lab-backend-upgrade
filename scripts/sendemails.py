#!/usr/bin/env python

#  sending email test using python3 subprocess.run and subprocess.Popen

import subprocess

subprocess.run("echo 'body-python' | mail -s 'subject-python' clarktest989@gmail.com", shell=True)

subprocess.run("echo 'bodyfile-python' > emailtest.txt", shell=True)
subprocess.run("cat emailtest.txt | mail -s 'subjectfile-python' clarktest989@gmail.com",
               shell=True)
subprocess.run("rm emailtest.txt", shell=True)
# use of shell=True is discouraged unless the input can be trusted              