# apdebug - Webserver Debugging Toolkit

apdebug will help you troubleshoot issues with Apache (or any webserver), by making an HTTP request and automatically stracing the process which accepts the connection. This makes life easier for debugging purposes, especially in prefork mode where you have little control over which process receives your request. After the strace, apdebug will output the 5 longest system calls which were made during the request.

* * *

### Usage

**Note:** Keep-Alives must be enabled on your webserver in order to grab the correct PID to strace.

Because the features of apdebug analyze system calls and configurations, all interactions are meant to take place local to the webserver with root-level privileges. However, for the sake of simplicity, you can still pass the URLs as example.com/pagetotest.php instead of localhost/pagetotest.php. apdebug will simply connect to localhost and pass the example.com Host header when making the request. Check out the examples below for a better idea of what you can do.

##### Examples

```# python apdebug.py example.com/debugme.php```

On an alternate port:

```# python apdebug.py example.com:8080/debugme.php```

