"""
StatisFLOW Domain-Specific Modules
Agriculture, Biology/Ecology, Social Sciences, Epidemiology
"""

from .agri_tech import AgriTechSuite
from .bio_ecology import BioEcologyToolkit
from .social_science import SocialScienceLab
from .epidemiology import EpidemiologyModule

__all__ = [
    "AgriTechSuite",
    "BioEcologyToolkit",
    "SocialScienceLab",
    "EpidemiologyModule"
]
