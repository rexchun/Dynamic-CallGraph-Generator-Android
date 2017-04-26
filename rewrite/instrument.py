#!/usr/bin/python
 # -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as ET
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')


PATH = os.path.abspath(os.path.dirname(__file__))
sign_tool_path = os.path.join(PATH, "tools", "sign.jar")
IR_Dir = os.path.join(PATH, "IR")
OUT_Dir = os.path.join(PATH, "out")
template_path = os.path.join(PATH, "template", "template_MainApp.smali")
tracking_method_template_path = os.path.join(PATH, "template", "template_startTracking_method.smali")

def mkdir(d):
	if not os.path.isdir(d):
		os.system("mkdir %s"%d)

def rm(d):
	if os.path.exists(d):
		os.system("rm -r %s"%d)


def signApk(apkpath):
	signedPath = apkpath[:len(apkpath) - 4] + ".s.apk"
	os.system("java -jar %s %s"%(sign_tool_path, apkpath))
	print "APK signed %s"%signedPath
	return signedPath

def decompile(apkpath):
	mkdir(IR_Dir)
	apkName = os.path.basename(apkpath)
	if apkName.endswith(".apk"):
		apkName = apkName[:len(apkName) - 4]
	decom_dir = os.path.join(IR_Dir, apkName)
	os.system("apktool d %s -f -o %s"%(apkpath, decom_dir))
	if not os.path.exists(decom_dir):
		errorDecompileHander(apkpath, decom_dir)

	print "Decomiled APK %s"%decom_dir
	return decom_dir

def errorDecompileHander(apkpath, decom_dir):
	print "Error in decompiling %s"%apkpath
	rm(decom_dir)
	sys.exit(-1)

def rewriteActivity(activityPath):
	fobj = open(activityPath, 'r')
	lines = fobj.readlines()
	fobj.close()

	hasonDestroy = False
	hasstopTracing = False
	inonDestroy = False
	hasVirtualMethods = False
	for l in lines:
		if l.find(".method") >= 0 and l.find("onDestroy()V") >= 0: 
			hasonDestroy = True
			inonDestroy = True
			hasVirtualMethods = True
		elif l.find(".end method") >= 0:
			if inonDestroy:
				inonDesrory = False
			else:
				continue
		elif l.find("invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V") >= 0:
			if inonDestroy:
				hasstopTracing = True
		elif l.find("# virtual methods") >= 0:
			hasVirtualMethods = True
	if hasonDestroy:
		if hasstopTracing:
			print "Nothing to do return"
			return 
		else:
			print "Add stopMethodTracing to onDestroy"
			with open(activityPath, 'w') as fobj:
				for l in lines:
					if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
						continue
					fobj.write(l)
					if l.find(".method") >= 0 and l.find("onDestroy()V") >= 0: 
						fobj.write("    invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V\n")

	else:
		print "Add the function onDestroy"
		with open(activityPath, 'w') as fobj:
			for l in lines:
				if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
					continue
				fobj.write(l)
			fobj.write("\n")
			if not hasVirtualMethods:
				fobj.write("# virtual methods\n")
			fobj.write(".method protected onDestroy()V\n")
			fobj.write("    .locals 0\n")
			fobj.write("    invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V\n")
			fobj.write("    invoke-super {p0}, Landroid/support/v7/app/AppCompatActivity;->onDestroy()V\n")
			fobj.write("    return-void\n")
			fobj.write(".end method\n")
	print "Finish rewrite %s"%activityPath


def rewriteApp(appPath, androidPath):
	fobj = open(appPath, 'r')
	lines = fobj.readlines()
	fobj.close()
	hasVirtualMethods = False
	hasonCreate = False
	for l in lines:
		if l.find("# virtual methods") >= 0:
			hasVirtualMethods = True
		elif l.find(".method") >= 0 and l.find("onCreate()V") >= 0: 
			hasVirtualMethods = True
			hasonCreate = True
	

	with open(appPath, 'w') as fobj:
		if hasonCreate:
			inonCreate = False
			
			for l in lines:
				if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
					continue

				if l.find(".method") >= 0 and l.find("onCreate()V") >= 0:
					inonCreate = True
				elif l.find(".end method") >= 0:
					if inonCreate:
						inonCreate = False
				if inonCreate and l.find("return-void") >= 0:
					print "In method onCreate(), inject call startTracking()"
					fobj.write("    invoke-virtual {p0}, %s;->startTracking()V\n"%androidPath)
				fobj.write(l)
			
		else:
			for l in lines:
				if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
					continue
				fobj.write(l)

			fobj.write("\n")
			if not hasVirtualMethods:
				fobj.write("# virtual methods\n")

			fobj.write(".method public onCreate()V\n")
			fobj.write("    .locals 0\n")
			fobj.write("    invoke-super {p0}, Landroid/app/Application;->onCreate()V\n")
			fobj.write("    invoke-virtual {p0}, %s;->startTracking()V\n"%androidPath)
			fobj.write("    return-void\n")
			fobj.write(".end method\n")
			print "Add the method onCreate()"
		template_lines = []
		with open(tracking_method_template_path, 'r') as template_object:
			template_lines = template_object.readlines()
		
		fobj.write("\n")
		for template_command in template_lines:
			if template_command.find("Lzyqu/com/boostdroid/MainAppClass") >= 0:
				template_command = template_command.replace("Lzyqu/com/boostdroid/MainAppClass", androidPath)
			fobj.write(template_command)



	print "Finish rewrite %s"%appPath


