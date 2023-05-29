variable "keypair" {
  type    = string
  default = "gareth"   # name of keypair created
}

variable "flavor" {
  type    = string
  default = "tiny"
}

variable "root_vol_size" {
  type    = number
  default = 25
}

variable "extra_vol" {
  type    = map(object({
    size = string
    type = string
  }))
  default = {}
}

variable "network" {
  type    = string
  default = "lasair" # default network to be used
}

variable "security_groups" {
  type    = list(string)
  default = ["default"]  # Name of default security group
}

variable "name" {
  type    = string
}

variable "number" {
  type    = number
  default = 1
}

# UUID of the default servergroup to use for singleton instances
variable "default_group_id" {
  type = string
}

# Assign a floating IP
variable "floating_ip" {
  type = bool
  default = false
}

# Additional networks
variable "extra_networks" {
  type = list(string)
  default = []
}
