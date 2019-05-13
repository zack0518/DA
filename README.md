# COMP90020 Distributed Algorithm - Bank Transaction System

USAGE:

### HTTP Web Server
The Web Server uses flask web framework. There are serveral options for user to deploy/run the appliation on their local development server. In default, the application has specified a app.run method to start the Server. On command line, simply `python3 server` or `nohup python3 server` to keep the server running on the background. The user can also specify the port by `python3 server port_number` for example `python3 server 20001` 

```
app.run(host, port, debug, options)
debug : defaults to false. If set to true, provides a debug information
options : to be forwarded to underlying Werkzeug server.
```
However, flask’s built-in server is not suitable for production as it doesn’t scale well. If user uses the hosted option to deploy the server for example Heroku, OpenShift, Google App Engine etc. Please refer the below link http://flask.pocoo.org/docs/1.0/deploying/ 

To run the client, open the browser then enter http://ip_address/http_port_number/index where ip_address and http port number can be obtained on the server console output. For example, http://127.0.0.1:8080/index will open the the home page of the website deployed on the local address with port number 8080.
