"""LDAP agent for SONiC user authentication.

This module provides a simple wrapper around ldap3 to authenticate
users against an LDAP server.  It can be used by other SONiC services
that need to validate credentials.
"""

from typing import Dict, Optional

from ldap3 import ALL, Connection, MODIFY_REPLACE, Server
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError


class LDAPAgent:
    """Simple LDAP authentication agent with basic CRUD helpers."""

    def __init__(
        self,
        host: str,
        port: int = 389,
        base_dn: Optional[str] = None,
        bind_dn: Optional[str] = None,
        bind_password: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.server = Server(self.host, port=self.port, get_info=ALL)

    # ------------------------------------------------------------------
    # Authentication helpers

    def authenticate(self, user_dn: str, password: str) -> bool:
        """Return True if the provided DN and password are valid."""
        try:
            conn = Connection(self.server, user=user_dn, password=password, auto_bind=True)
            conn.unbind()
            return True
        except LDAPBindError:
            return False
        except LDAPSocketOpenError:
            # Unable to reach LDAP server
            return False

    def authenticate_user(self, uid: str, password: str) -> bool:
        """Authenticate using a uid under the configured base_dn.

        The `base_dn` must be provided when constructing the agent for this
        method to work.
        """
        if not self.base_dn:
            raise ValueError("base_dn not set; cannot build user DN")

        user_dn = f"uid={uid},{self.base_dn}"
        return self.authenticate(user_dn, password)

    # ------------------------------------------------------------------
    # CRUD helpers

    def _admin_conn(self) -> Connection:
        """Return a bound connection using configured bind credentials."""
        if not (self.bind_dn and self.bind_password):
            raise ValueError("bind_dn and bind_password required for write operations")

        return Connection(
            self.server, user=self.bind_dn, password=self.bind_password, auto_bind=True
        )

    def add_user(self, uid: str, password: str, attributes: Optional[Dict[str, str]] = None) -> bool:
        """Create a simple user entry under base_dn."""
        if not self.base_dn:
            raise ValueError("base_dn not set; cannot build user DN")

        user_dn = f"uid={uid},{self.base_dn}"
        attrs: Dict[str, str] = {
            "objectClass": ["inetOrgPerson"],
            "sn": uid,
            "cn": uid,
            "userPassword": password,
        }
        if attributes:
            attrs.update(attributes)

        with self._admin_conn() as conn:
            conn.add(user_dn, attributes=attrs)
            return conn.result.get("description") == "success"

    def get_user(self, uid: str) -> Optional[Dict[str, str]]:
        """Return user attributes or None if not found."""
        if not self.base_dn:
            raise ValueError("base_dn not set; cannot search")

        with self._admin_conn() as conn:
            conn.search(
                search_base=self.base_dn,
                search_filter=f"(uid={uid})",
                attributes=ALL,
            )
            if not conn.entries:
                return None
            return conn.entries[0].entry_attributes_as_dict

    def update_user(self, uid: str, attributes: Dict[str, str]) -> bool:
        """Modify provided attributes of a user."""
        if not self.base_dn:
            raise ValueError("base_dn not set; cannot build user DN")

        user_dn = f"uid={uid},{self.base_dn}"
        changes = {attr: [(MODIFY_REPLACE, [value])] for attr, value in attributes.items()}
        with self._admin_conn() as conn:
            conn.modify(user_dn, changes)
            return conn.result.get("description") == "success"

    def delete_user(self, uid: str) -> bool:
        """Remove a user entry."""
        if not self.base_dn:
            raise ValueError("base_dn not set; cannot build user DN")

        user_dn = f"uid={uid},{self.base_dn}"
        with self._admin_conn() as conn:
            conn.delete(user_dn)
            return conn.result.get("description") == "success"


__all__ = ["LDAPAgent"]
