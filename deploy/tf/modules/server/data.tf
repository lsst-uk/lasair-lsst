# Data sources
## Get Image ID
data "openstack_images_image_v2" "image" {
  name        = "ubuntu-jammy" # Name of image to be used
  most_recent = true
}

## Get flavor id
data "openstack_compute_flavor_v2" "flavor" {
   name = var.flavor
#  name = "TestUtilityFlavor" # flavor to be used
}

## Get server group
#data "openstack_compute_servergroup_v2" "group" {
#  name = "var.group"
#}

