module "resources" {
  source = "./../../modules/resources"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}
