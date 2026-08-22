#!/usr/bin/env python3
"""Build the synthetic `.vaudtax` fixture used by the test suite.

Every value below is invented. The household is deliberately fictional
("Camille et Dominique Exemple", living at an address that does not exist).
IBANs and AVS numbers are generated so that their check digits are valid --
otherwise the validation tests could not pass -- but the account numbers
themselves are placeholders.

Keeping the fixture as a *generator* rather than an opaque binary means a
reviewer can verify at a glance that no real data is committed.

    python3 tests/build_fixture.py            # writes tests/fixtures/exemple.vaudtax
    python3 tests/build_fixture.py --stdout   # print the XML instead
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "exemple.vaudtax"
XML_NAME = "CTB99999999_PF2025_EXEMPL-FIDUC1_2026-01-15.xml"
DOC_KEY = "doc1737000000000"


def iban(country: str, bban: str) -> str:
    """Return a syntactically valid IBAN with correct mod-97 check digits."""
    rotated = bban + country + "00"
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rotated)
    check = 98 - int(digits) % 97
    return f"{country}{check:02d}{bban}"


def avs(prefix12: str) -> str:
    """Return a valid AVS/AHV number from the first 12 digits."""
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(prefix12))
    return f"{prefix12}{(10 - total % 10) % 10}"


def fmt_avs(number: str) -> str:
    return f"{number[:3]}.{number[3:7]}.{number[7:11]}.{number[11:]}"


IBAN_A = iban("CH", "00900000100000001")   # main current account
IBAN_B = iban("CH", "00900000100000002")   # savings, eReleve-imported
IBAN_C = iban("CH", "00900000100000003")   # multi-currency broker account
IBAN_D = iban("CH", "00900000100000004")   # mortgage lender

AVS_1 = fmt_avs(avs("756000000001"))
AVS_2 = fmt_avs(avs("756000000002"))
AVS_3 = fmt_avs(avs("756000000003"))

# Known-good and known-bad vectors for the checksum tests. They live here, in
# the one module allowed to contain identifier-shaped literals, so that
# scripts/check_no_pii.py keeps guarding the test files themselves -- those are
# exactly where someone debugging with a real declaration would paste one.
# The valid IBAN is the textbook Swiss example; the AVS is the standard
# documentation example. Neither belongs to anyone.
IBAN_VALID_VECTOR = "CH9300762011623852957"
IBAN_INVALID_VECTOR = "CH9300762011623852958"      # last digit altered
IBAN_TOO_SHORT_VECTOR = "CH93"
AVS_VALID_VECTOR = "756.1234.5678.97"
AVS_VALID_VECTOR_UNSEPARATED = "7561234567897"
AVS_INVALID_VECTOR = "756.1234.5678.96"            # wrong check digit
AVS_WRONG_PREFIX_VECTOR = "123.4567.8901.23"
AVS_TRUNCATED_VECTOR = "756.1234.5678"


def build_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<vaudTaxData xmlns="http://www.vd.ch/fiscalite/vaudtax">
    <fiscalPeriod>2025</fiscalPeriod>
    <identification>
        <communeFiscale>
            <nomOfficiel>Commune-Exemple</nomOfficiel>
            <numeroOfs>9999</numeroOfs>
            <sigleCanton>VD</sigleCanton>
        </communeFiscale>
        <etatCivil>MARIE</etatCivil>
    </identification>
    <taxpayerPersonalData1>
        <lastName>Exemple</lastName>
        <firstName>Camille</firstName>
        <avs>{AVS_1}</avs>
        <birthDate>1985-04-12</birthDate>
        <civility>2</civility>
        <profession>Profession-Exemple</profession>
    </taxpayerPersonalData1>
    <taxpayerPersonalData2>
        <lastName>Exemple</lastName>
        <firstName>Dominique</firstName>
        <avs>{AVS_2}</avs>
        <birthDate>1987-09-30</birthDate>
        <civility>1</civility>
        <profession>Profession-Exemple</profession>
    </taxpayerPersonalData2>
    <enfants>
        <trackingIndex>1</trackingIndex>
        <lastName>Exemple</lastName>
        <firstName>Alix</firstName>
        <avs>{AVS_3}</avs>
        <birthDate>2018-02-20</birthDate>
        <activite>AUTRE</activite>
        <menageCommunAvecEnfant>true</menageCommunAvecEnfant>
        <enfACharge>true</enfACharge>
        <enfFraisGarde>4800</enfFraisGarde>
    </enfants>
    <activiteSalarieeRevenus>
        <trackingIndex>1</trackingIndex>
        <employeur>Employeur Exemple SA</employeur>
        <type>PRINCIPAL</type>
        <tauxActivite>100</tauxActivite>
        <dateDebut>2025-01-01</dateDebut>
        <dateFin>2025-12-31</dateFin>
        <salaireNet>95000</salaireNet>
        <cotisationOrdinaire>6200</cotisationOrdinaire>
        <transportGratuit>false</transportGratuit>
        <contributionFraisRepas>false</contributionFraisRepas>
        <isContribuable1>true</isContribuable1>
    </activiteSalarieeRevenus>
    <activiteSalarieeRevenus>
        <trackingIndex>2</trackingIndex>
        <employeur>Autre Employeur Exemple</employeur>
        <type>PRINCIPAL</type>
        <tauxActivite>60</tauxActivite>
        <dateDebut>2025-01-01</dateDebut>
        <dateFin>2025-12-31</dateFin>
        <salaireNet>52000</salaireNet>
        <cotisationOrdinaire>3100</cotisationOrdinaire>
        <isContribuable1>false</isContribuable1>
    </activiteSalarieeRevenus>
    <fraisRepas>
        <trackingIndex>1</trackingIndex>
        <noLigne>1</noLigne>
        <fraisRepasType>HORS_DOMICILE_NORMAL</fraisRepasType>
        <nbJours>240</nbJours>
        <isContribuable1>true</isContribuable1>
    </fraisRepas>
    <fraisTransport>
        <trackingIndex>1</trackingIndex>
        <noLigne>1</noLigne>
        <moyenTransport>TRANSPORT_PUBLIC</moyenTransport>
        <domicile>Commune-Exemple</domicile>
        <lieuTravail>Autre-Commune-Exemple</lieuTravail>
        <nbJours>240</nbJours>
        <isForfait>true</isForfait>
    </fraisTransport>
    <primesEtCotisationsAssurance>
        <montantPrimesBrutes>11400</montantPrimesBrutes>
        <montantSubsides>0</montantSubsides>
        <formesReconnuesPrevoyanceIndividuelleContribuable1>7258</formesReconnuesPrevoyanceIndividuelleContribuable1>
        <formesReconnuesPrevoyanceIndividuelleContribuable2>3000</formesReconnuesPrevoyanceIndividuelleContribuable2>
    </primesEtCotisationsAssurance>
    <etatTitres>
        <trackingIndex>1</trackingIndex>
        <contribuable>CTB1_CTB2</contribuable>
        <etablissement>Banque Exemple</etablissement>
        <iban>{IBAN_A}</iban>
        <numCompte>10-000000-1</numCompte>
        <devise>
            <id>1</id>
            <label>CHF</label>
            <coefficient>1.000000</coefficient>
        </devise>
        <soldeCompteCHF>18450</soldeCompteCHF>
        <rendementNonSoumisIA>12.35</rendementNonSoumisIA>
        <rendementType>OUI_NON_SOUMIS_IA</rendementType>
    </etatTitres>
    <etatTitres>
        <trackingIndex>2</trackingIndex>
        <contribuable>CTB1</contribuable>
        <etablissement>Banque Exemple</etablissement>
        <iban>{IBAN_B}</iban>
        <numCompte>10-000000-2</numCompte>
        <devise>
            <id>1</id>
            <label>CHF</label>
            <coefficient>1.000000</coefficient>
        </devise>
        <soldeCompteCHF>32000</soldeCompteCHF>
        <rendementNonSoumisIA>41.10</rendementNonSoumisIA>
        <rendementType>OUI_NON_SOUMIS_IA</rendementType>
        <nomEreleve>exemple_2026-01-07_E960_00000.pdf</nomEreleve>
        <identifiantEReleve>CH00900000100000002_20251231</identifiantEReleve>
    </etatTitres>
    <etatTitres>
        <trackingIndex>3</trackingIndex>
        <contribuable>CTB1</contribuable>
        <etablissement>Courtier Exemple</etablissement>
        <iban>{IBAN_C}</iban>
        <numCompte>90-000000-3</numCompte>
        <devise>
            <id>1</id>
            <label>CHF</label>
            <coefficient>1.000000</coefficient>
        </devise>
        <soldeCompteCHF>5200</soldeCompteCHF>
        <rendementType>NON</rendementType>
    </etatTitres>
    <etatTitres>
        <trackingIndex>4</trackingIndex>
        <contribuable>CTB1</contribuable>
        <etablissement>Courtier Exemple</etablissement>
        <iban>{IBAN_C}</iban>
        <numCompte>90-000000-3</numCompte>
        <devise>
            <id>3</id>
            <label>USD</label>
            <coefficient>0.880000</coefficient>
        </devise>
        <soldeCompteDevise>4000</soldeCompteDevise>
        <coursMonetaire>0.880000</coursMonetaire>
        <soldeCompteCHF>3520</soldeCompteCHF>
        <rendementType>NON</rendementType>
    </etatTitres>
    <fraisAdministrationTitres>
        <fraisEffectif>85</fraisEffectif>
    </fraisAdministrationTitres>
    <actionPartSociale>
        <trackingIndex>1</trackingIndex>
        <designation>Societe Exemple SA</designation>
        <numeroValeur>0</numeroValeur>
        <country>
            <iso2Id>US</iso2Id>
        </country>
        <typeImpotSoumis>AUCUN</typeImpotSoumis>
        <valeurNominaleInitiale>1000</valeurNominaleInitiale>
        <infosImpotNational>
            <valeurNominaleFinale>1200</valeurNominaleFinale>
            <coursFiscalFinal>4.50</coursFiscalFinal>
            <valeurFiscaleFinale>5400</valeurFiscaleFinale>
        </infosImpotNational>
    </actionPartSociale>
    <relevesFiscauxBancaires>
        <trackingIndex>1</trackingIndex>
        <designation>Courtier Exemple — relevé fiscal</designation>
        <numeroCompte>90-000000-3</numeroCompte>
        <revenusBrutsNonSoumisIA>210.40</revenusBrutsNonSoumisIA>
        <valeurFiscaleFinaleNonSoumisIA>8720</valeurFiscaleFinaleNonSoumisIA>
    </relevesFiscauxBancaires>
    <biensImmobiliers>
        <trackingIndex>1</trackingIndex>
        <contribuable>CTB1_CTB2</contribuable>
        <partProprieteCtb1>50.00</partProprieteCtb1>
        <partProprieteCtb2>50.00</partProprieteCtb2>
        <communeFiscale>
            <nomOfficiel>Commune-Immeuble-Exemple</nomOfficiel>
            <numeroOfs>8888</numeroOfs>
            <sigleCanton>VD</sigleCanton>
        </communeFiscale>
        <numParcelle>1234</numParcelle>
        <batimentExiste>true</batimentExiste>
        <anneeConstruction>1990</anneeConstruction>
        <estimationFiscale>320000</estimationFiscale>
        <typeImmeublePrivate>true</typeImmeublePrivate>
        <typeLogementPrincipal>false</typeLogementPrincipal>
        <interetsPassifsImmeuble>4200</interetsPassifsImmeuble>
        <detteImmeuble>280000</detteImmeuble>
        <isImmeubleOccupeSuisse>false</isImmeubleOccupeSuisse>
        <surfaceHabitable>95</surfaceHabitable>
        <isAutresRendementsImmobiliers>true</isAutresRendementsImmobiliers>
        <autresRendementsImmobiliers>9600</autresRendementsImmobiliers>
        <taxesPrimesImpots>
            <primesAssuranceDM>180</primesAssuranceDM>
            <primesAssuranceRC>90</primesAssuranceRC>
            <taxesOrdures>140</taxesOrdures>
        </taxesPrimesImpots>
        <fraisEntretienImmeuble>
            <trackingIndex>1</trackingIndex>
            <dateFacture>2025-06-14</dateFacture>
            <maitreEtat>Entreprise Exemple Sarl</maitreEtat>
            <montant>1850</montant>
            <plusValue>false</plusValue>
        </fraisEntretienImmeuble>
    </biensImmobiliers>
    <interetsDettes>
        <trackingIndex>1</trackingIndex>
        <contribuable>CTB1_CTB2</contribuable>
        <isGageImmobGarantie>true</isGageImmobGarantie>
        <creancier>Banque Exemple</creancier>
        <iban>{IBAN_D}</iban>
        <numCompte>20-000000-4</numCompte>
        <interets>4200</interets>
        <detteMontant>280000</detteMontant>
    </interetsDettes>
    <fraisMedicaux>
        <trackingIndex>1</trackingIndex>
        <etabliPar>Cabinet Exemple</etabliPar>
        <datePaiement>2025-03-08</datePaiement>
        <type>MEDECIN</type>
        <montantBrut>420</montantBrut>
        <montantACharge>310</montantACharge>
    </fraisMedicaux>
    <acomptes>
        <acomptesPayes>18000.00</acomptesPayes>
    </acomptes>
    <objetsMobiliers>
        <isInitialized>false</isInitialized>
    </objetsMobiliers>
    <piecesJustificativesObligatoires>
        <id>1</id>
        <titleLabelKey>pieces.obligatoires</titleLabelKey>
        <isRequired>true</isRequired>
        <piecesJustificatives>
            <id>11</id>
            <labelKey>pieces.certificat.salaire</labelKey>
            <canBeDeleted>true</canBeDeleted>
            <documents>
                <reference>00000000-0000-0000-0000-000000000001</reference>
                <filename>certificat_exemple.pdf</filename>
                <label>Certificat de salaire (exemple)</label>
                <key>{DOC_KEY}</key>
                <mimeType>application/pdf</mimeType>
                <fileSize>24</fileSize>
            </documents>
        </piecesJustificatives>
    </piecesJustificativesObligatoires>
    <userProfil>
        <menuPrefs>
            <menuId>revenus</menuId>
            <expanded>true</expanded>
        </menuPrefs>
    </userProfil>
    <guidedNav>
        <displayedSubForms>
            <etatTitres>true</etatTitres>
            <immeubles>true</immeubles>
            <enfants>true</enfants>
            <fraisMedicaux>true</fraisMedicaux>
        </displayedSubForms>
    </guidedNav>
</vaudTaxData>
"""


def build(path: Path = FIXTURE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(XML_NAME, build_xml())
        zf.writestr(DOC_KEY, b"%PDF-1.4 fictitious placeholder\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    if args.stdout:
        print(build_xml(), end="")
    else:
        print(f"écrit : {build()}")


if __name__ == "__main__":
    main()
