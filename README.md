# DEF/LEF Webviewer

## Description:<br/>
This project is part of the Digital Design2 Course in The American University in Cairo that converts DEF and LEF files to a corresponding Layout in SVG format.
This is a web application that receives the DEF and LEF file paths and displays the SVG output in the webviewer. 

## Webviewer Implemented Features: <br/>
• Zooming and Panning<br/>
• Hiding/Showing cell components and layers of Metals and vias<br/>
•A searchable list of all Nets where you can highlight<br/>
•A searchable list of all Cell Names where you can highlight cells by name <br/>
•A searchable list of all Cell Types where you can highlight cells by type <br/>
•A searchable list of all Pins where you can highlight<br/>
•Display the cell name when you hover over the cell<br/>
•Changing colours of Metals and vias<br/>

### Languages and Frameworks:<br/>
• Python<br/>
• Flask<br/>
• HTML<br/>
• CSS<br/>
• Javascript<br/>

### How to build and run:<br/>
•Clone repository and choose the path where you want to download the repo.<br/>
•Open the downloaded folder using Pycharm <br/>
•Configure python interpreter to python 3.7 <br/>
•Import Libraries: Flask, Matplotlib, drawSvg <br/>
•Add configuration - choose flask server - target type and choose app.py as your target <br/>
•Run program and open in local host <br/>
•Provide DEF, LEF and DRC (optionally) file paths respectively in the Home screen <br/>



### References:<br/>
https://github.com/ariutta/svg-pan-zoom<br/>
https://github.com/trimcao/lef-parser
