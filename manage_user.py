"""CLI tool for managing LDAP users (add/get/update/delete)."""

import argparse
import getpass

import config
from ldap_agent import LDAPAgent


def build_agent() -> LDAPAgent:
    return LDAPAgent(
        config.LDAP_SERVER,
        port=config.LDAP_PORT,
        base_dn=config.BASE_DN,
        bind_dn=config.BIND_DN,
        bind_password=config.BIND_PASSWORD,
    )


def cmd_add(args: argparse.Namespace) -> None:
    password = args.password or getpass.getpass("Password: ")
    attrs = {}
    if args.sn:
        attrs["sn"] = args.sn
    if args.cn:
        attrs["cn"] = args.cn
    ok = build_agent().add_user(args.uid, password, attrs)
    print("✅ User created" if ok else "❌ Failed to create user")


def cmd_get(args: argparse.Namespace) -> None:
    user = build_agent().get_user(args.uid)
    if user:
        print(user)
    else:
        print("User not found")


def cmd_delete(args: argparse.Namespace) -> None:
    ok = build_agent().delete_user(args.uid)
    print("✅ User deleted" if ok else "❌ Failed to delete user")


def cmd_set_password(args: argparse.Namespace) -> None:
    password = args.password or getpass.getpass("New password: ")
    ok = build_agent().update_user(args.uid, {"userPassword": password})
    print("✅ Password updated" if ok else "❌ Failed to update password")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage LDAP users")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add", help="Create a user")
    add_p.add_argument("uid")
    add_p.add_argument("--password")
    add_p.add_argument("--sn")
    add_p.add_argument("--cn")
    add_p.set_defaults(func=cmd_add)

    get_p = sub.add_parser("get", help="Retrieve user attributes")
    get_p.add_argument("uid")
    get_p.set_defaults(func=cmd_get)

    del_p = sub.add_parser("delete", help="Delete a user")
    del_p.add_argument("uid")
    del_p.set_defaults(func=cmd_delete)

    pw_p = sub.add_parser("set-password", help="Change a user's password")
    pw_p.add_argument("uid")
    pw_p.add_argument("--password")
    pw_p.set_defaults(func=cmd_set_password)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
