Warning: Invalid Attribute Combination

with aws_s3_bucket_lifecycle_configuration.invoice,
on main.tf line 99, in resource "aws_s3_bucket_lifecycle_configuration" "invoice":
99: resource "aws_s3_bucket_lifecycle_configuration" "invoice" {

No attribute specified when one (and only one) of [rule[0].filter,rule[0].prefix] is required

This will be an error in a future version of the provider

---

Error: Cannot index a set value

on ../../modules/dynamodb/outputs.tf line 13, in output "product_type_gsi_name":
13: value = aws_dynamodb_table.this["products"].global_secondary_index[0].name

Block type "global_secondary_index" is represented by a set of objects, and set elements do not have addressable
keys. To find elements matching specific criteria, use a "for" expression with an "if" clause.

---

Error: Unsupported attribute

on ../../modules/ses/main.tf line 6, in resource "aws_sesv2_email_identity_policy" "allow_ses":
6: email_identity = aws_ses_email_identity.this.email_identity

This object has no argument, nested block, or exported attribute named "email_identity".

Error: invalid value for statement_id (must contain alphanumeric, underscores or dashes only)
  with module.http_api.aws_lambda_permission.apigw["GET /products"],

Error: invalid value for statement_id (must contain alphanumeric, underscores or dashes only)
  with module.http_api.aws_lambda_permission.apigw["GET /products"],
  on ../../modules/apigw_http/main.tf line 67, in resource "aws_lambda_permission" "apigw":
  67:   statement_id  = "AllowExecutionFromAPIGateway-${replace(each.key, " ", "_")}"


Error: invalid value for statement_id (must contain alphanumeric, underscores or dashes only)

Error: invalid value for statement_id (must contain alphanumeric, underscores or dashes only)

   with module.http_api.aws_lambda_permission.apigw["GET /products"],
   with module.http_api.aws_lambda_permission.apigw["GET /products"],
   on ../../modules/apigw_http/main.tf line 67, in resource "aws_lambda_permission" "apigw":
   on ../../modules/apigw_http/main.tf line 67, in resource "aws_lambda_permission" "apigw":
   67:   statement_id  = "AllowExecutionFromAPIGateway-${replace(each.key, " ", "_")}"

   67:   statement_id  = "AllowExecutionFromAPIGateway-${replace(each.key, " ", "_")}"
