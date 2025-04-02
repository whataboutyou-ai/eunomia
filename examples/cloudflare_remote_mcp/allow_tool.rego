package eunomia

default allow := false

allow if {
    # Add email of users who should have access to the image generation tool
    allowed_emails := ["john.doe@example.com"]

	input.principal.attributes.email in allowed_emails
	input.resource.attributes.type == "tool"
	input.resource.attributes.name == "generateImage"
}
