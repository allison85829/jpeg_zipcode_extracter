# jpeg_zipcode_extracter

- "imggps.py" program take jpeg images as input and display the zipcode of the location where the images are taken. 
Return -1 if it couldn't find the zipcode or the type of file is not supported. 

- imggps.py only support jpeg with Exif application marker. 

- The program can take in multiples images as command line arguments at the same time.
eg: python3 imggps.py img1.jpg img2.jpg 

- The program can run on Linux, MacOS and Windows operating system. 
- There are instruction for setting up the required Python libraries code for each operating system. 

***********
Requirements:
- Need to have python3 installed 

MacOS:
1. Run macos_setup file 
```
chmod 777 macos_setup 
./macos_setup
```
2. Run the program 
```
python3 imggps.py img1.py img2.py 
````

Linux:
1. Run linux_setup file
```
chmod 777 linux_setup
./linux_setup 
```
2. Run the program 
```
python3 imggps.py img1.py img2.py
```

Windows:
1. Make sure the "get-pip.py" file is in the same folder as "windows_setup.bat" file. 
Double click on "windows_setup.bat" file to run the setup.
2. Open "Command Prompt" window
3. Go the folder where "imggps.py" located and run the program with the command. 
```
python imggps.py img1.py img2.py 
```

** For all of the operating system, replace img1.py and img2.py with images that you want to get zipcode for. It can run more than 2 images at the same time. **

********

There are a unittest file "test.py" and serveral images attached for testing. 

Possible improvement for readability:
- The code right now split into 2 cases for little endian and big endian format. Some of the code is repeated. Improve the repetition of code and readabilty can still be work on. 
