#!/usr/bin/python
 # -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as ET
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')


PATH = os.path.abspath(os.path.dirname(__file__))
sign_tool_path = os.path.join(PATH, "tools", "sign.jar")
IR_Dir = os.path.join(PATH, "IR")
OUT_Dir = os.path.join(PATH, "out")

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
	for l in lines:
		if l.find(".method") >= 0 and l.find("onDestroy()V") >= 0: 
			hasonDestroy = True
			inonDestroy = True
		elif l.find(".end method") >= 0:
			if inonDestroy:
				inonDesrory = False
			else:
				continue
		elif l.find("invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V") >= 0:
			if inonDestroy:
				hasstopTracing = True
	if hasonDestroy:
		if hasstopTracing:
			print "Nothing to do return"
			return 
		else:
			print "Add stopMethodTracing to onDestroy"
			fobj = open(activityPath, "w")
			for l in lines:
				if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
					continue
				fobj.write(l)
				if l.find(".method") >= 0 and l.find("onDestroy()V") >= 0: 
					fobj.write("    invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V\n")
			fobj.close()
	else:
		print "Add the function onDestroy"
		fobj = open(activityPath, "w")
		for l in lines:
			if l.find("Landroid/os/Debug;->stopMethodTracing") >= 0 or l.find("Landroid/os/Debug;->startMethodTracing") >= 0:
				continue
			fobj.write(l)
		fobj.write("\n")
		fobj.write(".method protected onDestroy()V\n")
		fobj.write("    .locals 0\n")
		fobj.write("    invoke-static {}, Landroid/os/Debug;->stopMethodTracing()V\n")
		fobj.write("    invoke-super {p0}, Landroid/support/v7/app/AppCompatActivity;->onDestroy()V\n")
		fobj.write("    return-void\n")
		fobj.write(".end method\n")
		fobj.close()
	print "Finish rewrite %s"%activityPath





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
			#tree.write(manifest_path,encoding="UTF-8",xml_declaration=True)
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




def reCompile(decom_dir):
	mkdir(OUT_Dir)
	apkName = os.path.basename(decom_dir)
	outPath = os.path.join(OUT_Dir, "%s_instrument.apk"%apkName)
	os.system("apktool b %s -f -o %s"%(decom_dir, outPath))
	print "Compile APK %s"%outPath
	return outPath


if __name__=="__main__":
	#apkpath = "app-release.apk"
	apkpath = "dynamicapp-release.apk"
	decom_dir = decompile(apkpath)
	rewrite(apkpath, decom_dir)
	outAPKPath = reCompile(decom_dir)
	singedPath = signApk(outAPKPath)