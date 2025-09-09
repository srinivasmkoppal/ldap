# LDAP Agent for SONiC

This repository provides a minimal LDAP agent that can be used by SONiC to
authenticate users against an external LDAP server.

## Usage

1. Ensure the `ldap3` package is installed:

   ```bash
   pip install ldap3
   ```

2. Adjust the values in `config.py` to match your environment.

### Authentication

Run the CLI to test authentication:

```bash
python main.py
```

Enter a username and password when prompted.

### Managing Users

`manage_user.py` exposes a few basic CRUD helpers.  Example:

```bash
# create a user
python manage_user.py add alice --sn Alice --cn "Alice Example"

# change password
python manage_user.py set-password alice

# fetch attributes
python manage_user.py get alice

# delete
python manage_user.py delete alice
```

The `LDAPAgent` class in `ldap_agent.py` can be imported by other SONiC
components to programmatically authenticate or manage users.
