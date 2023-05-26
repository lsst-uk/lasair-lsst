# Configure the OpenStack Provider
terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
  cloud  = "openstack" # cloud defined in cloud.yml file
}

# base name for the deployment
variable "base_name" {
  type = string
}

# map defining the instances to deploy
variable "instances" {
  type = map(any)
}

# iterate over instances map
# create a node-set for each entry
module "node-set" {
  for_each = var.instances 
  source = "./modules/node-set"
  name = "${var.base_name}-${each.key}"
  number = can(each.value.number) ? each.value.number : 1
  root_vol_size = can(each.value.root_volume_size) ? each.value.root_volume_size : 25
  extra_vol = can(each.value.extra_volumes) ? each.value.extra_volumes : {}
#  extra_vol = {
#    tmp = {
#      size = 5
#      type = "ceph-ssd"
#    },
#    db = {
#      size = each.value.volume_size
#      type = "ceph-hdd"
#    }
#  }
}

