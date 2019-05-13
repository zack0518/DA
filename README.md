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
