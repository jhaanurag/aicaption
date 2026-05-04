- make a mvp backend
- multiple caption
- custom tones
- 


user:
'User' Entity Fields:
Id: Unique identifier.
Email id: Email ID of the user (must be unique system-wide).
First Name & Last Name
Role: Enum (ADMIN, USER)
Max AI Credits: Integer representing how many AI generations the user is allowed to perform.
Is Active: Boolean to activate/deactivate login access.


content: 'Content Request' Entity Fields:
Requested By: The User who generated the text.
Product Description: The original input.
Campaign Tone: The selected tone.
Generated Caption: The text output from the LLM.
Request Status: Status of the post (PENDING, APPROVED, REJECTED). Defaults to PENDING.
Request Reject Reason: Reason added by Admin upon rejection. Empty upon creation.
Created At: Timestamp.