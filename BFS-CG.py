#!/usr/bin/python
import sys, os

DELIMIT = "----------------------------------------------------"
ENDSECTION = "======================================================================"

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
			res = tokens[1]
			res = res.replace("[", "")
			res = res.replace("]", "")
		elif tokens[0].find("[") >= 0:
			res = tokens[0]
			res = res.replace("[", "")
			res = res.replace("]", "")			
		else:
			res = None
		return res

	def parseNode(self, l):
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
									child = self.parseChild(l)
									if child != None:
										curNode.neighbourIds.append(child)









	def bfs(self, outputPath):
		if self.rootId == None:
			print "Root node not found"
			sys.exit(-1)
		visited = set()
		numNodes = 0
		numEdges = 0
		curLayer = []
		nextLayer = []
		curLayer.append(self.nodeMap[self.rootId])
		with open(outputPath, 'w') as fobj:
			while len(curLayer) > 0 or len(nextLayer) > 0:
				curNode = curLayer[0]
				curLayer.pop(0)
				visited.add(curNode.id)
				fobj.write("%s\n"%curNode.toString())
				numNodes += 1
				for childNodeId in curNode.neighbourIds:
					numEdges += 1
					if childNodeId in visited:
						continue
					else:
						visited.add(childNodeId)
						if childNodeId not in self.nodeMap:
							sysCallNode = Node(childNodeId, "")
							self.nodeMap[childNodeId] = sysCallNode
						
						nextLayer.append(self.nodeMap[childNodeId])
				if len(curLayer) == 0:
					curLayer = nextLayer
					nextLayer = []
					fobj.write("%s\n"%DELIMIT)
		print "Num Nodes: %s, Num Edges: %s"%(numNodes, numEdges)


if __name__=="__main__":
	if len(sys.argv) != 4:
		print "python BFS-CG.py path-to-input-trace-file-dump entry-class path-to-output"
		sys.exit(-1)
	else:
		inputPath = sys.argv[1]
		entryClass = sys.argv[2]
		outputPath = sys.argv[3]
		if not os.path.isfile(inputPath):
			print "%s not exist"%inputPath
			sys.exit(-1)

		graph = Graph(inputPath, entryClass)
		graph.bfs(outputPath)