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
  default = "lasair"
}

variable "security_groups" {
  type    = list(string)
  default = ["default"]
}

# name for the instance
variable "name" {
  type    = string
}

# UUID of the server group
variable "group_id" {
  type = string
}
