"""Configuration for LDAP agent."""

LDAP_SERVER = "172.27.1.132"
LDAP_PORT = 1389  # default LDAP is 389; adjust if needed
BASE_DN = "ou=people,dc=example,dc=com"
BIND_DN = "cn=admin,dc=example,dc=com"  # account with write permissions
BIND_PASSWORD = "adminpass"
