using DataFrames
using CSV

df = DataFrame(CSV.File("raw\\raw.csv")) 
municipalities = unique(df[:, "Municipality"])
