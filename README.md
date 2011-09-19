<h1>apdebug</hi>
<p>apdebug will help you troubleshoot issues with Apache (or any webserver for that matter), by making an HTTP request and automatically stracing the process which accepts the connection. This makes life easier for debugging purposes, especially in prefork mode where you have little control over which process receives your request. After the strace, apdebug will output the 5 longest system calls which were made during the request.</p>

<h3>Usage</h3>
<p>Currently, apdebug can only strace requests for the default Virtual Host, but I will be adding support for passing a host header in the short future.</p>
	./apdebug.py /url/to/debug.php

