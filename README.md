---
# The Repository is ARCHIVED!
### it is now maintained in https://github.com/ai4os-hub/litter-assessment
---

# litter_assessment_service
[![Build Status](https://jenkins.indigo-datacloud.eu/buildStatus/icon?job=Pipeline-as-code/DEEP-OC-org/UC-cleluschko-litter_assessment_service/master)](https://jenkins.indigo-datacloud.eu/job/Pipeline-as-code/job/DEEP-OC-org/job/UC-cleluschko-litter_assessment_service/job/master)

Integration of DeepaaS API and litter assessment software

To launch it, first install the package then run [deepaas](https://github.com/indigo-dc/DEEPaaS):
```bash
git clone https://github.com/DFKI-NI/litter_assessment_service
cd litter_assessment_service
pip install -e .
deepaas-run --listen-ip 0.0.0.0
```
The associated Docker container for this module can be found in https://github.com/DFKI-NI/DEEP-OC-litter_assessment_service.

## Project structure
```
├── LICENSE                <- License file
│
├── README.md              <- The top-level README for developers using this project.
│
├── requirements.txt       <- The requirements file for reproducing the analysis environment, e.g.
│                             generated with `pip freeze > requirements.txt`
│
├── setup.py, setup.cfg    <- makes project pip installable (pip install -e .) so
│                             litter_assessment_service can be imported
│
├── litter_assessment_service    <- Source code for use in this project.
│   │
│   ├── __init__.py        <- Makes litter_assessment_service a Python module
│   │
│   └── api.py             <- Main script for the integration with DEEP API
│
└── Jenkinsfile            <- Describes basic Jenkins CI/CD pipeline
```
