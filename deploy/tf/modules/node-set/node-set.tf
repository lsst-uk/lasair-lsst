module "server" {
  source    = "../server"
  count     = var.number
  name      = (var.number > 1) ? "${var.name}-${count.index}" : var.name
  root_vol_size = var.root_vol_size
  extra_vol = var.extra_vol
}
