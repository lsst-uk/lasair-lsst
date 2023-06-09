locals {
  group = var.name
}

# create a servergroup only if we have multiple instances
resource "openstack_compute_servergroup_v2" "group" {
  count = (var.number > 1) ? 1 : 0
  name     = local.group
  policies = ["soft-anti-affinity"]
}

module "server" {
  source    = "../server"
  count     = var.number
  name      = (var.number > 1) ? "${var.name}-${count.index}" : var.name
  root_vol_size = var.root_vol_size
  extra_vol = var.extra_vol
  group_id  = (var.number > 1) ? openstack_compute_servergroup_v2.group[0].id : var.default_group_id
  floating_ip = var.floating_ip
  extra_networks = var.extra_networks
  flavor = var.flavor
  image_name = var.image_name
}

output "private_ips" {
  value = [ for server in module.server : {
    name = server.name
    address = server.private_ip
  } ]
}
