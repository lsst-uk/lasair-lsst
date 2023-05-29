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

# Get extra network ids
data "openstack_networking_network_v2" "extra_networks" {
  count = length(var.extra_networks)
  name = var.extra_networks[count.index]
}
