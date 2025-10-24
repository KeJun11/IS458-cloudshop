output "table_names" {
  description = "Map of logical table keys to DynamoDB table names."
  value       = { for k, tbl in aws_dynamodb_table.this : k => tbl.name }
}

output "table_arns" {
  description = "Map of logical table keys to DynamoDB table ARNs."
  value       = { for k, tbl in aws_dynamodb_table.this : k => tbl.arn }
}

output "category_gsi_name" {
  description = "Name of the category secondary index."
  value       = [
    for gsi in aws_dynamodb_table.this["products"].global_secondary_index : gsi.name
    if gsi.hash_key == "category"
  ][0]
}
