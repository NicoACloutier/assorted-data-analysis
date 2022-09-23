using Statistics
using CSV
using DataFrames

getinfo(name, collection) = (name, mean(collection), length(collection), std(collection))

df = DataFrame(CSV.File("data.csv"))
cities = names(df)
deleteat!(cities, 1)
cityinfo = [getinfo(city, df[:, city]) for city in cities]
df = DataFrame(Name=[], Mean=[], Length=[], Standard_Deviation=[])

for city in cityinfo
	push!(df, city)
end

CSV.write("stats.csv", df)
