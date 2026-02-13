"""
Data models for the Budget Management Application.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date


@dataclass
class Client:
    """Client data model."""
    id: Optional[int] = None
    nom: str = ""
    raison_sociale: str = ""
    adresse: str = ""
    code_postal: str = ""
    ville: str = ""
    email: str = ""
    telephone: str = ""
    actif: bool = True


@dataclass
class Contact:
    """Contact data model."""
    id: Optional[int] = None
    client_id: Optional[int] = None
    nom: str = ""
    prenom: str = ""
    fonction: str = ""
    telephone: str = ""
    email: str = ""
    notes: str = ""


@dataclass
class Contrat:
    """Contrat data model."""
    id: Optional[int] = None
    numero_contrat: str = ""
    client_id: Optional[int] = None
    contact_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    montant: float = 0.0
    description: str = ""
    statut: str = "Actif"
    alerte_6_mois: bool = False


@dataclass
class Budget:
    """Budget data model."""
    id: Optional[int] = None
    client_id: Optional[int] = None
    annee: int = 0
    nature: str = ""
    montant_initial: float = 0.0
    montant_consomme: float = 0.0
    montant_disponible: float = 0.0
    service_demandeur: str = ""


@dataclass
class BonCommande:
    """Bon de commande data model."""
    id: Optional[int] = None
    numero_bc: str = ""
    client_id: Optional[int] = None
    contrat_id: Optional[int] = None
    nature: str = ""
    type: str = ""
    service_demandeur: str = ""
    montant: float = 0.0
    valide: bool = False
    date_validation: Optional[datetime] = None
    description: str = ""


@dataclass
class Projet:
    """Projet data model."""
    id: Optional[int] = None
    nom_projet: str = ""
    fap_redigee: bool = False
    porteur_projet: str = ""
    service_demandeur: str = ""
    contacts_pris: str = ""
    sourcing: str = ""
    clients_contactes: str = ""
    pret_materiel_logiciel: str = ""
    date_debut: Optional[date] = None
    date_fin_estimee: Optional[date] = None
    date_mise_service: Optional[date] = None
    remarques_1: str = ""
    remarques_2: str = ""
    statut: str = "En cours"


@dataclass
class InvestissementProjet:
    """Investissement projet data model."""
    id: Optional[int] = None
    projet_id: Optional[int] = None
    type: str = ""
    description: str = ""
    montant_estime: float = 0.0


@dataclass
class ContactSourcing:
    """Contact sourcing data model."""
    id: Optional[int] = None
    projet_id: Optional[int] = None
    nom: str = ""
    prenom: str = ""
    entreprise: str = ""
    telephone: str = ""
    email: str = ""
    notes: str = ""


@dataclass
class TodoItem:
    """Todo item data model."""
    id: Optional[int] = None
    motif: str = ""
    description: str = ""
    contrat_id: Optional[int] = None
    date_echeance: Optional[date] = None
    priorite: str = "Normale"
    complete: bool = False
    date_completion: Optional[datetime] = None


@dataclass
class Sauvegarde:
    """Sauvegarde data model."""
    id: Optional[int] = None
    nom_fichier: str = ""
    chemin: str = ""
    date_sauvegarde: Optional[datetime] = None
    taille_ko: float = 0.0
    commentaire: str = ""
