resource "aws_dynamodb_table" "module_example" {
  name         = "module-example-table"
  billing_mode = "PAY_PER_REQUEST"
}
