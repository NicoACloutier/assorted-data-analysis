using Statistics
using CSV
using DataFrames

function getinfo(collection)
	
end

df = DataFrame(CSV.read("data.csv"))
cities = names(df)
delete!(cities, "Date")

