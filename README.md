# Dynamic-CallGraph-Generator-Android
Generate the Call Graph by Dynamic Analysis based on Android dmtracedump [https://developer.android.com/studio/profile/traceview.html#dmtracedump]

Usage scenario:
Based on the trace file, you can easily generate the call graph starting from any customized entry component (Activity, Service, Content Provider, Receiver).You do not need to instrument the app or OS. The flow across framework call back functions are captured.    

How to use:
  Set up the start/end point of dynamic analysis with Debug.startMethodTracing() and Debug.stopMethodTracing() in the Android source code, e.g. onCreate(), onDestory() of an Activity.
  Execute the app, manually or automatically with tools like monkey
  Collect the generated trace file from the phone: adb pull path-to-trace-file-on device
  Dump the trace file: dmtracedump -t 0 profile.trace > profile.trace.dump
  Generate the call graph: python BFS-CG.py profile.trace.dump[path-to-the-dumped-trace-file] "list.com.dynamicprofiledemo.MainActivity"[entry-class-name] callGraph.txt[outputfile]

How to interpret the call graph (shown in layers by BFS):
[id]  method signature [child methods's id]


Layer 0:

8 list.com.dynamicprofiledemo.MainActivity.onCreate (Landroid/os/Bundle;)V ['1633', '14', '2343', '3942', '37', '112', '9', 'excl']

----------------------------------------------------
Layer 1:

1633 android.support.v7.app.AppCompatActivity.findViewById (I)Landroid/view/View;    ['excl', '1694', '43']

14 android.support.v7.app.AppCompatActivity.setContentView (I)V    ['excl', '15', '43']

2343 android.view.View.setOnClickListener (Landroid/view/View$OnClickListener;)V     ['excl', '2279', '2505', '3765']

3942 list.com.dynamicprofiledemo.MainActivity$1.<init> (Llist/com/dynamicprofiledemo/MainActivity;)V ['excl', '355']

37 android.support.v7.app.AppCompatActivity.onCreate (Landroid/os/Bundle;)V        ['338', '43', '2854', '378', '2018', 'excl']

112 android.support.v7.app.AppCompatActivity.setSupportActionBar (Landroid/support/v7/widget/Toolbar;)V     ['excl', '43', '113']

9 java.lang.ClassLoader.loadClass (Ljava/lang/String;)Ljava/lang/Class;   ['10', 'excl']

----------------------------------------------------
Layer 2:

.....

