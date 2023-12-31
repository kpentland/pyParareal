#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Here we provide code for the functions:
    CoarseSolver()         : the coarse solver used within Parareal.
    FineSolver()           : the fine solver used within Parareal.
    RungeKutta()           : an explicit Runge Kutta solver (user can select up to 8th order acurate).
    Parareal()             : a standard implementation of Parareal.
    
See "FHN_Test_serial.py" and "FHN_Test_parallel.py" for examples of how to run the code in 
serial and parallel mode respectively (similarly for the Lorenz63 example scripts). 

@author: kpentland
"""


import numpy as np
import multiprocessing as mp   # for parallel processing in Parareal
import os                      # for parallel processing in Parareal
import time                    # for timing in Parareal


"""
############# CoarseSolver/FineSolver(tspan, dt, u0, f, dense)

This is where we define our coarse/fine solvers to be used in Parareal.
 - in this case they call the RungeKutta method defined below, however, they
   can be replaced with any time-stepping method of choice (e.g. implicit methods). 
   It may require a slight alteration of the Parareal function below to ensure 
   inputs/outputs align.

Inputs:
tspan:       Time interval over which to integrate (i.e. [0,12])
dt:          Time step size taken within tspan
u0:          Initial condition at tspan[0] (i.e. [np.array[0,1])
f:           Function handle for ODE system to be solved                                               
dense:       Boolean that determines strucutre of output:
                    'False' returns solution t[1] only
                    'True' returns solution at all steps t[0]:dt:t[1]
                    
Outputs:
u:           Solution to ODE system at each time step (if dense = 'True') 
              or the final timestep 'tspan[1]' (if dense = 'False')
"""


# Define the coarse solver that you wish to use
def CoarseSolver(tspan, dt, u0, f, dense):
    u_end = RungeKutta(tspan = tspan, dt = dt, u0 = u0, f = f, method = 'RK2', dense = dense)
    return u_end

# Define the fine solver that you wish to use
def FineSolver(tspan, dt, u0, f, dense):
    u_end = RungeKutta(tspan = tspan, dt = dt, u0 = u0, f = f, method = 'RK4', dense = dense)
    return u_end



"""

############# RungeKutta(t, dt, u0, f, method, dense)

This function solves a system of first order ODEs using the explicit RK method. 

Inputs:
tspan:       Time interval over which to integrate (i.e. [0,12])
dt:          Time steps to take between t[0] and t[1] (i.e. dt = 0.25)
u0:          Initial condition at t[0] (i.e. [np.array[0,1])
f:           Function handle for ODE system to be solved
method:      Specify order of RK method (i.e. 'RKj' for j = 1,...,8)
dense:       Boolean that determines strucutre of output:
                    'False' returns solution t[1] only
                    'True' returns solution at all steps t[0]:dt:t[1]

Outputs:
u:           Solution to ODE system at each time step (depending on if dense = 'True' or 'False')

"""


def RungeKutta(tspan, dt, u0, f, method, dense):
    # Select the method to be used.
    if method == 'RK1':  # Euler's method
        a = np.array([0])
        b = np.array([1])
        c = np.array([0])
    elif method == 'RK2':  # midpoint method
        a = np.array([[0, 0], [0.5, 0]])
        b = np.array([0, 1])
        c = np.array([0, 0.5])
    elif method == 'RK3':  # Kutta's third-order method
        a = np.array([[0, 0, 0], [0.5, 0, 0], [-1, 2, 0]])
        b = np.array([1/6, 2/3, 1/6])
        c = np.array([0, 0.5, 1])
    elif method == 'RK4':  # classic fourth-order method
        a = np.array([[0, 0, 0, 0], [0.5, 0, 0, 0], [0, 0.5, 0, 0], [0, 0, 1, 0]])
        b = np.array([1/6, 1/3, 1/3, 1/6])
        c = np.array([0, 0.5, 0.5, 1])
    elif method == 'RK5':  # Butcher's fifth-order method
        a = np.array([[0, 0, 0, 0, 0, 0],
                      [0.25, 0, 0, 0, 0, 0],
                      [0.125, 0.125, 0, 0, 0, 0],
                      [0, 0, 0.5, 0, 0, 0],
                      [3/16, -3/8, 3/8, 9/16, 0, 0],
                      [-3/7, 8/7, 6/7, -12/7, 8/7, 0]])
        b = np.array([7, 0, 32, 12, 32, 7]) / 90
        c = np.array([0, 0.25, 0.25, 0.5, 0.75, 1])
    elif method == 'RK6':  # Butcher's sixth-order method
        a = np.array([[0, 0, 0, 0, 0, 0, 0],
                      [1/3, 0, 0, 0, 0, 0, 0],
                      [0, 2/3, 0, 0, 0, 0, 0],
                      [1/12, 1/3, -1/12, 0, 0, 0, 0],
                      [25/48, -55/24, 35/48, 15/8, 0, 0, 0],
                      [3/20, -11/24, -1/8, 1/2, 1/10, 0, 0],
                      [-261/260, 33/13, 43/156, -118/39, 32/195, 80/39, 0]])
        b = np.array([13/200, 0, 11/40, 11/40, 4/25, 4/25, 13/200])
        c = np.array([0, 1/3, 2/3, 1/3, 5/6, 1/6, 1])
    elif method == 'RK7':  # Butcher's seventh-order method
        a = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1/6, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 1/3, 0, 0, 0, 0, 0, 0, 0],
                      [1/8, 0, 3/8, 0, 0, 0, 0, 0, 0],
                      [148/1331, 0, 150/1331, -56/1331, 0, 0, 0, 0, 0],
                      [-404/243, 0, -170/27, 4024/1701, 10648/1701, 0, 0, 0, 0],
                      [2466/2401, 0, 1242/343, -19176/16807, -51909/16807, 1053/2401, 0, 0, 0],
                      [5/154, 0, 0, 96/539, -1815/20384, -405/2464, 49/1144, 0, 0],
                      [-113/32, 0, -195/22, 32/7, 29403/3584, -729/512, 1029/1408, 21/16, 0]])
        b = np.array([0, 0, 0, 32/105, 1771561/6289920, 243/2560, 16807/74880, 77/1440, 11/270])
        c = np.array([0, 1/6, 1/3, 1/2, 2/11, 2/3, 6/7, 0, 1])
    elif method == 'RK8':  # Cooper-Verner eigth-order method
        s = np.sqrt(21)
        a = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1/4, 1/4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1/7, (-7-3*s)/98, (21+5*s)/49, 0, 0, 0, 0, 0, 0, 0, 0],
                      [(11+s)/84, 0, (18+4*s)/63, (21-s)/252, 0, 0, 0, 0, 0, 0, 0],
                      [(5+s)/48, 0, (9+s)/36, (-231+14*s)/360, (63-7*s)/80, 0, 0, 0, 0, 0, 0],
                      [(10-s)/42, 0, (-432+92*s)/315, (633-145*s)/90, (-504+115*s)/70, (63-13*s)/35, 0, 0, 0, 0, 0],
                      [1/14, 0, 0, 0, (14-3*s)/126, (13-3*s)/63, 1/9, 0, 0, 0, 0],
                      [1/32, 0, 0, 0, (91-21*s)/576, 11/72, (-385-75*s)/1152, (63+13*s)/128, 0, 0, 0],
                      [1/14, 0, 0, 0, 1/9, (-733-147*s)/2205, (515+111*s)/504, (-51-11*s)/56, (132+28*s)/245, 0, 0],
                      [0, 0, 0, 0, (-42+7*s)/18, (-18+28*s)/45, (-273-53*s)/72, (301+53*s)/72, (28-28*s)/45, (49-7*s)/18, 0]])
        b = np.array([1/20, 0, 0, 0, 0, 0, 0, 49/180, 16/45, 49/180, 1/20])
        c = np.array([0, 1/2, 1/2, (7+s)/14, (7+s)/14, 1/2, (7-s)/14, (7-s)/14, 1/2, (7+s)/14, 1])
    else:
        print('Error: Please define the Runge Kutta method.')
        return

    # SOLVING THE EQUATIONS.

    num_time_steps = int((tspan[-1] - tspan[0]) / dt)+1
        
    if dense == False:
        
        # Iterate over each time step explicitly (only returning the solution at tspan[1])
        un = u0
        for n in range(num_time_steps-1):
            # This function carries out the iterative step of a general form
            # of the Runge-Kutta method with inputs: (time step, initial time,
            # initial condition, function, coefficient matrices).
    
            tn = tspan[0] + n*dt
            dim = len(u0)  # dimension of the ODE problem
            S = len(b)  # order of the RK method
            k = np.zeros((dim, S))  # matrix for other k values
            k[:, 0] = dt*f(tn, un)  # definition of k1
    
            # calculate the coefficients k
            for i in range(1, S):
                temp = np.zeros(dim)
                for j in range(i):
                    temp +=  a[i, j] * k[:, j]
                k[:, i] = dt*f(tn + (c[i]*dt), un + temp)
    
            # calculate the final solution
            un += np.sum(b * k, axis=1)
        u = un
        
    elif dense == True:

        # Iterate over each time step explicitly (returning the solution at all timesteps)
        un = np.zeros((num_time_steps,len(u0)))
        un[0,:] = u0
        for n in range(num_time_steps-1):
            # This function carries out the iterative step of a general form
            # of the Runge-Kutta method with inputs: (time step, initial time,
            # initial condition, function, coefficient matrices).
    
            tn = tspan[0] + n*dt
            dim = len(u0)  # dimension of the ODE problem
            S = len(b)  # order of the RK method 
            k = np.zeros((dim, S))  # matrix for other k values
            k[:, 0] = dt*f(tn, un[n,:])  # definition of k1
    
            # calculate the coefficients k
            for i in range(1, S):
                temp = np.zeros(dim)
                for j in range(i):
                    temp +=  a[i, j] * k[:, j]
                k[:, i] = dt*f(tn + (c[i]*dt), un[n,:] + temp)
    
            # calculate the final solution
            un[n+1,:] = un[n,:] + np.sum(b * k, axis=1)
        u = un
    else:
        print('Error: Please define dense = ''True'' or ''False''.')
        return
    
    return u





"""
############# Parareal(f,tspan,u0,N,Ng,Nf,epsilon,parallel)

This function implements the parareal alogrithm for a system of first
order ODEs.

Inputs:
f:           Function handle for ODE system to be solved
tspan:       Time interval over which to integrate (i.e. [0,12])
u0:          Initial condition at tspan[0] (i.e. [np.array[0,1])
N:           Number of 'processors' (temporal sub-intervals) (i.e. N = 40)
Ng:          Number of coarse time steps (i.e. Ng = 40)
Nf:          Number of fine times steps (i.e. Nf = 4000)
epsilon:     Error tolerance (i.e. 1e-6
parallel:    Boolean that determines if fine solver is run in parallel or not ('True' or 'False')

Outputs:
t:           Array of time sub-intervals (at which solutions located)
u:           Solution to ODE system on the mesh given by 't' (dimension = dim(t) x (dim(ODE system) x k))
diagnostics: Dictionary of useful diagnostics which can be expanded by user if needed (see below for current keys/values)
    'Iterations': k,                # iterations until stopping tolerance reached
    'Errors': err[:, :k],           # errors at each successive iterations (dimension = dim(t) x k)
    'Parareal Timing': timePara,    # total Parareal wallclock time
    'F Timings': timesF[:,0:k+1],   # fine solver wallclock times (dimension = time slice x iteration)
    'G Timings': timesG[:,0:k+1],   # coarse solver wallclock times (dimension = time slice x iteration)
    'Slices': slices[0:k+1],        # integers detailing how many unconverged slices there were each iteration
}
    
"""


def Parareal(f,tspan,u0,N,Ng,Nf,epsilon,parallel):

    # start timing 
    timePara0 = time.time()

    # INITIALIZATION
    
    n = len(u0)                                       # Dimension of the ODE system
    L = tspan[1] - tspan[0]                           # Length of the interval
    L_sub = L / N                                     # Length of sub-interval
    dT = L / Ng                                       # Coarse time step
    dt = L / Nf                                       # Fine time step
    t = np.arange(tspan[0], tspan[1] + L_sub, L_sub)  # Time sub-intervals (the mesh)
    I = 0                                             # Counter for how many intervals have converged
    
    
    # Error catch: sub-interval, coarse, and fine time steps must be multiples of each other
    if Ng % N != 0 or Nf % Ng != 0:
        print("Nf must be a multiple of Ng and Ng must be a multiple of N - change time steps!")
        return
    
    
    # Solution storage matrices (sub-interval mesh x system dimension * iterations)
    u = np.full((N + 1, n * (N + 1)), np.nan)   # Predictor-corrected (refined) solutions
    uG = np.full((N + 1, n * (N + 1)), np.nan)  # Coarse solutions
    uF = np.full((N + 1, n * (N + 1)), np.nan)  # Fine solutions
    err = np.full((N + 1, N), np.nan)           # Successive errors
    
    # Pre-set the exact initial condition at the start of each iteration
    u[0, :] = np.tile(u0, N + 1)
    uG[0, :] = u[0, :]
    uF[0, :] = u[0, :]
    
    # diagnostics storage matrices and unconverged time slice counter
    timesG = np.zeros((N, N+1))
    timesF = np.zeros((N, N+1))
    slices = np.zeros(N+1)
    slices[0] = N
    
    
    # PARAREAL ALGORITHM
    
    # Step 1 (k = 0): Use G (coarse solver) to find approximate initial conditions
    for i in range(0,N):
        timeG0 = time.time()          # start timer
        temp = CoarseSolver(tspan = [t[i], t[i+1]], dt = dT, u0 = np.copy(uG[i,0:n]), f = f, dense = False) # run coarse solver
        uG[i+1, 0:n] = temp           # store solutions
        u[i+1, 0:n] = temp
        
        timeG1 = time.time()          # end timer
        timesG[i,0] = timeG1 - timeG0 # store timing
        
        

    # Step 2 (k > 0): Use F (fine solver) in parallel using current best initial
    # conditions and update using the predictor-corrector formula
    for k in range(1, N + 1):
        
        
        # give an indication as to which iteration we're at for the console
        if k == 1:
            print(f'Parareal iteration number (out of {N}): 1 ', end='')
        elif k == N:
            print(f'{N}.')
        else:
            print(f'{k} ', end='')
    
        # set current indices for solution storage
        dim_indices = slice(n * (k - 1), n * k)       # current indices
        dim_indices_next = slice(n * k, n * (k + 1))  # next indices

        # use the previously found (or updated) initial conditions and
        # solve with the fine solver (in parallel if 'parallel = True')
        if parallel == False:
            
            for i in range(I, N):
                timeF0 = time.time()            # start timer
                temp = FineSolver(tspan = [t[i], t[i+1]], dt = dt, u0 = np.copy(u[i, dim_indices]), f = f, dense = False) # run fine solver
                uF[i+1, dim_indices] = temp     # store solutions
                timeF1 = time.time()            # end timer
                timesF[i,k] = timeF1 - timeF0   # store timing
                
        elif parallel == True:
            timeF0 = time.time()                        # start timer
            inputs = [([t[i], t[i+1]], dt, np.copy(u[i, dim_indices]), f, False) for i in range(I, N)]  # set up inputs for each processor

            # carry out parallel solves 
            # (requires N processors but will run on one less than the number of cores available on current machine if not)
            num_cores = min(os.cpu_count()-1,N)
            with mp.Pool(processes = num_cores) as pool:
                results = pool.starmap(FineSolver, inputs)
        
            uF[I+1:, dim_indices] = np.vstack(results)  # store solutions
            timeF1 = time.time()                        # end timer
            timesF[i,k] = timeF1 - timeF0               # store timing
        
        else:
            print('Error: Please define parallel = ''True'' or ''False''.')
            return
    
    

        # Predictor-corrector step (for each sub-interval serially)
        for i in range(I, N):
            
            timeG0 = time.time()               # start timer

            # First need to find uG for the next iteration step using the coarse solver
            temp = CoarseSolver(tspan = [t[i], t[i+1]], dt = dT, u0 = np.copy(u[i, dim_indices_next]), f = f, dense = False) # run coarse solver
            uG[i+1, dim_indices_next] = temp  # store solutions
            timeG1 = time.time()              # stop timer
            timesG[i,k] = timeG1 - timeG0     # store timing
            
            # Do the predictor-corrector step and save the final solution value
            u[i + 1, dim_indices_next] = uG[i + 1, dim_indices_next] + uF[i + 1, dim_indices] - uG[i + 1, dim_indices]
            
    
        # error catch (to catch any solutions that blow up - means coarse solver is likely unstable)
        a = 0
        if np.isnan(uG[:, dim_indices_next]).any():
            a = np.nan
            break
            

        
        # CONVERGENCE CHECKS
        # if an error is small enough up to a certain time interval, all solutions are saved and the
        # next k considers only unconverged chunks (can use different criteria if needed)
        err[:, k - 1] = np.linalg.norm(u[:, dim_indices_next] - u[:, dim_indices], ord=np.inf, axis=1)
    
        II = I
        for p in range(II, N):
            if p == II:
                # we know I is now converged so we copy solutions to all future k
                u[p + 1, (n*(k + 1)):] = np.tile(u[p + 1, dim_indices_next], N - k)
                uG[p + 1, (n*(k + 1)):] = np.tile(uG[p + 1, dim_indices_next], N - k)
                uF[p + 1, (n*k):] = np.tile(uF[p + 1, dim_indices], N - k + 1)
                I = I + 1
            elif p > II:
                if err[p, k-1] < epsilon:
                    # If further intervals beyond I are converged, we can copy solutions to all future k
                    u[p + 1, (n*(k + 1)):] = np.tile(u[p + 1, dim_indices_next], N - k)
                    uG[p + 1, (n*(k + 1)):] = np.tile(uG[p + 1, dim_indices_next], N - k)
                    uF[p + 1, (n*k):] = np.tile(uF[p + 1, dim_indices], N - k + 1)
                    I = I + 1
                else:
                    break

        slices[k] = N - I;  # sotre how many slices remain unconverged

        # break the parareal iteration if solutions at all time steps have converged
        if I == N:
            break
    
    # Output the matrix containing the solutions after 1, 2, 3...k iterations
    u = u[:, n:n*(k + 1)]
    
    # Error catch
    if np.isnan(a):
        k = np.nan
        print("Parareal crashed...perhaps coarse solver is too coarse!")
    
                 
    
    # stop timing
    timePara1 = time.time()
    timePara = timePara1 - timePara0
    
    # store the diagnostic information
    diagnostics = {
        'Iterations': k,                # iterations until stopping tolerance reached
        'Errors': err[:, :k],           # errors at each successive iterations
        'Parareal Timing': timePara,    # total Parareal wallclock time
        'F Timings': timesF[:,0:k+1],   # fine solver wallclock times (slices x iteration)
        'G Timings': timesG[:,0:k+1],   # coarse solver wallclock times (slices x iteration)
        'Slices': slices[0:k+1],        # integers detailing how many unconverged slices were there each iteration
    }
    
    print('Done.')

    return t, u, diagnostics





