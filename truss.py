### Import libraries ### ----------------------------------------------------------------------
import pandas as pd
import numpy as np
from collections import Counter
import operator
import math
import matplotlib.pyplot as plt
from statistics import mean

### Load data ### ----------------------------------------------------------------------
elements = pd.read_excel("Data/Ex1.xlsx", "Element") # Truss elements
joints = pd.read_excel("Data/Ex1.xlsx", "Joint") # Truss joints

### Solve Reactions ### ----------------------------------------------------------------------

X_reactions = joints["RX"].tolist() # Reactions in X direction
Y_reactions = joints["RY"].tolist() # Reactions in y direction

x_index = [i for i, x in enumerate(X_reactions) if x == 1]	# Index for reactions in x
y_index = [i for i, x in enumerate(Y_reactions) if x == 1]	# Index for reactions in y

# Equations list 
if (len(x_index)) == 1: # 2 Rx and 1 Ry
	x_eq = [1, 0, 0]
	y_eq = [0, 1, 1]
else:					# 1 Rx and 1 Ry
	x_eq = [1, 1, 0]
	y_eq = [0, 0, 1]

X_values = [-i for i in joints["FX"].tolist()] # Value of the forces in x direction in the other side of =
Y_values = [-i for i in joints["FY"].tolist()] # Value of the forces in y direction in the other side of =

m_eq = [] # List to save Momentum equation

for i in x_index: # Reaction in X times Y distance to joint A: (0,0)
	m_eq.append(-X_reactions[i]*joints["Y"].tolist()[i])

for j in y_index: # Reaction in Y times X distance to joint A: (0,0)
	m_eq.append(Y_reactions[j]*joints["X"].tolist()[j])

M_F_X = [a*b for a, b in zip(joints["FX"].tolist(), joints["Y"].tolist())] # Momentum of FX forces in the other side of =
M_F_Y = [-a*b for a, b in zip(joints["FY"].tolist(), joints["X"].tolist())] # Momentum of Fxy Forces in the other side of =

a = np.array([x_eq, y_eq, m_eq]) # Left side of the equation system
b = np.array([sum(X_values), sum(Y_values), sum(M_F_Y) + sum(M_F_X)]) # Right side of the equation system

R = np.linalg.solve(a, b).tolist() # Reaction solutions R1, R2 and R3
print(a, b, R)

# Replace the reaction values in the dataframe
for i, val_x in enumerate(X_reactions):
	if val_x == 1: 
		X_reactions[i] = round(R[0], 2)
		R.pop(0)

for j, val_y in enumerate(Y_reactions):
	if val_y == 1: 
		Y_reactions[j] = round(R[0], 2)
		R.pop(0)

joints["RX"] = X_reactions
joints["RY"] = Y_reactions

joints.set_index("Joint", inplace = True)

### Solve Elements ### ----------------------------------------------------------------------

elements["Name"] = [a + b for a, b in zip(elements["Start"], elements["End"])] # Two letters name
elements["Value"] = [None]*len(elements) # Initial values

letters = Counter(elements["Start"].tolist() + elements["End"].tolist()) # Number of elements by joint

sorted_letters = sorted(letters.items(), key=operator.itemgetter(1)) # Sort the joints by number of elements

sorted_letters = [list(ele) for ele in sorted_letters] # list to tuples

