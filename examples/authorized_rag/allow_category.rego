package eunomia

default allow := false

allow if {
	input.principal.attributes.department == "Financial Fraud"
	input.resource.attributes.category == "Online Financial Fraud"
}

allow if {
	input.principal.attributes.department == "Media Related Crime"
	input.resource.attributes.category == "Online and Social Media Related Crime"
}

allow if {
	input.principal.attributes.role == "Director"
}
