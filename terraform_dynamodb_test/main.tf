resource "aws_dynamodb_table" "example" {
  name         = "outra_tabela"
  billing_mode = "PAY_PER_REQUEST"
}
