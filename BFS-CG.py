#!/usr/bin/python
import sys, os, json

DELIMIT = "----------------------------------------------------"
ENDSECTION = "======================================================================"

FULL_MODE = "full"
BFS_MODE = "bfs"

class Node():
	def __init__(self, methodId, sig):
		self.id = methodId
		self.sig = sig
		self.neighbourIds = []
	
	def toString(self):
		return  "%s\t%s\t%s"%(self.id, self.sig, self.neighbourIds)

class Graph():
	def parseChild(self, l):
		l = " ".join(l.split())
		tokens = l.split(" ")
		if tokens[0].find("%") >= 0:
			childId = tokens[1]
			childId = childId.replace("[", "")
			childId = childId.replace("]", "")
		elif tokens[0].find("[") >= 0:
			childId = tokens[0]
			childId = childId.replace("[", "")
			childId = childId.replace("]", "")			
		else:
			childId = None

		
		if len(tokens) == 7:
			childSig = "%s %s"%(tokens[4], tokens[5])
		elif len(tokens) == 6:
			childSig = "%s %s"%(tokens[3], tokens[4])
		elif len(tokens) == 3:
			childSig = childId 

		else:
			childSig = None

		return childId, childSig

	def parseNode(self, l):
		#print l
		l = " ".join(l.split())
		tokens = l.split(' ')
		res = []
		res.append(tokens[0])
		res[0] = res[0].replace('[', '')
		res[0] = res[0].replace(']','')

		if len(tokens) > 5:
			res.append("%s %s"%(tokens[4], tokens[5]))
		else:
			res.append("%s"%tokens[4])

		return res

	def __init__(self, inputFilePath, entryClass):
		self.nodeMap = {}
		self.rootId = None
		rootSig = "%s.onCreate (Landroid/os/Bundle;)V"%entryClass
		inSection = False
		curNode = None

		with open(inputFilePath, 'r') as fobj:
			lines = fobj.readlines()
			for index in range(len(lines)):
				l = lines[index]
				origL = l
				l = l.strip()
				if l == DELIMIT:
					if curNode != None:
						curNode.neighbourIds = list(set(curNode.neighbourIds))
						self.nodeMap[curNode.id] = curNode
						curNode = None
					inSection = True


				else:
					if not inSection:
						continue
					else:
						if l == ENDSECTION:
							if curNode != None:
								curNode.neighbourIds = list(set(curNode.neighbourIds))
								self.nodeMap[curNode.id] = curNode
								curNode = None
							inSection = False
							break
						else:
							if origL.startswith('['):
								tokens = self.parseNode(l)
								curNode = Node(tokens[0], tokens[1])
								if curNode.sig == rootSig:
									self.rootId = curNode.id
							else:
								if curNode != None:
									childId, childSig = self.parseChild(l)
									if childId != None and childSig != None:
										curNode.neighbourIds.append(childId)
										if childId not in self.nodeMap:
											self.nodeMap[childId] = Node(childId, childSig)






	def fullDump(self, outputPath):
		mapDict = {}
		numEdges = 0
		for nodeId in self.nodeMap:
			nodeSig = self.nodeMap[nodeId].sig
			neighbourIdLst = self.nodeMap[nodeId].neighbourIds
			tmpSet = set()
			if nodeSig in mapDict:
				tmpSet = mapDict[nodeSig]

			for neighbourID in neighbourIdLst:
				if neighbourID in self.nodeMap:
					neighbourSig = self.nodeMap[neighbourID].sig
					if neighbourSig not in tmpSet:
						tmpSet.add(neighbourSig)
						numEdges += 1
			mapDict[nodeSig] = tmpSet
		for key in mapDict:
			mapDict[key] = list(mapDict[key])
		with open(outputPath, 'w') as fobj:
			fobj.write(json.dumps(mapDict))
		print "Num Nodes: %s, Num Edges: %s"%(len(mapDict), numEdges)

	def bfs(self, outputPath):
		if self.rootId == None:
			print "Root node not found"
			sys.exit(-1)
		visited = set()
		numEdges = 0
		queue = []
		queue.append(self.rootId)
		mapDict = {}

		while len(queue) > 0:
			nodeId = queue.pop(0)
			visited.add(nodeId)
			nodeSig = self.nodeMap[nodeId].sig
			neighbourIdLst = self.nodeMap[nodeId].neighbourIds
			tmpSet = set()
			if nodeSig in mapDict:
				tmpSet = mapDict[nodeSig]

			for neighbourID in neighbourIdLst:
				if neighbourID in self.nodeMap:
					neighbourSig = self.nodeMap[neighbourID].sig
					if neighbourSig not in tmpSet:
						tmpSet.add(neighbourSig)
						numEdges += 1 

					if neighbourID not in visited and neighbourID not in queue:
						visited.add(neighbourID)
						queue.append(neighbourID)
			mapDict[nodeSig] = tmpSet

		for key in mapDict:
			mapDict[key] = list(mapDict[key])
		with open(outputPath, 'w') as fobj:
			fobj.write(json.dumps(mapDict))
		print "Num Nodes: %s, Num Edges: %s"%(len(mapDict), numEdges)


def exceptionHandler():
	print "python BFS-CG.py path-to-input-trace-file-dump mode[full/bfs] entry-class[required in bfs]"
	sys.exit(-1)	

def getAPKComponents(apkFilePath):
	if not os.path.isfile(apkFilePath):
		print "File not exist: %s"%apkFilePath
		sys.exit(-1)
	lines = os.popen("aapt dump xmltree %s AndroidManifest.xml"%apkFilePath).readlines()
	res = []
	entity = None
	for l in lines:
		l = l.strip()
		if entity != None and entity.lower() in ["activity", "service", "receiver","provider"]:
			if l.startswith("A: android:name"):
				name = l[l.find("\"")+1:]
				name = name[:name.find("\"")]
				#print name, entity
				res.append(name)
				entity = None
		else:
			if l.startswith("E:"):
				entity = l.split(" ")[1]


	res = list(set(res))
	return res

if __name__=="__main__":
	if len(sys.argv) < 4:
		exceptionHandler()
	else:
		inputPath = sys.argv[1]
		if not os.path.isfile(inputPath):
			print "File not exist: %s"%inputPath
			sys.exit(-1)

		mode = sys.argv[2]
		if mode == BFS_MODE:
			entryClass = sys.argv[3]
			graph = Graph(inputPath, entryClass)
			outputPath = "dynamic-cfg-%s-%s"%(os.path.basename(inputPath).replace(".trace.dump", ""), entryClass)
			graph.bfs(outputPath)
		elif mode == FULL_MODE:
			apkFilePath = sys.argv[3]
			componentLst = getAPKComponents(apkFilePath)
			for component in componentLst:
				print "Component %s"%component
				graph = Graph(inputPath, component)
				outputPath = "dynamic-cfg-%s-%s"%(os.path.basename(inputPath).replace(".trace.dump", ""), component)
				graph.fullDump(outputPath)
		else:
			exceptionHandler()

		
		


