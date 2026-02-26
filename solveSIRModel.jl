using DifferentialEquations
using Plots
import CSV
using DataFrames

#== 
# Write the ODE in-place for performance benefits:
# https://docs.sciml.ai/DiffEqDocs/stable/getting_started/#Example-2:-Solving-Systems-of-Equations
# du: output array containing [ dS, dI, dR]
# u: initial conditions [ S, I, R ]
# p: parameters [ beta, gamma, N ]
# t: time 
==#

function sirModel!(du, u, p, t)


    S, I, R = u
    Beta, Gamma, N = p

    # dS
    du[1] = -Beta * S * I / N

    # dI
    du[2] = Beta * S * I / N - Gamma * I

    # dR
    du[3] = Gamma * I
end

function solveSIRModel()

    println("Plots check: $(isdefined(Plots, :plot!))") 

    inputFile = "SIR_init_conditions.csv"
    faasr_get_file(inputFile, inputFile) 

    # Expecting columns: beta, gamma, N, S0, I0, R0, tmax
    data = CSV.read(inputFile, DataFrame)
    Beta = data.beta[1]
    Gamma = data.gamma[1]
    N = data.N[1]
    S0 = data.S0[1]
    I0 = data.I0[1]
    R0 = data.R0[1]
    tmax = data.tmax[1]    

    # Basic reproduction number
    R_null = Beta / Gamma

    u0 = [S0, I0, R0]
    tspan = (0.0, tmax)
    p = (Beta, Gamma, N)

    prob = ODEProblem(sirModel!, u0, tspan, p)
    sol = solve(prob, Tsit5())

    t = sol.t
    S = [u[1] for u in sol.u]
    I = [u[2] for u in sol.u]
    R = [u[3] for u in sol.u]

    out_df = DataFrame(
        time = t,
        S = S,
        I = I,
        R = R
    )

    outName = "sir_output.csv"
    CSV.write(outName, out_df)
    faasr_put_file(outName, outName)


end

#solveSIRModel()

