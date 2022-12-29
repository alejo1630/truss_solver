# Truss Solver

This Python code solves any 2D truss structure using the joints method.

## 🔰 How does it work?
*In order to explain the code, it was used for solving the following truss structure (Engineering Mechanics: Statics. Bedford & Fowler - Problem 6.7)*

 <img src = "https://github.com/alejo1630/truss_solver/blob/main/Image_Readme/1.png" width="500">

- The data is uploaded from an excel file with two main sheets
  - **Element** Sheet shows the start and end joints for each element
  
  <img src = "https://github.com/alejo1630/truss_solver/blob/main/Image_Readme/2.png" width="200">
  
  - **Joint** Sheet shows information such as:
    - X, Y coodinates for each joint.
    - Rx, Ry represents the support reactions. If there are 1 in both columns that joint is a pinned support. If just one column has 1 that joint is a roller support.
    - Fx, Fy represents the forces in X and Y direction for each joint.
    
    <img src = "https://github.com/alejo1630/truss_solver/blob/main/Image_Readme/3.png" width="400">

- In the first part of the code the support reactions are solved using the equilibrium equations for 2D structures:

$$ \Sigma F_x = 0 $$

$$ \Sigma F_y = 0 $$

$$ \Sigma M = 0 $$

- After that, all the joints are sorted based on the unknown values.
- The solution process starts with the joints with less unknowns (1 or 2) and uses the equilibrium equations for joints.

$$ \Sigma F_x = 0 $$

$$ \Sigma F_y = 0 $$

- The equation system is solved using the [linalg](https://numpy.org/doc/stable/reference/routines.linalg.html) function from numpy
- The quantity of unknowns are updated after solve a joint. The above process is repeated until all the joints are solved.
- Finally, a line-plot with the internal load of each element (in tension[+] or compression[-]) is shown.

<img src = "https://github.com/alejo1630/truss_solver/blob/main/Image_Readme/5.png" width="600">

- A solution of this example truss obtained using the software [MDSolid](https://web.mst.edu/~mdsolids/) is shown below.

<img src = "https://github.com/alejo1630/truss_solver/blob/main/Image_Readme/4.png" width="600">

    
## 🔶 What is next?

- Load tha truss data using a grid and straight lines drawn with mouse.
