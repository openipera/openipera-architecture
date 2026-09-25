# SMV: DENIED

{
  "status": "DENIED",
  "model_valid": true,
  "model_agreement": "DISCREPANCIES",
  "policy": {
    "block_on": [
      "UNMODELED"
    ]
  },
  "findings": [
    {
      "source": "boot",
      "target": "vm",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "cmdb",
      "target": "register-ci",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "compute",
      "target": "cpu",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "compute",
      "target": "memory",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "compute",
      "target": "vm",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "cyberark",
      "target": "domain",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "domain",
      "target": "validate",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "gpc",
      "target": "allocate-ip",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "boot",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "cmdb",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "compute",
      "status": "CORROBORATED",
      "sm_dag": true,
      "lc": true
    },
    {
      "source": "gpc",
      "target": "cpu",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "cyberark",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "domain",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "identity",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "memory",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "network",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "register-ci",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "register-dns",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "security",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "storage",
      "status": "CORROBORATED",
      "sm_dag": true,
      "lc": true
    },
    {
      "source": "gpc",
      "target": "validate",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "gpc",
      "target": "vm",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "identity",
      "target": "domain",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "network",
      "target": "allocate-ip",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "network",
      "target": "register-dns",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "register-ci",
      "target": "validate",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "register-dns",
      "target": "allocate-ip",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "security",
      "target": "cyberark",
      "status": "UNCORROBORATED",
      "sm_dag": true,
      "lc": false
    },
    {
      "source": "validate",
      "target": "boot",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "vm",
      "target": "cpu",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "vm",
      "target": "memory",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "vm",
      "target": "network",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    },
    {
      "source": "vm",
      "target": "storage",
      "status": "UNMODELED",
      "sm_dag": false,
      "lc": true
    }
  ],
  "diagnostics": [
    {
      "code": "POLICY_BLOCK",
      "message": "Compilation blocked by configured finding class",
      "blocked_findings": [
        {
          "source": "boot",
          "target": "vm",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "cyberark",
          "target": "domain",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "domain",
          "target": "validate",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "register-ci",
          "target": "validate",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "register-dns",
          "target": "allocate-ip",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "validate",
          "target": "boot",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "vm",
          "target": "cpu",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "vm",
          "target": "memory",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "vm",
          "target": "network",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        },
        {
          "source": "vm",
          "target": "storage",
          "status": "UNMODELED",
          "sm_dag": false,
          "lc": true
        }
      ]
    }
  ]
}
