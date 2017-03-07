# Dynamic-CallGraph-Generator-Android
Generate the Call Graph by Dynamic Analysis based on Android dmtracedump [https://developer.android.com/studio/profile/traceview.html#dmtracedump]

1. Usage scenario:
  This tool is able to automatically rewrite the input APK file so as to inject the DEBUG label. Based on the trace file, you can easily generate the call graph starting from any customized entry component (Activity, Service, Content Provider, Receiver). The flow across framework call back functions are captured.    

2. How to use:

  1.1 go to dir rewrite: cd rewrite, execute: python instrument.py path-to-input-apk. You will get rewritten APK file in dir out/ 
   
  1.2 Install and execute the app, manually or automatically with tools like monkey
  
  1.3 Collect the generated trace file from the phone: adb pull path-to-trace-file-on device, right now the file profile.trace is located in /data/data/appPackageName/files. You can run it on an emulator or a rooted Android phone. 
  
  1.4 Dump the trace file: dmtracedump -t 0 profile.trace > profile.trace.dump
  
  1.5 Generate the call graph: python BFS-CG.py profile.trace.dump[path-to-the-dumped-trace-file] "list.com.dynamicprofiledemo.MainActivity"[entry-class-name] callGraphMainActivity.txt[outputfile]

3. How to interpret the call graph (shown in layers by BFS):

  [id]  method signature [child methods's id]

  3.1 Sample:

    layer 0:

    13      list.com.dynamicprofiledemo.MainActivity.onCreate (Landroid/os/Bundle;)V        ['151', '3240', '1783', '62', '3535', '396', '134', '1717', '1813', '4723', '1111', '1953', 'excl', '14', '19', '3446', '5078', '52', '1366', '473', '824', '418', '2511']

    ----------------------------------------------------

    layer 1:

    151     android.support.v7.app.AppCompatActivity.setSupportActionBar (Landroid/support/v7/widget/Toolbar;)V     ['excl', '152', '58']

    3240    java.lang.Integer.valueOf (I)Ljava/lang/Integer;        ['excl', '4612']

    1783    android.support.v7.app.AppCompatActivity.findViewById (I)Landroid/view/View;    ['excl', '58', '1823']

    62      java.lang.Class.newInstance ()Ljava/lang/Object;        ['14', '3605', '1942', '4293', '4024', '127', 'excl']

    3535    java.lang.reflect.AccessibleObject.setAccessible (Z)V   ['excl']

    396     java.lang.Class.getDeclaredMethods ()[Ljava/lang/reflect/Method;        ['393', '3489', 'excl', '629']

    134     java.lang.String.equals (Ljava/lang/Object;)Z   ['excl', '189', '228']

    1717    java.lang.reflect.Method.invoke (Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;       ['1987', '2341', '3240', '865', 
    '5079', '4995', 'excl']


    1813    android.util.Log.d (Ljava/lang/String;Ljava/lang/String;)I      ['excl', '1904']

    4723    list.com.dynamicprofiledemo.MainActivity$1.<init> (Llist/com/dynamicprofiledemo/MainActivity;)V ['excl', '403']

    1111    java.lang.StringBuilder.<init> ()V      ['excl', '1401']

    1953    java.lang.StringBuilder.append (I)Ljava/lang/StringBuilder;     ['2014', 'excl']

    excl            []

    14      java.lang.ClassLoader.loadClass (Ljava/lang/String;)Ljava/lang/Class;   ['18', 'excl']

    19      android.support.v7.app.AppCompatActivity.setContentView (I)V    ['excl', '20', '58']

    3446    java.lang.Integer.toString ()Ljava/lang/String; ['3589', 'excl']

    5078    list.com.dynamicprofiledemo.MainActivity.divide (II)I   ['excl']

    layer 2:

    ...
