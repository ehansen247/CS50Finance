## Introduction
Create an account, login, and start trading virtual stocks. Developed within Harvard's Introduction to Computer Science course, CS50 and adapted to make the project accessible outside of CS50's customized IDE. 

### Requisite Packages
The project is built off the Flask's lightweight but simple web framework.  

The requisite Flask files should be downloaded when the project is cloned but if not, follow the instructions to [download Flask](http://flask.pocoo.org/docs/1.0/installation/). 

You will also need to download the requests and flask_session modules, which are not build-in.   

Download requests:  
For OSX/Linux: 
```
sudo pip install requests
```  
For Windows:   
```
pip install requests
```

Download flask_session:    
```
pip install flask_session 
```


### Running the Project:
After cloning the project...
```
cd CS50Finance; cd flask; flask run
```

While running, the application will be accessible at http://127.0.0.1:5000/. 

### Troubleshooting:
  
1. ``` ModuleNotFoundError: No module named 'requests' or No module named 'flask_session' ```  
Requests and flask_session are not built-in to Flask. To download them, the instructions under the "Requisite Packages" header.  
  
2. ``` Error: Could not import "some_string". ```  
Check that you're current working directory is the flask folder within CS50Finance. [More information](http://flask.pocoo.org/docs/1.0/cli/).
For OSX/Linux:  
```
export FLASK_APP=app.py  
```
For Windows:  
```
set FLASK_APP=app.py  
```

