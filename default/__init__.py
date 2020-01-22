import sys, os
cwd = os.getcwd()
parentcwd = os.path.dirname(cwd)
sys.path.append(cwd)
sys.path.append(parentcwd)
print(sys.path)