while (None in elements["Value"].tolist()):

	joint = sorted_letters[0][0] # joint with least unkonws
	e_forces = [] # List to save the elements connected to the joint

	# Find the elements which are connected to the joint and also it's a unknown
	for i in range(len(elements)):
		if (joint in elements["Name"][i]) and elements["Value"][i] == None:
			e_forces.append(elements["Name"][i])

	# Find the angles for each element
	if len(e_forces) == 2:

		angles = []

		for point in e_forces:

			y = joints.loc[point.replace(joint,"")]["Y"] - joints.loc[joint]["Y"] # Y-component of position vector
			x = joints.loc[point.replace(joint,"")]["X"] - joints.loc[joint]["X"] # X-component of position vector

			if x < 0:
				angles.append(math.atan(y/x) + math.pi)

			elif x > 0:
				angles.append(math.atan(y/x))

			else:
				if y > 0:
					angles.append(math.pi/2)
				else:
					angles.append(-math.pi/2)

			# Reduce number of unknowns by joint
			for i in range(len(sorted_letters)):
				if point.replace(joint,"") == sorted_letters[i][0]:
					sorted_letters[i][1] -= 1

		
		# Left side of force equilibrium equations
		left_x = [math.cos(angles[0]), math.cos(angles[1])]
		left_y = [math.sin(angles[0]), math.sin(angles[1])]

		# Right side of force equilibrium equations
		right_x = -(joints.loc[joint]["RX"] + joints.loc[joint]["FX"])
		right_y = -(joints.loc[joint]["RY"] + joints.loc[joint]["FY"])
		
		a = np.array([left_x, left_y]) # Left side of the equation system
		b = np.array([right_x, right_y]) # Right side of the equation system

		R = np.linalg.solve(a, b).tolist() # Solution of forces
		result = R.copy()

		elements_forces = [tuple(x) for x in list(zip(e_forces, R))] # Tuple of element and its force

		for i in e_forces:
			for j, values in enumerate(elements["Name"].tolist()):
				if i == values:
					elements["Value"][j] = round(result[0], 2)
					result.pop(0)
	
	# Same that above but for joints with only 1 unknown
	else:

		angles = []
		y = joints.loc[e_forces[0].replace(joint,"")]["Y"] - joints.loc[joint]["Y"] 
		x = joints.loc[e_forces[0].replace(joint,"")]["X"] - joints.loc[joint]["X"]

		if x < 0:
			angles.append(math.atan(y/x) + math.pi)

		elif x > 0:
			angles.append(math.atan(y/x))

		else:
			if y > 0:
				angles.append(math.pi/2)
			else:
				angles.append(-math.pi/2)

		for i in range(len(sorted_letters)):
			if e_forces[0].replace(joint,"") == sorted_letters[i][0]:
				sorted_letters[i][1] -= 1

		if angles[0] == 0:

			a = np.array([[math.cos(angles[0])]]) # Left side of the equation system
			b = np.array([-(joints.loc[joint]["RX"] + joints.loc[joint]["FX"])]) # Right side of the equation system

			result = np.linalg.solve(a, b)[0] # Reaction solutions R1, R2 and R3

		else:
			a = np.array([[math.sin(angles[0])]]) # Left side of the equation system
			b = np.array([-(joints.loc[joint]["RY"] + joints.loc[joint]["FY"])]) # Right side of the equation system

			R = np.linalg.solve(a, b)[0] # Reaction solutions R1, R2 and R3
			result = R

			elements_forces = (e_forces[0], R)

		for j, values in enumerate(elements["Name"].tolist()):
				if e_forces[0] == values:
					elements["Value"][j] = round(result, 2)

	# Forces in X and Y for each joint
	FX_forces = joints["FX"].tolist()
	FY_forces = joints["FY"].tolist()
	
	# Add forces based on solve elements for each joints
	for point in e_forces:
		if len(e_forces) == 2:
			for i, j in enumerate(elements_forces):
				if point == j[0]:
					for k, ind in  enumerate(list(joints.index.values)):
						if point.replace(joint,"") == ind:
							FX_forces[k]= FX_forces[k]-(R[i]*math.cos(angles[i]))
							FY_forces[k]= FY_forces[k]-(R[i]*math.sin(angles[i]))

						
		else:
			for k, ind in  enumerate(list(joints.index.values)):
				if point.replace(joint,"") == ind:
					FX_forces[k]= FX_forces[k]-(R*math.cos(angles[0]))
					FY_forces[k]= FY_forces[k]-(R*math.sin(angles[0]))
				

	# Replace Forces in joint dataframe
	joints["FX"] = FX_forces
	joints["FY"] = FY_forces

	# Sort the list of joints again
	sorted_letters.pop(0)
	sorted_letters = sorted(sorted_letters, key=operator.itemgetter(1))
	

# joints[["RX", "RY"]].round(decimals = 2)
# elements["Value"].round(decimals = 2)

print(joints[["RX", "RY"]])
print(" ")
print(elements[["Name", "Value"]])


### Plot Truss + Results ### ----------------------------------------------------------------------


for i, name in enumerate(elements["Name"]):
	x_coord = [joints["X"][name[0]], joints["X"][name[1]]]
	y_coord = [joints["Y"][name[0]], joints["Y"][name[1]]]



	plt.plot(x_coord, y_coord, "ro-")
	plt.text(mean(x_coord), mean(y_coord), str(round(elements["Value"][i], 2)), fontsize=12)
	plt.text(x_coord[0], y_coord[0], name[0] , fontsize=12, color = "b", fontweight="bold")
	plt.text(x_coord[1], y_coord[1], name[1] , fontsize=12, color = "b", fontweight="bold")


plt.show()
