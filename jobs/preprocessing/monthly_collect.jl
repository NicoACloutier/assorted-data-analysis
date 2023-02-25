using HTTP
using Gumbo
using Cascadia
using CSV
using DataFrames
using Dates

#This script collects job data from job posting websites.
#Output dataframe:
#	raw.csv in the subdirectory data\raw of the project folder
#	it has five columns: the title, the company, the location,
#	the salary, and the date the collection script ran.

const DATA_DIR = "..\\data\\raw"

const COMPANY_SELECTOR = sel".d-flex.justify-content-between.align-items-start"
const TITLE_SELECTOR = sel".jobLink.css-1rd3saf.eigr9kq2"
const LOCATION_SELECTOR = sel".d-flex.flex-wrap.css-11d3uq0.e1rrn5ka2" 
const SALARY_SELECTOR = sel".d-flex.flex-wrap.css-1i7b5bu.e1rrn5ka1"

#summary information on a 
struct Page 
	title #the job title
	company #the company it's at
	location #the location of the job
	salary #the estimated salary
end

get_css(selector, webpage) = eachmatch(selector, webpage)[1][1][1] #get a single element with a selector
to_array(page) = [page.title, page.company, page.location, page.salary] #turn a page struct into an array

#parse a search response for all of its postings
function parse_page(http_response)
	pages = []
	page = parsehtml(String(http_response.body))
	all_selector = sel".d-flex.flex-column.pl-sm.css-3g3psg.css-1of6cnp.e1rrn5ka4"
	postings = eachmatch(all_selector, page.root)[2:end]
	
	for posting in postings
		push!(pages, parse_posting(posting))
	end
	pages
end

#parse a singular job posting for various pieces of information
function parse_posting(job_posting)
	company = get_css(COMPANY_SELECTOR, job_posting)
	company = match(r">(.+)\<", string(company)).captures[1]
	location = get_css(LOCATION_SELECTOR, job_posting)
	tester = eachmatch(TITLE_SELECTOR, job_posting)
	title = get_css(TITLE_SELECTOR, job_posting)
	
	try
		salary = get_css(SALARY_SELECTOR, job_posting)[1]
		return Page(title, company, location, salary)
	catch
		return Page(title, company, location, missing)
	end
end

function main()
	searches = ["scientist", "analyst", "engineer"]
	pages = []
	
	for search in searches
		response = HTTP.get("https://www.glassdoor.com/Job/data-$(search)-jobs-SRCH_KO0,14.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=data%2520$(search)")
		pages = cat(pages, parse_page(response); dims=1)
	end
	
	df = DataFrame(Title=[], Company=[], Location=[], Salary=[])
	
	for page in pages
		push!(df, to_array(page))
	end
	
	current_date = today()
	df = unique(df)
	df[!, "Date"] .= current_date
	
	CSV.write("$(DATA_DIR)\\raw.csv", df)
end

main()