module "resources" {
  source = "./../../modules/service"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}
