# Dynamic-CallGraph-Generator-Android
Generate the Call Graph by Dynamic Analysis based on Android dmtracedump [https://developer.android.com/studio/profile/traceview.html#dmtracedump]

0. Dependencies:
	Apktool [https://ibotpeaches.github.io/Apktool/]

	aapt under Android sdk build-tools, remember to setup the environment variables

1. Usage scenario:
  This tool is able to automatically rewrite the input APK file so as to inject the DEBUG label. Based on the trace file, you can easily     
    1.1 Generate the call graph starting from any customized entry component (Activity, Service, Content Provider, Receiver) 
  
    1.2 Generate the complete call graph from the dynamic analysis
  
  The flow across framework call back functions are captured.    

2. How to use:

    2.1 go to dir rewrite: cd rewrite, execute: python instrument.py path-to-input-apk. You will get rewritten APK file in dir out/ 
   
    2.2 Install and execute the app, manually or automatically with tools like monkey
  
    2.3 Collect the generated trace file from the phone: adb pull path-to-trace-file-on device, right now the file profile.trace is located in /data/data/appPackageName/files. You can run it on an emulator or a rooted Android phone. 
  
    2.4 Dump the trace file: dmtracedump -t 0 profile.trace > profile.trace.dump
  
    2.5 Generate the call graph: python BFS-CG.py profile.trace.dump[path-to-the-dumped-trace-file] full/bfs[mode] "zyqu.com.boostdroid.MainActivity"[entry-class-name, required in BFS mode] 

3. The output is organized as Map(Node, Set(Node)), where key is the source node and value is the set of neighbors
