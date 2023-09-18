<h1> OPC UA Client</h1>
<p>This application implements a simple OPC UA client for testing the functionality of the server. The client functionality includes the ability to establish a connection with the server without using passwords or encryption, receive data from the server and select variables for monitoring</p>
<h2> How it works</h2>
<p>After running the main.exe file, the main application window will open:</p>
<img src="readme_img/main_window.png" width="450"/>
<p>To connect to the server, you must click "menu New" -> "Connect",a new window will open in which you need to enter the IP address of the device and click on the “Connect” button</p>
<img src="readme_img/connect_window.png" width="200"/>
<p>After a successful connection to the server, available server objects will appear in the tree window and a message about the successful connection will appear in the log window. In case of failure, a message about the reasons will also appear in the log.</p>
<p>In order to add a variable to the monitoring table, you need to right-click on it and select "add to list"
<br> In order to delete a variable from the monitoring table, you need to right-click on it in the table window and select "delete"</p>
<img src="readme_img/update_window.png" width="450"/>