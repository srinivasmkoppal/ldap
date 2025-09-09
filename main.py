"""Example CLI for authenticating SONiC users via LDAP."""

import getpass
import sys

from ldap_agent import LDAPAgent
import config


def main() -> int:
    uid = input("Username: ")
    password = getpass.getpass("Password: ")

    agent = LDAPAgent(config.LDAP_SERVER, port=config.LDAP_PORT, base_dn=config.BASE_DN)
    ok = agent.authenticate_user(uid, password)

    if ok:
        print("✅ Authentication successful")
        return 0
    else:
        print("❌ Authentication failed")
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
