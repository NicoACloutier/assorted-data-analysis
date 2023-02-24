#set this script to run once a month, it will update sqlite database with new data.

julia monthly_collect.jl #collect data
julia monthly_organize.jl #organize into dataframes
julia update_database.jl #write to sqlite db
