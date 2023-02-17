using DataFrames
using CSV

function main()
	state_codes = DataFrame(CSV.File("..\\data\\raw\\states.csv"))
	locations = DataFrame(CSV.File("..\\data\\raw\\us-area-code-cities.csv"))
	
	code_dict = Dict(Pair.(state_codes[!, "State"], state_codes[!, "Abbr"]))
	locations[!, "State"] = map(x -> code_dict[x], locations[!, "State"])
	locations[!, "Town"] = map(x -> "$(x.Name), $(x.State)", eachrow(locations))
	
	output_df = DataFrame(Name=locations.Town, Latitude=locations.Latitude, Longitude=locations.Longitude)
	
	CSV.write("..\\data\\cleaned\\locations.csv", output_df)
end

main()
