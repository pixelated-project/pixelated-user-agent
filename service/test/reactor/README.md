To test the run times of functions in the main reactor thread:

- Apply the patch defer.patch
```
patch <venv>/local/lib/python2.7/twisted/internet/defer.py service/test/reactor/defer.patch
```
- Run the user agent, preferrably out of debug mode, the timing of all the functions that take more than 100ms will be printed on the log
