# apdebug
<p>apdebug will help you troubleshoot issues with Apache (or any webserver), by making an HTTP request and automatically stracing the process which accepts the connection. This makes life easier for debugging purposes, especially in prefork mode where you have little control over which process receives your request. After the strace, apdebug will output the 5 longest system calls which were made during the request.</p>

* * *

### Usage
<p>Currently, apdebug can only strace requests for the default Virtual Host, but support for passing host headers will be added in the near future.</p>
	./apdebug.py /url/to/debug.php

