package eunomia

default allow := false

allow if {
	input.principal.attributes.caller == "agent"
	input.resource.attributes.tool_name == "web_search"
	not any_prohibited_term_found
}

any_prohibited_term_found if {
	# Define your set of prohibited terms here
	prohibited_terms := ["fight", "blood", "gun"]

	some term in prohibited_terms
	contains(input.resource.attributes.query, term)
}