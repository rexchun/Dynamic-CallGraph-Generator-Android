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

8       list.com.dynamicprofiledemo.MainActivity.onCreate (Landroid/os/Bundle;)V        ['1633', '14', '2343', '3942', '37', '112', '9', 'excl']
----------------------------------------------------
1633    android.support.v7.app.AppCompatActivity.findViewById (I)Landroid/view/View;    ['excl', '1694', '43']
14      android.support.v7.app.AppCompatActivity.setContentView (I)V    ['excl', '15', '43']
2343    android.view.View.setOnClickListener (Landroid/view/View$OnClickListener;)V     ['excl', '2279', '2505', '3765']
3942    list.com.dynamicprofiledemo.MainActivity$1.<init> (Llist/com/dynamicprofiledemo/MainActivity;)V ['excl', '355']
37      android.support.v7.app.AppCompatActivity.onCreate (Landroid/os/Bundle;)V        ['338', '43', '2854', '378', '2018', 'excl']
112     android.support.v7.app.AppCompatActivity.setSupportActionBar (Landroid/support/v7/widget/Toolbar;)V     ['excl', '43', '113']
9       java.lang.ClassLoader.loadClass (Ljava/lang/String;)Ljava/lang/Class;   ['10', 'excl']
excl            []
----------------------------------------------------
1694    android.support.v7.app.AppCompatDelegateImplV9.findViewById (I)Landroid/view/View;      ['excl', '53', '1453']
43      android.support.v7.app.AppCompatActivity.getDelegate ()Landroid/support/v7/app/AppCompatDelegate;       ['excl', '44']
15      android.support.v7.app.AppCompatDelegateImplV9.setContentView (I)V      ['2486', '18', '1330', '53', '3974', 'excl', '1406']
2279    android.view.View.setClickable (Z)V     ['487', 'excl']
2505    android.view.View.getListenerInfo ()Landroid/view/View$ListenerInfo;    ['excl', '3032']
3765    android.view.View.isClickable ()Z       ['excl']
355     java.lang.Object.<init> ()V     ['excl']
338     android.support.v7.app.AppCompatDelegateImplV9.installViewFactory ()V   ['excl', '4457', '503', '481', '1406']
2854    android.support.v7.app.AppCompatDelegateImplV14.applyDayNight ()Z       ['excl', '3613', '3499']
378     android.support.v7.app.AppCompatDelegateImplV14.onCreate (Landroid/os/Bundle;)V ['380', 'excl']
2018    android.support.v4.app.FragmentActivity.onCreate (Landroid/os/Bundle;)V ['3901', '3683', '3872', '2665', 'excl', '3162', '4375']
113     android.support.v7.app.AppCompatDelegateImplV9.setSupportActionBar (Landroid/support/v7/widget/Toolbar;)V       ['1544', '3928', '4424', '115', '3946', 'excl', '2497']
10      java.lang.ClassLoader.loadClass (Ljava/lang/String;Z)Ljava/lang/Class;  ['11', '10', '12', '57', '1845', '61', 'excl']
