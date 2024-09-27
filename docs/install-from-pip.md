# access-ci-org/ipf %VER%-%REL%
=====================


## Pre-requisites
--------------

### Preparing to Install IPF
-------------------------


- Before installing IPF operators should register their cluster resource in [CiDeR (4)](#CIDER).
  While IPF is capable of publishing information for resources not in CiDeR, ACCESS needs resource
  descriptions in CiDeR to complement the information published with IPF.

- Identify a single server to run IPF -- a single IPF instance can be used to publish information for multiple resources.

- To install IPF on a cluster that presents publicly as multiple resources please review this document:
  [Publishing Software for multiple Resources from a single IPF deployment](https://docs.google.com/document/d/1UXF_pwwZdycuUiV7JToKOKMOHNs6VWjdMWFOjUyKMU4/edit?usp=sharing)

- If you already have an older IPF create a backup of the /etc/ipf working configurations:
  ```
  tar -cf ipf-etc-yyyymmdd.tar /etc/ipf
  ```


### Software Dependencies

- Python 3.6 or newer 
- The python-amqp package


## Installing IPF
--------------

### PIP installation


To install using pip, you need to have the pip package installed in an appropriate version of Python (3.6+).
We recommend using venv to manage Python installations. More information on venv is available at
<https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>

Depending on how many python versions are in place on your system, "pip" may or may not refer to the python 3 version.
"pip3" should always unambiguously refer to a python3 version of pip.

Once you have a Python 3.6 environment (whether venv or not), to install execute:
```
pip3 install ipf
```


When installing via pip, the files get
installed relative to your Python installation (whether in a virtualenv
or system Python). Notably, `ipf_configure` and `ipf_workflow` end
up in the "bin" of the virtualenv, and the location IPF expects to
find as its IPF_ETC_PATH (/etc/ipf in an RPM install) is relative to
the Python site-packages directory.

You can find your site-packages path for the Python you used for the pip install with: 
```
python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'
```


When running any IPF commands by hand in a pip install, you will need to
set the environment variable IPF_ETC_PATH. Its value should be the
site-packages directory referenced above, plus "/etc/ipf". For a system
Python, this might look something like
"/usr/lib/python3.6/site-packages/etc/ipf". 

If you have run `ipf_configure` to set up your workflows, and chosen the
recommended base directory, your workflow definitions will have the
appropriate IPF_ETC_PATH defined in them.

If you wish to have the workflows run as a user other than the one that 
performed the pip install, you will have to do so manually.

## Next Steps
*  [Configure Workflows](configure-workflows.md)