def rewrite(apkpath, decom_dir):
	manifest_path = os.path.join(decom_dir, "AndroidManifest.xml")
	if not os.path.exists(manifest_path):
		errorDecompileHander(apkpath, decom_dir)
	tree = ET.parse(manifest_path)
	xmlRoot = tree.getroot()

	if "package" not in xmlRoot.attrib:
		errorDecompileHander(apkpath, decom_dir)

	packageName = xmlRoot.attrib["package"]

	entryActivity = None
	applicationName = "%s.MainApp"%packageName
	hasAppComponentDeclared = False

	for child in xmlRoot:
		if child.tag != "application":
			continue
		if "{http://schemas.android.com/apk/res/android}name" in child.attrib:
			applicationName = child.attrib["{http://schemas.android.com/apk/res/android}name"]
			hasAppComponentDeclared = True
		else:
			child.set("{http://schemas.android.com/apk/res/android}name", applicationName)
			tree.write(manifest_path,encoding="UTF-8",xml_declaration=True)
			print "Add a new Application class in Manifest %s"%manifest_path
			hasAppComponentDeclared = False
		for component in child:
			if entryActivity != None:
				break
			if component.tag == "activity":
				for activityChild in component:
					if entryActivity != None:
						break
					if activityChild.tag == "intent-filter":
						numConditionsMeet = 0
						for filterChild in activityChild:
							if filterChild.tag == "action":
								if "{http://schemas.android.com/apk/res/android}name" in filterChild.attrib and filterChild.attrib["{http://schemas.android.com/apk/res/android}name"] == "android.intent.action.MAIN":
									numConditionsMeet += 1
							elif filterChild.tag == "category":
								if "{http://schemas.android.com/apk/res/android}name" in filterChild.attrib and filterChild.attrib["{http://schemas.android.com/apk/res/android}name"] == "android.intent.category.LAUNCHER":
									numConditionsMeet += 1
						if numConditionsMeet >= 2 and "{http://schemas.android.com/apk/res/android}name" in component.attrib:
							entryActivity = component.attrib["{http://schemas.android.com/apk/res/android}name"]
							break
		if entryActivity == None:
			errorDecompileHander(apkpath, decom_dir)

		entryActivityPath = os.path.join(decom_dir, "smali", "%s.smali"%entryActivity.replace(".","/"))
		rewriteActivity(entryActivityPath)

		applicationPath = os.path.join(decom_dir, "smali", "%s.smali"%applicationName.replace(".","/"))
		androidPath =  "L%s"%applicationName.replace(".","/")
		if not hasAppComponentDeclared:
			template_lines = []
			with open(template_path, "r") as fobj:
				template_lines = fobj.readlines()

			with open(applicationPath, "w") as fobj:
				
				for l in template_lines:
					if l.find("Llist/com/dynamicprofiledemo/MainApp") >= 0:
						l = l.replace("Llist/com/dynamicprofiledemo/MainApp", androidPath)
					elif l.startswith(".source"):
						l = ".source \"%s.java\""%os.path.basename(androidPath)
					fobj.write(l)
				print "Add smali file %s"%applicationPath
		else:
			rewriteApp(applicationPath, androidPath)
			








def reCompile(decom_dir):
	mkdir(OUT_Dir)
	apkName = os.path.basename(decom_dir)
	outPath = os.path.join(OUT_Dir, "%s_instrument.apk"%apkName)
	os.system("apktool b %s -f -o %s"%(decom_dir, outPath))
	print "Compile APK %s"%outPath
	return outPath


if __name__=="__main__":
	if len(sys.argv) != 2:
		print "python instrument.py path-to-input-apk"
		sys.exit(-1)
	apkpath = sys.argv[1]
	if not os.path.exists(apkpath):
		print "File %s not exisit"%apkpath
	decom_dir = decompile(apkpath)
	rewrite(apkpath, decom_dir)
	outAPKPath = reCompile(decom_dir)
	singedPath = signApk(outAPKPath)